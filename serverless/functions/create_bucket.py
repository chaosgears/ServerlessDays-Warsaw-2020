import boto3
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = os.environ['REGION']
bucket_name = os.environ['BUCKET_NAME']
s3 = boto3.client('s3', region_name = region)

def create_bucket(acl):
    try:
        location = {'LocationConstraint': region}
        s3.create_bucket(ACL = acl, Bucket = bucket_name,
                        CreateBucketConfiguration = location)
        bucket_waiter = s3.get_waiter('bucket_exists')
        bucket_waiter.wait(Bucket = bucket_name)
    except ClientError as err:
        logging.error(err)
        return False
    return True

def put_file(body, key):
    try:
        s3.put_object(
            Bucket = bucket_name, Body = body, Key = key)
   
    except ClientError as err:
        logging.error(err)
        return False
        
    return True

def handler(event, context):
    if create_bucket('private') == True:
        put_file('', '/files')
        put_file('', '/helpers')