import os
import boto3
from strands import Agent, tool
from infra.aws_clients import aws

# Set up AWS region and  Amazon Bedrock Agent Runtime client for knowledge base interactions
region = aws.region
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=region)

UNSTRUCTURED_KB_ID = "FGKY9RB1DR"  # From 1-prerequisites-unstructured-kb.ipynb
STRUCTURED_KB_ID = "H876UDGSOR"      # From 0-prerequisites-structured-kb.ipynb


print("="*60)
print(f"Unstructured KB ID: {UNSTRUCTURED_KB_ID}")
print(f"Structured KB ID: {STRUCTURED_KB_ID}")


@tool
def unstructured_data_assistant(query: str) -> str:
    """
    Handle document-based, narrative, and conceptual queries using the unstructured knowledge base.
    
    Args:
        query: A question about business strategies, policies, company information, 
               or requiring document comprehension and qualitative analysis
    
    Returns:
        Raw retrieve response from the unstructured knowledge base
    """
    try:
        retrieve_response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=UNSTRUCTURED_KB_ID,
            retrievalQuery={'text': query},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 10,
                }
            }
        )
        
        return retrieve_response
        
    except Exception as e:
        return f"Error in unstructured data assistant: {str(e)}"


@tool
def structured_data_assistant(query: str) -> str:
    """
    Handle data analysis, metrics, and quantitative queries using the structured knowledge base.
    
    Args:
        query: A question requiring calculations, aggregations, statistical analysis,
               or database operations on structured data
    
    Returns:
        Raw retrieve response from the structured knowledge base
    """
    try:
        retrieve_response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=STRUCTURED_KB_ID,
            retrievalQuery={'text': query},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 10,
                }
            }
        )
        
        return retrieve_response
        
    except Exception as e:
        return f"Error in structured data assistant: {str(e)}"



# Create the orchestrator agent with both tools
orchestrator = Agent(
    system_prompt="""You are an intelligent assistant that routes queries to the appropriate knowledge base. Choose the appropriate tool based on the query type. 
    The tools return raw data that you should analyze and present in a clear, helpful format.""",
    tools=[
        unstructured_data_assistant,
        structured_data_assistant
    ]
)


# EXAMPLE 1: Business Strategy Query (should use unstructured_data_assistant)
print("=== EXAMPLE 1: BUSINESS STRATEGY QUERY ===")
print("Query: What is Octank Financial's business strategy?")
print()

response = orchestrator("What is Octank Financial's business strategy?")
print(response)


# EXAMPLE 2: Financial Data Query (should use structured_data_assistant)
print("=== EXAMPLE 2: FINANCIAL DATA QUERY ===")
print("Query: What is the total spending by all customers?")
print()

response = orchestrator("What is the total spending by all customers?")
print(response)

# Inspect the complete conversation flow
def inspect_message_flow(messages):
    print("=== DETAILED MESSAGE FLOW ===")
    
    for i, message in enumerate(messages):
        print(f"\n--- Message {i+1} ---")
        print(f"Role: {message['role']}")
        
        for j, content in enumerate(message['content']):
            print(f"  Content {j+1}:")
            
            if 'text' in content:
                text = content['text']
                # Truncate long text for readability
                if len(text) > 200:
                    text = text[:200] + "..."
                print(f"    Text: {text}")
            
            elif 'toolUse' in content:
                tool_use = content['toolUse']
                print(f"    Tool Use: {tool_use['name']}")
                print(f"    Input: {tool_use['input']}")
                print(f"    ID: {tool_use['toolUseId']}")
            
            elif 'toolResult' in content:
                tool_result = content['toolResult']
                print(f"    Tool Result: {tool_result['status']}")
                print(f"    ID: {tool_result['toolUseId']}")
                # Don't print full content as it's very long
                print(f"    Content: [Raw KB Response - {len(str(tool_result['content']))} chars]")

# Run the inspection
inspect_message_flow(orchestrator.messages)


