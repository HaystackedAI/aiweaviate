import boto3, botocore, os

from infra.aws_clients import aws
from infra.utils.knowledge_base import BedrockKnowledgeBase

foundation_model = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

knowledge_base_name = f"octank-financial-unstructured-kb-{aws.suffix}"
knowledge_base_description = "Octank Financial Unstructured Knowledge Base containing 10K financial document for business strategy and company information queries."
data_bucket_name = f'octank-financial-unstructured-{aws.suffix}-bucket'
data_sources = [{"type": "S3", "bucket_name": data_bucket_name}]

knowledge_base_name_corr = f"hr-agent-knowledge-base-{aws.suffix}"
knowledge_base_description_corr = "HR Agent Knowledge Base containing onboarding and benefits documentation."
data_bucket_name_corr = f'bedrock-hr-agent-{aws.suffix}-bucket' # replace it with your first bucket name.
data_sources_corr=[{"type": "S3", "bucket_name": data_bucket_name_corr}]


unstructured_knowledge_base = BedrockKnowledgeBase(
    kb_name=f'{knowledge_base_name}',
    kb_description=knowledge_base_description,
    data_sources=data_sources,
    chunking_strategy="FIXED_SIZE", 
    suffix=f'{aws.suffix}-u' 
)



knowledge_base = BedrockKnowledgeBase(
    kb_name=f'{knowledge_base_name_corr}',
    kb_description=knowledge_base_description_corr,
    data_sources=data_sources_corr,
    chunking_strategy = "FIXED_SIZE", 
    suffix = f'{aws.suffix}-f'
)