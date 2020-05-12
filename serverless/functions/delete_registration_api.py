import boto3
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = os.environ['REGION']
table_name = os.environ['TABLE_NAME']
dynamodb_client = boto3.client('dynamodb', region_name=region)

def lambda_handler(event, context):
    registration_id = event['registration_id']

    try:
        dynamodb_client.delete_item(
            Key={
                'registrationId': {
                    'S': registration_id
                }
            },
            TableName=table_name
        )

    except ClientError as err:
        logger.critical("----Client error: {0}".format(err))
        logger.critical(
            "----HTTP code: {0}".format(err.response['ResponseMetadata']['HTTPStatusCode']))
        message = err.response['Error']['Message']
        statusCode = err.response['ResponseMetadata']['HTTPStatusCode']
    else:
        message = "Registration " + registration_id + " has been successfully deleted."
        statusCode = 200
        
    response = {
        "statusCode": statusCode,
        "message": message,
        "headers": {
            "Content-Type": 'application/json',
            "X-Requested-With": '*',
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with,x-correlation-id,x-session-id',
            "Access-Control-Allow-Origin": '*',
            "Access-Control-Allow-Methods": 'POST,GET,OPTIONS'
        }

    }

    return response
            
       