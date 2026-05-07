from contextlib import asynccontextmanager
from io import BytesIO
import os
import uuid

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import APIStatusError, OpenAI, OpenAIError
from pydantic import BaseModel, Field
from pypdf import PdfReader
from weaviate.classes.query import Filter, MetadataQuery

from wv.core.wvclient import get_client
from wv.schema.wvschema import create_schema


COLLECTION = "Doc"
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
EXPECTED_VECTOR_DIM = 3072
DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 150
SAMPLE_SOURCE = "__dimension_seed__"
SAMPLE_DOCS = [
    "Sample seed document for biomedical artificial intelligence retrieval.",
    "Sample seed document for PDF and text ingestion into Weaviate.",
    "Sample seed document for semantic search over embedded chunks.",
]

weaviate_client = None
openai_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global weaviate_client

    weaviate_client = get_client()
    create_schema(weaviate_client)
    seed_collection_if_empty()

    yield

    if weaviate_client is not None:
        weaviate_client.close()


app = FastAPI(
    title="AI Weaviate RAG MVP",
    description="Upload text/PDF content, embed with OpenAI, store in Weaviate, and run semantic search.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextUploadIn(BaseModel):
    text: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    chunk_size: int = Field(DEFAULT_CHUNK_SIZE, ge=200, le=8000)
    chunk_overlap: int = Field(DEFAULT_CHUNK_OVERLAP, ge=0, le=2000)


class SearchIn(BaseModel):
    question: str = Field(..., min_length=1)
    limit: int = Field(5, ge=1, le=25)


def get_collection():
    if weaviate_client is None:
        raise HTTPException(status_code=503, detail="Weaviate client is not ready")

    return weaviate_client.collections.get(COLLECTION)


def get_openai_client() -> OpenAI:
    global openai_client

    if openai_client is None:
        try:
            openai_client = OpenAI()
        except OpenAIError as exc:
            raise HTTPException(
                status_code=500,
                detail="OpenAI client is not configured. Set OPENAI_API_KEY.",
            ) from exc

    return openai_client


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    try:
        response = get_openai_client().embeddings.create(
            input=[text.replace("\n", " ") for text in texts],
            model=EMBEDDING_MODEL,
        )
    except APIStatusError as exc:
        raise HTTPException(status_code=exc.status_code, detail=f"OpenAI embedding failed: {exc}") from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI embedding failed: {exc}") from exc

    embeddings = [item.embedding for item in response.data]
    for vector in embeddings:
        validate_vector(vector)

    return embeddings


def validate_vector(vector: list[float]):
    if len(vector) != EXPECTED_VECTOR_DIM:
        raise HTTPException(
            status_code=400,
            detail=f"Expected vector dimension {EXPECTED_VECTOR_DIM}, got {len(vector)}",
        )


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []

    if chunk_overlap >= chunk_size:
        raise HTTPException(status_code=400, detail="chunk_overlap must be smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunks.append(normalized[start:end])

        if end == len(normalized):
            break

        start = end - chunk_overlap

    return chunks


def extract_pdf_text(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read PDF: {exc}") from exc

    text = "\n".join(pages).strip()
    if not text:
        raise HTTPException(status_code=400, detail="PDF did not contain extractable text")

    return text


def save_chunks(source: str, chunks: list[str]) -> dict:
    if not chunks:
        raise HTTPException(status_code=400, detail="No text content found to upload")

    embeddings = embed_texts(chunks)
    collection = get_collection()
    uploaded_ids = []

    for index, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        object_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source}:{index}:{chunk}"))

        collection.data.delete_by_id(object_id)
        collection.data.insert(
            uuid=object_id,
            properties={
                "text": chunk,
                "source": source,
                "chunk_index": index,
            },
            vector=vector,
        )
        uploaded_ids.append(object_id)

    return {
        "status": "ok",
        "source": source,
        "chunks": len(chunks),
        "ids": uploaded_ids,
        "embedding_model": EMBEDDING_MODEL,
        "vector_dimension": EXPECTED_VECTOR_DIM,
    }


def sample_vector(seed: int) -> list[float]:
    vector = [0.0] * EXPECTED_VECTOR_DIM
    vector[seed] = 1.0
    return vector


def seed_collection_if_empty():
    collection = get_collection()
    existing = collection.query.fetch_objects(limit=1)
    if existing.objects:
        return

    for index, text in enumerate(SAMPLE_DOCS):
        object_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{SAMPLE_SOURCE}:{index}"))
        collection.data.insert(
            uuid=object_id,
            properties={
                "text": text,
                "source": SAMPLE_SOURCE,
                "chunk_index": index,
            },
            vector=sample_vector(index),
        )


@app.get("/health")
def health():
    ready = weaviate_client is not None and weaviate_client.is_ready()
    return {
        "status": "ok",
        "weaviate_ready": ready,
        "embedding_model": EMBEDDING_MODEL,
        "vector_dimension": EXPECTED_VECTOR_DIM,
    }


@app.get("/collections")
def list_collections():
    if weaviate_client is None:
        raise HTTPException(status_code=503, detail="Weaviate client is not ready")

    return weaviate_client.collections.list_all()


@app.get("/documents")
def list_docs(limit: int = 100):
    collection = get_collection()
    res = collection.query.fetch_objects(limit=limit)

    return [
        {
            "id": str(obj.uuid),
            "text": obj.properties.get("text"),
            "source": obj.properties.get("source"),
            "chunk_index": obj.properties.get("chunk_index"),
        }
        for obj in res.objects
    ]


@app.delete("/documents/{doc_id}")
def delete_doc(doc_id: str):
    collection = get_collection()
    deleted = collection.data.delete_by_id(doc_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Document chunk not found")

    return {"status": "ok", "deleted_id": doc_id}


@app.delete("/documents")
def delete_docs_by_source(source: str):
    collection = get_collection()
    result = collection.data.delete_many(where=Filter.by_property("source").equal(source))

    if result.matches == 0:
        raise HTTPException(status_code=404, detail="No document chunks found for source")

    return {
        "status": "ok",
        "source": source,
        "matched": result.matches,
        "deleted": result.successful,
        "failed": result.failed,
    }


@app.post("/upload/text")
def upload_text(payload: TextUploadIn):
    chunks = chunk_text(payload.text, payload.chunk_size, payload.chunk_overlap)
    return save_chunks(payload.source, chunks)


@app.post("/upload/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    source: str | None = Form(default=None),
    chunk_size: int = Form(default=DEFAULT_CHUNK_SIZE, ge=200, le=8000),
    chunk_overlap: int = Form(default=DEFAULT_CHUNK_OVERLAP, ge=0, le=2000),
):
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Upload a PDF file")

    file_bytes = await file.read()
    text = extract_pdf_text(file_bytes)
    chunks = chunk_text(text, chunk_size, chunk_overlap)

    return save_chunks(source or file.filename or "uploaded.pdf", chunks)


@app.post("/search")
def search(payload: SearchIn):
    query_vector = embed_texts([payload.question])[0]
    collection = get_collection()

    res = collection.query.near_vector(
        near_vector=query_vector,
        limit=payload.limit,
        return_metadata=MetadataQuery(distance=True),
    )

    return {
        "question": payload.question,
        "results": [
            {
                "id": str(obj.uuid),
                "text": obj.properties.get("text"),
                "source": obj.properties.get("source"),
                "chunk_index": obj.properties.get("chunk_index"),
                "distance": obj.metadata.distance,
            }
            for obj in res.objects
        ],
    }
