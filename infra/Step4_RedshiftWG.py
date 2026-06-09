REDSHIFT_NAMESPACE= "sds-ecommerce-0029"
REDSHIFT_WORKGROUP= "sds-ecommerce-wg-0029"
REDSHIFT_DATABASE= "sds-ecommerce"
# S3 Bucket: sds-ecommerce-redshift-0029
# Created role RedshiftS3AccessRole-0029
redshift_role_arn = "arn:aws:iam::822206589627:role/RedshiftS3AccessRole-0029"
WorkgroupARN = "arn:aws:redshift-serverless:us-east-1:822206589627:workgroup/26b8362e-d554-457f-8173-ce038691abc5"

import os, requests, json, time

from utils.structured_knowledge_base import BedrockStructuredKnowledgeBase
from aws_clients import aws

def create_redshift_workgroup():
    """Create Redshift Serverless workgroup"""
    try:
        # Check if workgroup already exists
        try:
            response = aws.redshift_client.get_workgroup(workgroupName=REDSHIFT_WORKGROUP)
            print(f'Workgroup {REDSHIFT_WORKGROUP} already exists')
            return response['workgroup']
        except aws.redshift_client.exceptions.ResourceNotFoundException:
            print(f'Creating workgroup {REDSHIFT_WORKGROUP}...')
        
        # Create the workgroup
        response = aws.redshift_client.create_workgroup(
            workgroupName=REDSHIFT_WORKGROUP,
            namespaceName=REDSHIFT_NAMESPACE,
            baseCapacity=8,  # Minimum base capacity
            enhancedVpcRouting=False,
            publiclyAccessible=True,
            configParameters=[
                {
                    'parameterKey': 'enable_user_activity_logging',
                    'parameterValue': 'true'
                }
            ]
        )
        
        print(f'Created workgroup {REDSHIFT_WORKGROUP}')
        
        # Wait for workgroup to be available
        print('Waiting for workgroup to be available...')
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                workgroup_response = aws.redshift_client.get_workgroup(workgroupName=REDSHIFT_WORKGROUP)
                status = workgroup_response['workgroup']['status']
                if status == 'AVAILABLE':
                    print(f'Workgroup {REDSHIFT_WORKGROUP} is now available')
                    return workgroup_response['workgroup']
                else:
                    print(f'Workgroup status: {status}, waiting...')
                    time.sleep(10)
            except Exception as e:
                print(f'Error checking workgroup status: {str(e)}, retrying...')
                time.sleep(10)
        
        print('Timeout waiting for workgroup, but proceeding...')
        return response['workgroup']
        
    except Exception as e:
        print(f'Error creating workgroup: {str(e)}')
        raise

# Create workgroup
workgroup = create_redshift_workgroup()
workgroup_arn = workgroup['workgroupArn']
print(f"Workgroup ARN: {workgroup_arn}")


# def create_s3_bucket():
#     """Create S3 bucket for data staging"""
#     try:
#         s3_client.head_bucket(Bucket=S3_BUCKET)
#         print(f'Bucket {S3_BUCKET} already exists')
#     except:
#         try:
#             if region == 'us-east-1':
#                 s3_client.create_bucket(Bucket=S3_BUCKET)
#             else:
#                 s3_client.create_bucket(
#                     Bucket=S3_BUCKET,
#                     CreateBucketConfiguration={'LocationConstraint': region}
#                 )
#             print(f'Created bucket {S3_BUCKET}')
#         except Exception as e:
#             print(f'Error creating bucket: {str(e)}')
#             raise

# # Create S3 bucket
# create_s3_bucket()


# def upload_sample_data():
#     """Upload sample CSV files to S3"""
#     data_files = ['orders.csv', 'order_items.csv', 'payments.csv', 'reviews.csv']
#     sds_directory = 'sample_structured_data'
    
#     print("Uploading sample data files to S3...")
#     files_found = 0
    
#     for file_name in data_files:
#         local_path = os.path.join(sds_directory, file_name)
#         if os.path.exists(local_path):
#             # Get file size for informational purposes
#             file_size = os.path.getsize(local_path)
#             file_size_mb = file_size / (1024 * 1024)
            
