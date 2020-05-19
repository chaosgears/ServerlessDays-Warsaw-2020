import boto3
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = os.environ['REGION']
table_registration = os.environ['TABLE_REGISTRATION']
table_presentation = os.environ['TABLE_PRESENTATION']
dynamodb = boto3.resource('dynamodb', region_name=region)

def create_table(table_name, primary_key):
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': primary_key,
                    'KeyType': 'HASH'  #Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': primary_key,
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 15,
                'WriteCapacityUnits': 15
            }
        )   
    except ClientError as err:
        logger.critical("----Client error: {0}".format(err))
        logger.critical(
            "----HTTP code: {0}".format(err.response['ResponseMetadata']['HTTPStatusCode']))
        print(err.response['Error']['Message'])
    
    print("Table status:", table.table_status)

def handler(event, context):
    #create_table(table_registration, 'registrationId')
    create_table(table_presentation, 'presentationId')

            
       