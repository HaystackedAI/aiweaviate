import boto3, botocore, os

from infra.aws_clients import aws

knowledge_base_name = f"octank-financial-unstructured-kb-{aws.suffix}"
knowledge_base_description = "Octank Financial Unstructured Knowledge Base containing 10K financial document for business strategy and company information queries."
foundation_model = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

data_bucket_name = f'octank-financial-unstructured-{aws.suffix}-bucket'
data_sources = [{"type": "S3", "bucket_name": data_bucket_name}]

def create_s3_bucket(bucket_name, region=None):
    s3 = boto3.client('s3', region_name=region)

    try:
        if region is None or region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Bucket '{bucket_name}' created successfully.")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket '{bucket_name}' already exists and is owned by you.")
        else:
            print(f"Failed to create bucket: {e.response['Error']['Message']}")

create_s3_bucket(data_bucket_name, aws.region)


def upload_directory(path, bucket_name):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_to_upload = os.path.join(root, file)
            print(f"Uploading file {file_to_upload} to {bucket_name}")
            aws.s3_client.upload_file(file_to_upload, bucket_name, file)


upload_directory("./unstructured-structured-rag/data/un", data_bucket_name)