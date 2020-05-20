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
region = os.environ['REGION']
ses = boto3.client('ses')

def delete_template(template_name):
    response = ses.delete_template(
    TemplateName=template_name
)

def create_template():
    with open('functions/email_html_template.html', 'r') as f:
        html_string = f.read()

    send_template = {
        "TemplateName": "ServerlessDays-Warsaw-2020",
        "SubjectPart": "Greetings {{name}}, you've just registered on ServerlessDays Warsaw 2020!",
        "TextPart": "Dear {{name}},\r\n.",
        "HtmlPart": html_string
    }

    response = ses.create_template(
        Template = send_template
    )

    print(response)

def create_template_thanks_for_cfp():
    with open('functions/email_html_call_for_papers.html', 'r') as f:
        html_string = f.read()

    send_template = {
        "TemplateName": "ServerlessDays-Warsaw-2020-cfp",
        "SubjectPart": "Presentation confirmation!",
        "TextPart": "Dear {{name}},\r\n.",
        "HtmlPart": html_string
    }

    response = ses.create_template(
        Template = send_template
    )

    print(response)

def handler(event, context):
    create_template_thanks_for_cfp()
    # delete_template('ServerlessDays-Warsaw-2020-cfp')   

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