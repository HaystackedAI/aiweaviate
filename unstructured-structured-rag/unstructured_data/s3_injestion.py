from s2_kb import unstructured_knowledge_base

# Sync knowledge base
unstructured_knowledge_base.start_ingestion_job()
# Keep the kb_id for invocation later in the invoke request
unstructured_kb_id = unstructured_knowledge_base.get_knowledge_base_id()
print(f"Unstructured Knowledge Base ID: {unstructured_kb_id}")
