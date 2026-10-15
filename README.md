# EAEU_projects_hub
This repository is devoted to construction of the DB, that is full of joint projects of the Eurasian Economic Union

## Installation
### Docker
1. Copy .env.example to your repository
```
# 1. Get Backend path
cd Backend

# 2. Copy .env.example to .env
cp .env.example .env
```
2. Create vector extension in PostgreSQL in Query Tool
```
CREATE EXTENSION IF NOT EXISTS vector;
```
3. Launch Docker container
```
# 3. Give permission to /volume directory
sudo chmod -R 777 {PATH_TO_FILE}/volume

# 4. Build Docker container
docker compose build

# 5. Pick up the container
docker compose up
```
4. Pull LLM in Ollama
```
# 6. Pull language model (initially llama3.2:latest)
docker exec -it ollama_eaeu ollama pull llama3.2:latest
```