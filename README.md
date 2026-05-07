# aiweaviate

A project created with FastAPI CLI.

## Quick Start

### Configure OpenAI

Set an OpenAI API key before using upload or search endpoints:

```bash
export OPENAI_API_KEY="your-api-key"
```

The default embedding model is `text-embedding-3-large` with 3072 dimensions. Override it with:

```bash
export OPENAI_EMBEDDING_MODEL="text-embedding-3-large"
```

### Start Weaviate

```bash
docker compose up -d
```

### Start the development server

```bash
uv run fastapi dev
```

Visit http://localhost:8000/docs for Swagger UI.

## MVP API Flow

- `POST /upload/text` accepts text, embeds chunks with OpenAI, and stores vectors in Weaviate.
- `POST /upload/pdf` accepts a PDF upload, extracts text, embeds chunks with OpenAI, and stores vectors in Weaviate.
- `POST /search` accepts a human question, embeds it with the same model, and returns semantic matches from Weaviate.
- `POST /search/hybrid` combines keyword search and vector search. Use `alpha` from `0` to `1` to tune keyword vs vector weight.
- `GET /documents` lists stored chunks.
- On startup, an empty `Doc` collection is seeded with three 3072-dimensional sample vectors.
- `DELETE /documents/{doc_id}` deletes one stored chunk by UUID.
- `DELETE /documents?source=...` deletes all chunks for an uploaded source.
- `GET /health` checks app and Weaviate readiness.

### Deploy to FastAPI Cloud

> FastAPI Cloud is currently in private beta. Join the waitlist at https://fastapicloud.com

```bash
uv run fastapi deploy
```

## Project Structure

- `main.py` - Your FastAPI application
- `pyproject.toml` - Project dependencies

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [FastAPI Cloud](https://fastapicloud.com)
