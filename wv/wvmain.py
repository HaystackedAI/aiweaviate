# main.py
from core.wvclient import get_client
from schema.wvschema import create_schema
from data.ingestion import insert_doc
from query.vectorsearch import search

client = get_client()

try:
    print("Connected:", client.is_ready())

    create_schema(client)

    insert_doc(
        client,
        "Sanofi builds biomedical AI systems",
        "doc1",
        [0.1, 0.2, 0.3]
    )

    results = search(client, [0.1, 0.2, 0.3])

    print("\nRESULTS:")
    for r in results:
        print(r)

finally:
    client.close()