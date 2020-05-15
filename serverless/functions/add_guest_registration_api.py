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


def delete_template():
    response = client.delete_template(
    TemplateName='MyTemplate'
)

def create_template():
    with open('functions/email_html_template.html', 'r') as f:
        html_string = f.read()

    send_template = {
        "TemplateName": "MyTemplate",
        "SubjectPart": "Greetings, {{name}}!",
        "TextPart": "Dear {{name}},\r\n.",
        "HtmlPart": html_string
    }

    response = ses.create_template(
        Template = send_template
    )

    print(response)

def send_ses(email, token, first_name):
    link = 'http://example_link.s3-website.eu-central-1.amazonaws.com/guest_registration?uuid=' + token
    template_data = '{ \"name\": \"' + first_name + ' \", \"link\": \"' + link + ' \" }' 
    try:
        result = ses.send_templated_email(
            Source=emails[0],
            Destination={
                'ToAddresses': [email]
            },
            # ReplyToAddresses=[emails[0]],
            # Message={
            #     'Subject': {  
            #         'Data': "ServerlessDays Warsaw 2020 - Confirmation email"
            #     },
            #     'Body': {
            #         'Text': {
            #             'Data': ": %s" % link
            #         }
            #     }
            # },
            
            Template='MyTemplate',
            TemplateData=template_data     
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
    else:
        response = { 
            "statusCode" : 200,
            "message": ("Email sent! Message ID: %s", result['MessageId']),
            "output":  result['MessageId']
        }
        
        return response


def put_item(first_name, last_name, position, email, organization_name, business_interests, \
                                                         technical_interests):
    guest_registration_id = str(uuid.uuid4())
 
    try:
        response = guest_registration_table.put_item(
            Item={
                    'registrationId': guest_registration_id,
                    'firstName': first_name,
                    'lastName': last_name,
                    'organizationName': organization_name,
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
    organization_name = event['json']['organizationName']
    business_interests =  event['json']['businessInterests']
    technical_interests = event['json']['technicalInterests']

    response = put_item(first_name, last_name, position, email, organization_name, business_interests, \
                                                         technical_interests) 

    # create_template()
    # delete_template()
    if response["statusCode"] == 200:
        guest_registration_id = response["output"]
        response = send_ses(email, guest_registration_id, first_name)     


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