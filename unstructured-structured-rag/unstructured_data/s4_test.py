import logging
import boto3
from infra.aws_clients import aws

logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
bedrock_agent_runtime_client = boto3.client("bedrock-agent-runtime")


# query = "What is Octank Financial's primary business strategy?"
query = "summarize the key points from the document about Octank Financial's primary business strategy."

foundation_model = "amazon.nova-micro-v1:0"

response = bedrock_agent_runtime_client.retrieve_and_generate(
    input={
        "text": query
    },
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            'knowledgeBaseId': "FGKY9RB1DR",
            "modelArn": "arn:aws:bedrock:{}::foundation-model/{}".format(aws.region, foundation_model),
            "retrievalConfiguration": {
                "vectorSearchConfiguration": {
                    "numberOfResults": 5
                } 
            }
        }
    }
)

print("Response:")
print(response['output']['text'], end='\\n'*2)
