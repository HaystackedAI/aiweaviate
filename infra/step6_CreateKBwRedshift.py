# Knowledge Base Name: redshift-structured-kb-1400
# Knowledge Base configuration: {'type': 'SQL', 'sqlKnowledgeBaseConfiguration': {'type': 'REDSHIFT', 'redshiftConfiguration': {'storageConfigurations': [{'type': 'REDSHIFT', 'redshiftConfiguration': {'databaseName': 'sds-ecommerce'}}], 'queryEngineConfiguration': {'type': 'SERVERLESS', 'serverlessConfiguration': {'workgroupArn': 'arn:aws:redshift-serverless:us-east-1:822206589627:workgroup/26b8362e-d554-457f-8173-ce038691abc5', 'authConfiguration': {'type': 'IAM'}}}}}}
# ========================================================================================
# Step 1 - Creating Knowledge Base Execution Role (AmazonBedrockExecutionRoleForStructuredKnowledgeBase_1400) and Policies
# ========================================================================================
# Step 2 - Creating Knowledge Base
# { 'createdAt': datetime.datetime(2026, 6, 9, 0, 14, 2, 766352, tzinfo=tzutc()),
#   'description': 'Datamond kb',
#   'knowledgeBaseArn': 'arn:aws:bedrock:us-east-1:822206589627:knowledge-base/YBTG6019LE',
#   'knowledgeBaseConfiguration': { 'sqlKnowledgeBaseConfiguration': { 'redshiftConfiguration': { 'queryEngineConfiguration': { 'serverlessConfiguration': { 'authConfiguration': { 'type': 'IAM'},
#                                                                                                                                                            'workgroupArn': 'arn:aws:redshift-serverless:us-east-1:822206589627:workgroup/26b8362e-d554-457f-8173-ce038691abc5'},
#                                                                                                                               'type': 'SERVERLESS'},
#                                                                                                 'storageConfigurations': [ { 'redshiftConfiguration': { 'databaseName': 'sds-ecommerce'},
#                                                                                                                              'type': 'REDSHIFT'}]},
#                                                                      'type': 'REDSHIFT'},
#                                   'type': 'SQL'},
#   'knowledgeBaseId': 'YBTG6019LE',
#   'name': 'redshift-structured-kb-1400',
#   'roleArn': 'arn:aws:iam::822206589627:role/AmazonBedrockExecutionRoleForStructuredKnowledgeBase_1400',
#   'status': 'CREATING',
#   'updatedAt': datetime.datetime(2026, 6, 9, 0, 14, 2, 766352, tzinfo=tzutc())}
# Creating Data Sources aka query engine
# { 'createdAt': datetime.datetime(2026, 6, 9, 0, 14, 2, 921704, tzinfo=tzutc()),
#   'dataSourceConfiguration': {'type': 'REDSHIFT_METADATA'},
#   'dataSourceId': 'DXZEYR30TN',
#   'description': 'Query engine',
#   'knowledgeBaseId': 'YBTG6019LE',
#   'name': 'redshift-structured-kb-1400-ds',
#   'status': 'AVAILABLE',
#   'updatedAt': datetime.datetime(2026, 6, 9, 0, 14, 2, 921704, tzinfo=tzutc())}
# ========================================================================================
# Knowledge Base created successfully!
# 'YBTG6019LE'
# Knowledge Base ID: YBTG6019LE
REDSHIFT_NAMESPACE= "sds-ecommerce-0029"
REDSHIFT_WORKGROUP= "sds-ecommerce-wg-0029"
REDSHIFT_DATABASE= "sds-ecommerce"
# S3 Bucket: sds-ecommerce-redshift-0029
# Created role RedshiftS3AccessRole-0029
redshift_role_arn = "arn:aws:iam::822206589627:role/RedshiftS3AccessRole-0029"
WORKGROUP_ARN = "arn:aws:redshift-serverless:us-east-1:822206589627:workgroup/26b8362e-d554-457f-8173-ce038691abc5"

from aws_clients import aws
from utils.structured_knowledge_base import BedrockStructuredKnowledgeBase
# Configure Knowledge Base parameters
kb_name = f"redshift-structured-kb-{aws.suffix}"
kb_description = "Datamond kb"
# generation_model = "anthropic.claude-3-5-haiku-20241022-v1:0"
generation_model = "us.anthropic.claude-sonnet-4-20250514-v1:0"

print(f"Knowledge Base Name: {kb_name}")

# Configure Knowledge Base parameters for Redshift Serverless with IAM authentication
kb_config_param = {
    "type": "SQL",
    "sqlKnowledgeBaseConfiguration": {
        "type": "REDSHIFT",
        "redshiftConfiguration": {
            "storageConfigurations": [{
                "type": "REDSHIFT",
                "redshiftConfiguration": {
                    "databaseName": REDSHIFT_DATABASE
                }
            }],
            "queryEngineConfiguration": {
                "type": "SERVERLESS",
                "serverlessConfiguration": {
                    "workgroupArn": WORKGROUP_ARN,
                    "authConfiguration": {}
                }
            }
        }
    }
}

kb_config_param['sqlKnowledgeBaseConfiguration']['redshiftConfiguration']['queryEngineConfiguration']['serverlessConfiguration']['authConfiguration']['type'] = "IAM"

print(f"Knowledge Base configuration: {kb_config_param}")

try:
    structured_kb = BedrockStructuredKnowledgeBase(
        kb_name=kb_name,
        kb_description=kb_description,
        workgroup_arn=WORKGROUP_ARN,
        kbConfigParam=kb_config_param,
        generation_model=generation_model,
        suffix=aws.suffix
    )
    
    print("Knowledge Base created successfully!")
    kb_id = structured_kb.get_knowledge_base_id()
    print(f"Knowledge Base ID: {kb_id}")
    
except Exception as e:
    print(f"Error creating Knowledge Base: {str(e)}")
    raise
