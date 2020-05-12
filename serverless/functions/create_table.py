import boto3
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = os.environ['REGION']
table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb', region_name=region)

def handler(event, context):
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'registrationId',
                    'KeyType': 'HASH'  #Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'registrationId',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )   
    except ClientError as err:
        logger.critical("----Client error: {0}".format(err))
        logger.critical(
            "----HTTP code: {0}".format(err.response['ResponseMetadata']['HTTPStatusCode']))
        print(err.response['Error']['Message'])
    
    print("Table status:", table.table_status)

            
       