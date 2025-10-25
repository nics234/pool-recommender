import os
import json
import time
import glob
import requests
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import year, month, to_date, col
import boto3
from botocore.client import Config

# --- Load environment variables ---
load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "weather-data")

NYC_POOLS_URL = "https://data.cityofnewyork.us/resource/82jf-bykm.json?$limit=100000"

# --- Initialize Spark ---
spark = SparkSession.builder.appName("NYCPoolsToMinIO").getOrCreate()

# --- Fetch NYC pool attendance data ---
resp = requests.get(NYC_POOLS_URL)
if resp.status_code != 200:
    raise Exception(f"Failed to fetch NYC pool data: {resp.status_code} - {resp.text}")

data = resp.json()
print(f"Fetched {len(data)} records from NYC pool attendance")

if data:
    # --- Convert to Spark DataFrame ---
    df = spark.read.json(spark.sparkContext.parallelize([json.dumps(d) for d in data]))

    # --- Detect and normalize date column ---
    date_col = None
    for candidate in ["date", "observationdate", "observation_date"]:
        if candidate in df.columns:
            date_col = candidate
            break

    if date_col:
        df = df.withColumn("parsed_date", to_date(col(date_col)))
        df = df.withColumn("year", year("parsed_date")).withColumn("month", month("parsed_date"))
        partition_cols = ["year", "month"]
    else:
        print("⚠️ No date column found — saving without partitions.")
        partition_cols = []

    # --- Save locally as partitioned Parquet ---
    local_parquet_dir = "/tmp/pool_attendance_parquet"
    if partition_cols:
        df.write.mode("overwrite").partitionBy(*partition_cols).parquet(local_parquet_dir)
    else:
        df.write.mode("overwrite").parquet(local_parquet_dir)

    print(f"Saved local Parquet files to {local_parquet_dir}")

    # --- Upload recursively to MinIO ---
    s3_client = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4")
    )

    # Ensure bucket exists
    try:
        s3_client.head_bucket(Bucket=MINIO_BUCKET)
    except:
        s3_client.create_bucket(Bucket=MINIO_BUCKET)
        print(f"Created bucket: {MINIO_BUCKET}")

    for file_path in glob.glob(f"{local_parquet_dir}/**/*", recursive=True):
        if os.path.isfile(file_path):
            key = os.path.relpath(file_path, local_parquet_dir)
            s3_client.upload_file(file_path, MINIO_BUCKET, f"pool_attendance_parquet/{key}")

    print(f"✅ Uploaded NYC pool attendance data to MinIO bucket '{MINIO_BUCKET}' successfully.")

else:
    print("No records fetched from NYC pool attendance.")

spark.stop()
