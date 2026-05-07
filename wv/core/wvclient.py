import weaviate

def get_client():
    client = weaviate.connect_to_local(
        host="localhost",
        port=8080,
        grpc_port=8082
    )

    return client