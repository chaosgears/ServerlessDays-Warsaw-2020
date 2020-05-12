import boto3
import os
import json
import uuid
from boto3.dynamodb.conditions import Key, Attr
import logging
from botocore.exceptions import ClientError
from botocore.exceptions import ParamValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
env = os.environ.copy()
region = os.environ['REGION']
dynamodb = boto3.resource('dynamodb', region_name=region)
dynamodb_client = boto3.client('dynamodb', region_name=region)
guest_registration_table_name = os.environ['TABLE_NAME']
guest_registration_table = dynamodb.Table(guest_registration_table_name)
ses = boto3.client('ses')

emails = []
if "EMAIL" in env:
    emails.append(os.environ["EMAIL"])
if "EMAIL1" in env:
    emails.append(os.environ["EMAIL1"])  

def send_ses(email, token):
    link = 'http://example_link.s3-website.eu-central-1.amazonaws.com/guest_registration?uuid=' + token
    try:
        result = ses.send_email(
            Destination={
                'ToAddresses': [email]
            },
            ReplyToAddresses=[emails[0]],
            Message={
                'Subject': {  
                    'Data': "ServerlessDays Warsaw 2020 - Confirmation email"
                },
                'Body': {
                    'Text': {
                        'Data': ": %s" % link
                    }
                }
            },
            Source=emails[0]
        )
    except ClientError as e:
        message = e.response['Error']['Message']
        statusCode = e.response['ResponseMeta data']['HTTPStatusCode']
        return (statusCode, message)
    else:
        return (200, ("Email sent! Message ID: %s", result['MessageId']))


def put_item(first_name, last_name, position, address, email, organization_name, business_interests, \
                                                         technical_interests):
    guest_registration_id = str(uuid.uuid4())
 
    try:
        response = guest_registration_table.put_item(
            Item={
                    'registrationId': guest_registration_id,
                    'firstName': first_name,
                    'lastName': last_name,
                    'organizationName': organization_name, 
                    'address' : address, 
                    'email': email,
                    'businessInterests': business_interests,
                    'technicalInterests': technical_interests 
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
        return response
        
    response = { 
                "statusCode" : 200,
                "message": "Success",
                "output": guest_registration_id
                }

    return response


def handler(event, context):
    first_name = event['json']['firstName']
    last_name = event['json']['lastName']
    email = event['json']['email']
    position =  event['json']['position']
    address =  event['json']['address']
    organization_name = event['json']['organizationName']
    business_interests =  event['json']['business_interests']
    technical_interests = event['json']['technical_interests']

    response = put_item(first_name, last_name, position, address, email, organization_name, business_interests, \
                                                         technical_interests)      

    response = {
        "statusCode": response["statusCode"],
        "message": response["message"],
        "output": response["output"],        
        "headers": {
            "Content-Type": 'application/json',
            "X-Requested-With": '*',
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with,x-correlation-id,x-session-id',
            "Access-Control-Allow-Origin": '*',
            "Access-Control-Allow-Methods": 'POST,GET,OPTIONS'
        }
    }
    
    return response