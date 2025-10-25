FROM openjdk:17-jdk-slim

WORKDIR /code
COPY . /code

# Install Python + dependencies
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev curl && \
    pip3 install pyspark==3.5.2 boto3 requests python-dotenv pandas pyarrow

# Download Hadoop AWS & AWS SDK JARs for S3A
RUN mkdir -p /opt/spark/jars && \
    curl -L -o /opt/spark/jars/hadoop-aws-3.3.5.jar https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.5/hadoop-aws-3.3.5.jar && \
    curl -L -o /opt/spark/jars/aws-java-sdk-bundle-1.12.503.jar https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.503/aws-java-sdk-bundle-1.12.503.jar

# Add wait-for-it.sh to ensure MinIO is ready
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Run fetch script after MinIO is ready
CMD ["/wait-for-it.sh", "minio:9000", "--", "python3", "scripts/fetch_noaa_to_minio_parquet.py"]
