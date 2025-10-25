import os
import json
import time
import glob
import requests
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import year, month
import boto3
from botocore.client import Config

# --- Load environment variables ---
load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "weather-data")

NOAA_TOKEN = "ZIdIYtrgVzbXMmyVmsdjeHWvlNyyeOGm"
NOAA_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"

STATION_ID = "GHCND:USW00094728"
DATATYPES = ["TMAX", "TMIN", "PRCP", "SNOW", "AWND"]
YEARS = [2022, 2023, 2024, 2025]
LIMIT = 1000

# --- Initialize Spark ---
spark = SparkSession.builder.appName("NOAAToMinIO").getOrCreate()

all_records = []

# --- Fetch helper with retries ---
def fetch_with_retries(url, headers, params, max_retries=5, backoff_factor=2):
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code == 200:
            return resp
        elif resp.status_code == 503:
            wait = backoff_factor ** attempt
            print(f"503 error, retrying in {wait} seconds...")
            time.sleep(wait)
        else:
            print(f"Error {resp.status_code}: {resp.text[:200]}")
            time.sleep(2)
    raise Exception("Max retries exceeded.")

# --- Fetch NOAA data ---
for year_val in YEARS:
    startdate = f"{year_val}-01-01"
    enddate = f"{year_val}-12-31"
    offset = 1
    while True:
        params = {
            "datasetid": "GHCND",
            "stationid": STATION_ID,
            "startdate": startdate,
            "enddate": enddate,
            "datatypeid": DATATYPES,
            "units": "metric",
            "limit": LIMIT,
            "offset": offset
        }
        resp = fetch_with_retries(NOAA_URL, {"token": NOAA_TOKEN}, params)
        data = resp.json().get("results", [])
        if not data:
            break
        all_records.extend(data)
        print(f"Fetched {len(data)} records, total so far: {len(all_records)}")
        offset += len(data)
        time.sleep(1)

if all_records:
    # --- Convert to Spark DataFrame ---
    df = spark.read.json(spark.sparkContext.parallelize([json.dumps(r) for r in all_records]))
    df = df.withColumn("year", year("date")).withColumn("month", month("date"))

    # --- Save locally as partitioned Parquet ---
    local_parquet_dir = "/tmp/noaa_parquet"
    df.write.mode("overwrite").partitionBy("year", "month").parquet(local_parquet_dir)
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
            s3_client.upload_file(file_path, MINIO_BUCKET, f"noaa_parquet/{key}")

    print(f"Uploaded NOAA data to MinIO bucket '{MINIO_BUCKET}' successfully.")

else:
    print("No records fetched from NOAA API.")

spark.stop()
