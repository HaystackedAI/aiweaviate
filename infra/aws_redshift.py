import time
from aws_clients import aws

REDSHIFT_NAMESPACE= "sds-ecommerce-0029"
REDSHIFT_WORKGROUP= "sds-ecommerce-wg-0029"
REDSHIFT_DATABASE= "sds-ecommerce"
# S3 Bucket: sds-ecommerce-redshift-0029
# Created role RedshiftS3AccessRole-0029
redshift_role_arn = "arn:aws:iam::822206589627:role/RedshiftS3AccessRole-0029"
WORKGROUP_ARN = "arn:aws:redshift-serverless:us-east-1:822206589627:workgroup/26b8362e-d554-457f-8173-ce038691abc5"

def wait_for_statement(statement_id):
    """Wait for a Redshift Data API statement to complete"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = aws.redshift_data_client.describe_statement(Id=statement_id)
            status = response['Status']
            if status == 'FINISHED':
                return response
            elif status == 'FAILED':
                raise Exception(f"Statement failed: {response.get('Error', 'Unknown error')}")
            elif status == 'CANCELLED':
                raise Exception("Statement was cancelled")
            else:
                print(f"Statement status: {status}, waiting...")
                time.sleep(5)
        except Exception as e:
            if 'Statement failed' in str(e) or 'cancelled' in str(e):
                raise
            print(f"Error checking statement status: {str(e)}, retrying...")
            time.sleep(5)
    
    raise Exception("Timeout waiting for statement to complete")

def run_redshift_statement(sql_statement):
    """Execute a SQL statement in Redshift"""
    try:
        response = aws.redshift_data_client.execute_statement(
            WorkgroupName=REDSHIFT_WORKGROUP,
            Database=REDSHIFT_DATABASE,
            Sql=sql_statement
        )
        statement_id = response['Id']
        print(f"Executing statement: {statement_id}")
        result = wait_for_statement(statement_id)
        print(f"Statement completed successfully")
        return result
    except Exception as e:
        print(f"Error executing statement: {str(e)}")
        raise
