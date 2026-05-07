from weaviate.classes.config import DataType, Property


PROPERTIES = [
    Property(name="text", data_type=DataType.TEXT),
    Property(name="source", data_type=DataType.TEXT),
    Property(name="chunk_index", data_type=DataType.INT),
]


def create_schema(client):
    collections = client.collections.list_all()

    if "Doc" not in collections:
        client.collections.create(
            name="Doc",
            vectorizer_config=None,
            properties=PROPERTIES,
        )
        return

    collection = client.collections.get("Doc")
    existing = {prop.name for prop in collection.config.get().properties}

    for prop in PROPERTIES:
        if prop.name not in existing:
            collection.config.add_property(prop)
