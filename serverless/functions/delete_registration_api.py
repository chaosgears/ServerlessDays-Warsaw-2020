import boto3
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = os.environ['REGION']
table_name = os.environ['TABLE_NAME']
dynamodb_client = boto3.client('dynamodb', region_name=region)

def handler(event, context):
    registration_id = event['registration_id']

    # Get guest with specified registration id
    try:
        response = dynamodb_client.get_item(
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
        message = "Registration " + registration_id + " has been successfully canceled."
        statusCode = 200

    if "Item" not in response:
        message = "Registration not found"
        statusCode = 404
    else:
        item = response["Item"]
        # Change flag 
        try:
            dynamodb_client.put_item(
                TableName=table_name,
                Item={
                        'registrationId': item['registrationId'],
                        'firstName': item['firstName'],
                        'lastName': item['lastName'],
                        'organizationName': item['organizationName'],
                        'email': item['email'],
                        'businessInterests': item['businessInterests'],
                        'technicalInterests': item['technicalInterests'],
                        'isCanceled': {
                            'BOOL': True
                        }
                    }
            )

        except ClientError as e:
            logger.critical("----Client error: {0}".format(e))
            logger.critical(
                "----HTTP code: {0}".format(e.response['ResponseMetadata']['HTTPStatusCode']))
            message = e.response['Error']['Message']
            response = { "statusCode" : e.response['ResponseMetadata']['HTTPStatusCode'],
                        "message": message,
                        "output": None }

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
            
       