from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from wv.core.wvclient import get_client
import uuid

client = get_client()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    client.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

COLLECTION = "Doc"


class DocIn(BaseModel):
    text: str
    source: str
    vector: list[float]


@app.get("/collections")
def list_collections():
    return client.collections.list_all()


@app.get("/documents")
def list_docs():
    col = client.collections.get(COLLECTION)
    res = col.query.fetch_objects(limit=100)

    return [
        {
            "id": obj.uuid,
            "text": obj.properties.get("text"),
            "source": obj.properties.get("source"),
        }
        for obj in res.objects
    ]


@app.post("/insert")
def insert_doc(doc: DocIn):
    col = client.collections.get(COLLECTION)

    obj_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.source))

    col.data.replace(
        uuid=obj_id,
        properties={
            "text": doc.text,
            "source": doc.source
        },
        vector=doc.vector
    )

    return {"status": "ok", "id": obj_id}


@app.post("/search")
def search(vector: list[float]):
    col = client.collections.get(COLLECTION)

    res = col.query.near_vector(
        near_vector=vector,
        limit=5
    )

    return [
        {
            "id": obj.uuid,
            "text": obj.properties.get("text"),
            "source": obj.properties.get("source"),
            "distance": obj.metadata.distance
        }
        for obj in res.objects
    ]

