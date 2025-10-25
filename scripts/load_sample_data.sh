#!/usr/bin/env bash
set -e

echo "=== Pool Recommender | Load Sample Data to MinIO ==="

# 1️⃣ Ensure sample_data folder exists
mkdir -p sample_data

# 2️⃣ Create a simple CSV file with 10 records
cat > sample_data/pools.csv <<'EOF'
name,size
Pool A,10
Pool B,12
Pool C,8
Pool D,15
Pool E,20
Pool F,7
Pool G,9
Pool H,14
Pool I,11
Pool J,13
EOF

echo "Sample CSV created at sample_data/pools.csv"

# 3️⃣ Wait until MinIO is reachable
echo "Checking if MinIO is ready..."
until curl -s http://localhost:9000/minio/health/live >/dev/null; do
  echo "  Waiting for MinIO..."
  sleep 3
done
echo "MinIO is ready!"

# 4️⃣ Upload CSV to MinIO
echo "Uploading CSV to MinIO..."
docker-compose exec -T minio mc alias set local http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}
docker-compose exec -T minio mc mb -p local/pool-data || true
docker-compose exec -T minio mc cp /code/sample_data/pools.csv local/pool-data/

echo "✅ Sample CSV uploaded to MinIO bucket 'pool-data'."
echo "You can verify in the MinIO console at http://localhost:9001"
