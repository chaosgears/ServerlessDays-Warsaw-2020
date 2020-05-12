import json
import boto3
from botocore.exceptions import ClientError
import os
import uuid
from boto3.dynamodb.conditions import Key, Attr
import logging
from botocore.exceptions import ClientError
from botocore.exceptions import ParamValidationError

ses = boto3.client('ses')
env = os.environ.copy()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = os.environ['REGION']
dynamodb = boto3.resource('dynamodb', region_name=region)
dynamodb_client = boto3.client('dynamodb', region_name=region)
guest_registration_table_name = os.environ['TABLE_NAME']
guest_registration_table = dynamodb.Table(guest_registration_table_name)

emails = []
if "EMAIL" in env:
    emails.append(os.environ["EMAIL"])
if "EMAIL1" in env:
    emails.append(os.environ["EMAIL1"])  

def put_item_to_invitation_table(email=None, organization_id=None):
    token = uuid.uuid4().hex
    try:
        response = invitation_table.put_item(
            Item={
                    'invitationId': token,
                    'email': email,
                    'organizationId': organization_id
                }
        )
    except ClientError as err:
        logger.critical("----Client error: {0}".format(err))
        logger.critical(
            "----HTTP code: {0}".format(err.response['ResponseMetadata']['HTTPStatusCode']))
        message = err.response['Error']['Message']
        statusCode = err.response['ResponseMetadata']['HTTPStatusCode']
        token = None
        response = {
            "message": message,
            "statusCode": statusCode,
            "token": None
        }

        return response

    response = {
        "message": "Success!",
        "statusCode": 200,
        "token": token
    }

    return response

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
                    'Data': "Flowcontrol - Invitation email"
                },
                'Body': {
                    'Text': {
                        'Data':  "This is link for registration: %s" % link #link for registration
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

def handler(event, context):
    sub = event['sub']
    email = event['json']['email']
    response = send_ses(email)
    statusCode = response[0]
    message = response[1]
    output = response["token"]

    response = {
        "statusCode": statusCode,
        "message": message,
        "output" : output,
        "headers": {
            "Content-Type": 'application/json',
            "X-Requested-With": '*',
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with,x-correlation-id,x-session-id',
            "Access-Control-Allow-Origin": '*',
            "Access-Control-Allow-Methods": 'POST,GET,OPTIONS'
        }
    }
    return response