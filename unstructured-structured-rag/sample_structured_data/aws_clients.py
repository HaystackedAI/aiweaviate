# aws_clients.py
import boto3, time

class AWSClients:
    def __init__(self, region="us-east-1"):
        self.region = region

        self.s3_client = boto3.client("s3", region_name=region)
        self.sts_client = boto3.client("sts", region_name=region)

        self.redshift_data_client = boto3.client("redshift-data",region_name=region)
        self.redshift_client = boto3.client("redshift-serverless",region_name=region)

        self.iam_client = boto3.client("iam",region_name=region)

        self.bedrock_agent_client = boto3.client("bedrock-agent",region_name=region)
        self.bedrock_agent_runtime_client = boto3.client("bedrock-agent-runtime",region_name=region)
        
        # current_time = time.time()
        # timestamp_str = time.strftime("%Y%m%d%H%M%S", time.localtime(current_time))[-4:]
        # self.suffix = f"{timestamp_str}"
        
    @property
    def suffix(self):
        return time.strftime("%Y%m%d%H%M%S")[-4:]

        
aws = AWSClients()