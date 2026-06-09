import time

from infra.s6_kb_stru_Redshift import structured_kb
from aws_redshift import run_redshift_statement

# Extract the IAM role name from the ARN for database user creation
kb_details = structured_kb.knowledge_base

bedrock_role_arn = kb_details['roleArn']
bedrock_role_name = bedrock_role_arn.split('/')[-1]
print(f"   Extracted Role Name: {bedrock_role_name}")



# Create the IAM user in Redshift (this is the critical missing step!)
create_user_sql = f'CREATE USER "IAMR:{bedrock_role_name}" WITH PASSWORD DISABLE;'

try:
    print(f"Creating user: IAMR:{bedrock_role_name}")
    run_redshift_statement(create_user_sql)
    print("IAM user created successfully!")
except Exception as e:
    if "already exists" in str(e).lower():
        print("User already exists, continuing...")
    else:
        print(f"Error creating user: {str(e)}")
        raise


# Grant SELECT on all tables in public schema
grant_select_sql = f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "IAMR:{bedrock_role_name}";'

try:
    print(f"Granting SELECT permissions to: IAMR:{bedrock_role_name}")
    run_redshift_statement(grant_select_sql)
    print("SELECT permissions granted successfully!")
except Exception as e:
    print(f"Error granting permissions: {str(e)}")
    raise


# Wait a bit for the Knowledge Base to be fully ready
time.sleep(60)
structured_kb.start_ingestion_job()


# (rag) PS A:\rag\infra> python step7_iam.py
# Knowledge Base Name: redshift-structured-kb-0049
# Knowledge Base configuration: {'type': 'SQL', 'sqlKnowledgeBaseConfiguration': {'type': 'REDSHIFT', 'redshiftConfiguration': {'storageConfigurations': [{'type': 'REDSHIFT', 'redshiftConfiguration': {'databaseName': 'sds-ecommerce'}}], 'queryEngineConfiguration': {'type': 'SERVERLESS', 'serverlessConfiguration': {'workgroupArn': 'arn:aws:redshift-serverless:us-east-1:822206589627:workgroup/26b8362e-d554-457f-8173-ce038691abc5', 'authConfiguration': {'type': 'IAM'}}}}}}
# ========================================================================================
# Step 1 - Creating Knowledge Base Execution Role (AmazonBedrockExecutionRoleForStructuredKnowledgeBase_0049) and Policies
# ========================================================================================
# Step 2 - Creating Knowledge Base
# { 'createdAt': datetime.datetime(2026, 6, 9, 4, 0, 51, 502323, tzinfo=tzutc()),
#   'description': 'Datamond kb',
#   'knowledgeBaseArn': 'arn:aws:bedrock:us-east-1:822206589627:knowledge-base/H876UDGSOR',
#   'knowledgeBaseConfiguration': { 'sqlKnowledgeBaseConfiguration': { 'redshiftConfiguration': { 'queryEngineConfiguration': { 'serverlessConfiguration': { 'authConfiguration': { 'type': 'IAM'},
#                                                                                                                                                            'workgroupArn': 'arn:aws:redshift-serverless:us-east-1:822206589627:workgroup/26b8362e-d554-457f-8173-ce038691abc5'},
#                                                                                                                               'type': 'SERVERLESS'},
#                                                                                                 'storageConfigurations': [ { 'redshiftConfiguration': { 'databaseName': 'sds-ecommerce'},
#                                                                                                                              'type': 'REDSHIFT'}]},
#                                                                      'type': 'REDSHIFT'},
#                                   'type': 'SQL'},
#   'knowledgeBaseId': 'H876UDGSOR',
#   'name': 'redshift-structured-kb-0049',
#   'roleArn': 'arn:aws:iam::822206589627:role/AmazonBedrockExecutionRoleForStructuredKnowledgeBase_0049',
#   'status': 'CREATING',
#   'updatedAt': datetime.datetime(2026, 6, 9, 4, 0, 51, 502323, tzinfo=tzutc())}
# Creating Data Sources aka query engine
# { 'createdAt': datetime.datetime(2026, 6, 9, 4, 0, 51, 721123, tzinfo=tzutc()),
#   'dataSourceConfiguration': {'type': 'REDSHIFT_METADATA'},
#   'dataSourceId': 'OPOEPGM5LP',
#   'description': 'Query engine',
#   'knowledgeBaseId': 'H876UDGSOR',
#   'name': 'redshift-structured-kb-0049-ds',
#   'status': 'AVAILABLE',
#   'updatedAt': datetime.datetime(2026, 6, 9, 4, 0, 51, 721123, tzinfo=tzutc())}
# ========================================================================================
# Knowledge Base created successfully!
# 'H876UDGSOR'
# Knowledge Base ID: H876UDGSOR
#    Extracted Role Name: AmazonBedrockExecutionRoleForStructuredKnowledgeBase_0049
# Creating user: IAMR:AmazonBedrockExecutionRoleForStructuredKnowledgeBase_0049
# Executing statement: 4fb3ce38-754c-4869-9818-eff4437f35a0
# Statement status: PICKED, waiting...
# Statement completed successfully
# IAM user created successfully!
# Granting SELECT permissions to: IAMR:AmazonBedrockExecutionRoleForStructuredKnowledgeBase_0049
# Executing statement: a55ab25f-4384-4a93-abfa-410dd6c532d9
# Statement status: STARTED, waiting...
# Statement completed successfully
# SELECT permissions granted successfully!
# job  started successfully

# { 'dataSourceId': 'OPOEPGM5LP',
#   'ingestionJobId': 'FLJPNZTS5V',
#   'knowledgeBaseId': 'H876UDGSOR',
#   'startedAt': datetime.datetime(2026, 6, 9, 4, 2, 5, 102133, tzinfo=tzutc()),
#   'status': 'COMPLETE',
#   'updatedAt': datetime.datetime(2026, 6, 9, 4, 2, 14, 766058, tzinfo=tzutc())}