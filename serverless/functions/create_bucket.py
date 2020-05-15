import boto3
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = os.environ['REGION']
bucket_priv = os.environ['BUCKET_PRIV']
bucket_public = os.environ['BUCKET_PUBLIC']
s3 = boto3.client('s3', region_name = region)

def create_bucket(bucket_name, acl):
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

def put_file(bucket_name, body, key):
    try:
        s3.put_object(
            Bucket = bucket_name, Body = body, Key = key)
   
    except ClientError as err:
        logging.error(err)
        return False
        
    return True

def handler(event, context):
    if create_bucket(bucket_priv, 'private') == True:
        put_file(bucket_priv, '', 'files/')

    if create_bucket(bucket_public, 'public-read') == True:
        put_file(bucket_public, '', 'helpers/')