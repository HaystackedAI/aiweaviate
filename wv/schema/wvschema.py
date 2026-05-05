# app/schema/wvschema.py
def create_schema(client):
    collections = client.collections.list_all()

    if "Doc" not in collections:
        client.collections.create(
            name="Doc",
            vectorizer_config=None,
            properties=[
                {"name": "text", "data_type": "text"},
                {"name": "source", "data_type": "text"}
            ]
        )