#             s3_client.upload_file(local_path, S3_BUCKET, file_name)
#             print(f'Uploaded {file_name} ({file_size_mb:.1f} MB) to S3')
#             files_found += 1
#         else:
#             print(f'Warning: {local_path} not found')
    
#     if files_found == len(data_files):
#         print(f"\nSuccessfully uploaded all {files_found} data files to S3")
#     else:
#         print(f"\nOnly {files_found} out of {len(data_files)} files were found and uploaded")

# # Upload sample data
# upload_sample_data()


# def wait_for_statement(statement_id):
#     """Wait for a Redshift Data API statement to complete"""
#     max_attempts = 30
#     for attempt in range(max_attempts):
#         try:
#             response = redshift_data_client.describe_statement(Id=statement_id)
#             status = response['Status']
#             if status == 'FINISHED':
#                 return response
#             elif status == 'FAILED':
#                 raise Exception(f"Statement failed: {response.get('Error', 'Unknown error')}")
#             elif status == 'CANCELLED':
#                 raise Exception("Statement was cancelled")
#             else:
#                 print(f"Statement status: {status}, waiting...")
#                 time.sleep(5)
#         except Exception as e:
#             if 'Statement failed' in str(e) or 'cancelled' in str(e):
#                 raise
#             print(f"Error checking statement status: {str(e)}, retrying...")
#             time.sleep(5)
    
#     raise Exception("Timeout waiting for statement to complete")

# def run_redshift_statement(sql_statement):
#     """Execute a SQL statement in Redshift"""
#     try:
#         response = redshift_data_client.execute_statement(
#             WorkgroupName=REDSHIFT_WORKGROUP,
#             Database=REDSHIFT_DATABASE,
#             Sql=sql_statement
#         )
#         statement_id = response['Id']
#         print(f"Executing statement: {statement_id}")
#         result = wait_for_statement(statement_id)
#         print(f"Statement completed successfully")
#         return result
#     except Exception as e:
#         print(f"Error executing statement: {str(e)}")
#         raise


# # Create tables in Redshift
# def create_tables():
#     """Create all necessary tables in Redshift"""
    
#     # Orders table
#     orders_sql = """
#     CREATE TABLE IF NOT EXISTS orders (
#         order_id VARCHAR(255) PRIMARY KEY,
#         customer_id VARCHAR(255),
#         order_total DECIMAL(10,2),
#         order_status VARCHAR(50),
#         payment_method VARCHAR(50),
#         shipping_address TEXT,
#         created_at TIMESTAMP,
#         updated_at TIMESTAMP
#     );
#     """
    
#     # Order Items table
#     order_items_sql = """
#     CREATE TABLE IF NOT EXISTS order_items (
#         order_item_id VARCHAR(255) PRIMARY KEY,
#         order_id VARCHAR(255),
#         product_id VARCHAR(255),
#         quantity INTEGER,
#         price DECIMAL(10,2)
#     );
#     """
    
#     # Payments table
#     payments_sql = """
#     CREATE TABLE IF NOT EXISTS payments (
#         payment_id VARCHAR(255) PRIMARY KEY,
#         order_id VARCHAR(255),
#         customer_id VARCHAR(255),
#         amount DECIMAL(10,2),
#         payment_method VARCHAR(50),
#         payment_status VARCHAR(50),
#         created_at DATE
#     );
#     """
    
#     # Reviews table
#     reviews_sql = """
#     CREATE TABLE IF NOT EXISTS reviews (
#         review_id VARCHAR(255) PRIMARY KEY,
#         product_id VARCHAR(255),
#         customer_id VARCHAR(255),
#         rating INTEGER,
#         created_at DATE
#     );
#     """
    
#     tables = {
#         'orders': orders_sql,
#         'order_items': order_items_sql,
#         'payments': payments_sql,
#         'reviews': reviews_sql
#     }
    
#     for table_name, sql in tables.items():
#         print(f"Creating table: {table_name}")
#         run_redshift_statement(sql)
#         print(f"Created table: {table_name}")
#         print("-------------")

# # Create tables
# create_tables()
