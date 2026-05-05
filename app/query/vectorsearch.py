def search(client, vector, limit=3):
    collection = client.collections.get("Doc")

    result = collection.query.near_vector(
        near_vector=vector,
        limit=limit
    )

    return [obj.properties for obj in result.objects]