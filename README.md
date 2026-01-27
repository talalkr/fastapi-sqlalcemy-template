# App

## Run Project

### Using Docker
```bash
docker compose up -d
```

### Without Docker
```bash
export $(cat vars/*.env | grep -v '^#' | xargs)
uvicorn app.main:app --reload --host 0.0.0.0
```

## Development

Virtualenv will be created under the root folder and managed by poetry

Install Dependencies
```bash
poetry config --local virtualenvs.in-project true
poetry env use python3.14
```
