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

def delete_template(template_name):
    response = ses.delete_template(
    TemplateName=template_name
)

def create_template():
    with open('functions/email_html_template.html', 'r') as f:
        html_string = f.read()

    send_template = {
        "TemplateName": "TempTemplate",
        "SubjectPart": "Greetings, {{name}}!",
        "TextPart": "Dear {{name}},\r\n.",
        "HtmlPart": html_string
    }

    response = ses.create_template(
        Template = send_template
    )

    print(response)

def handler(event, context):
    create_template()
    # delete_template()   

    response = {
        "statusCode": 200,
        "message": 'Success',        
        "headers": {
            "Content-Type": 'application/json',
            "X-Requested-With": '*',
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with,x-correlation-id,x-session-id',
            "Access-Control-Allow-Origin": '*',
            "Access-Control-Allow-Methods": 'POST,GET,OPTIONS'
        }
    }
    
    return response