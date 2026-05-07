import weaviate

def get_client():
    client = weaviate.connect_to_local(
        host="localhost",
        port=8080,
        skip_init_checks=True
        # grpc_port=50051
    )

    return client