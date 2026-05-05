# app/data/ingestion.py
import uuid

def insert_doc(client, text, source, vector):
    collection = client.collections.get("Doc")

    obj_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, source))

    collection.data.replace(
        uuid=obj_id,
        properties={
            "text": text,
            "source": source
        },
        vector=vector
    )