#!/usr/bin/env bash

# Navigate to your repo folder (replace path if needed)
cd ~/path/to/pool-recommender

# Create directories
mkdir -p app scripts .github/workflows

# ---------------------
# Create README.md
cat > README.md <<'EOF'
# 🏊‍♂️ Pool Recommender

The Pool Recommender project suggests optimal pools for users.

See architecture.md for the system overview.
EOF

# ---------------------
# Create CONTRIBUTING.md
cat > CONTRIBUTING.md <<'EOF'
# Contributing
Use feature/* branches, open PRs, and follow conventional commits.
EOF

# ---------------------
# Create SECURITY.md
cat > SECURITY.md <<'EOF'
# Security Policy
Report vulnerabilities privately to security@poolrecommender.org
EOF

# ---------------------
# Create architecture.md
cat > architecture.md <<'EOF'
# Architecture
High-level diagram and component list placeholder
EOF

# ---------------------
# Create Makefile
cat > Makefile <<'EOF'
.PHONY: up down reset-db

up:
	@echo "Starting local environment (stub)"

down:
	@echo "Stopping local environment (stub)"

reset-db:
	@echo "Resetting database (stub)"
EOF

# ---------------------
# Create .gitignore
cat > .gitignore <<'EOF'
__pycache__/
*.pyc
node_modules/
.env
.DS_Store
docker-data/
EOF

# ---------------------
# Create .editorconfig
cat > .editorconfig <<'EOF'
root = true
[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
EOF

# ---------------------
# Create docker-compose.yml
cat > docker-compose.yml <<'EOF'
version: '3.9'
services:
  api:
    build: .
    container_name: pool-recommender-api
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/code
    ports:
      - "8000:8000"
  db:
    image: postgres:14
    container_name: pool-recommender-db
    environment:
      POSTGRES_USER: pooluser
      POSTGRES_PASSWORD: poolpass
      POSTGRES_DB: pooldb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
EOF

# ---------------------
# Create app/main.py
cat > app/main.py <<'EOF'
from fastapi import FastAPI
app = FastAPI(title="Pool Recommender API")

@app.get("/")
def read_root():
    return {"message": "🏊‍♂️ Pool Recommender API is running!"}
EOF

# ---------------------
# Create scripts placeholders
cat > scripts/start_local.sh <<'EOF'
#!/usr/bin/env bash
echo "[stub] docker-compose up -d"
EOF

cat > scripts/stop_local.sh <<'EOF'
#!/usr/bin/env bash
echo "[stub] docker-compose down"
EOF

cat > scripts/reset_db.sh <<'EOF'
#!/usr/bin/env bash
echo "[stub] reset database"
EOF

# ---------------------
# Create requirements.txt
cat > requirements.txt <<'EOF'
fastapi
uvicorn[standard]
EOF

# ---------------------
# Create .env.example
cat > .env.example <<'EOF'
DATABASE_URL=postgresql://pooluser:poolpass@db:5432/pooldb
DEBUG=true
EOF

# ---------------------
# Create GitHub workflow placeholders
cat > .github/workflows/ci.yml <<'EOF'
name: CI
on: [pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
EOF

cat > .github/workflows/protect-branch.yml <<'EOF'
name: Branch Protection Check
on: [pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: Verify PR
        run: echo "Check branch protection rules (stub)"
EOF

echo "✅ Pool Recommender skeleton created!"
