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
template_name = os.environ['TEMPLATE_NAME']
ses = boto3.client('ses')

emails = []
if "EMAIL" in env:
    emails.append(os.environ["EMAIL"])
if "EMAIL1" in env:
    emails.append(os.environ["EMAIL1"])  

def scan(key=None, value=None):
    try:
        response = guest_registration_table.scan(
            FilterExpression = Attr(key).begins_with(value))
    except ClientError as err:
        logger.critical("----Client error: {0}".format(err))
        logger.critical(
            "----HTTP code: {0}".format(err.response['ResponseMetadata']['HTTPStatusCode']))
        return {
            "output": None,
            "message" : err.response['Error']['Message'],
            "statusCode" : err.response['ResponseMetadata']['HTTPStatusCode']
        }
    except ParamValidationError as e:
        print(e)
        return {
            "output": None,
            "message" : "ParamValidationError",
            "statusCode" : 400
        } 
    else:
        if len(response["Items"]) == 0:
            return {
                "message" : "Success",
                "statusCode" : 200
            } 
        else:
            return {
                "output": response["Items"][0],
                "message" : "Already exists",
                "statusCode" : 409
            } 

def check_email_exists(email):
    response = scan("email", email)
    return response

def send_ses(email, token, first_name):
    link = 'https://1gxq5w09z7.execute-api.eu-central-1.amazonaws.com/dev/registration/' + token
    template_data = '{ \"name\": \"' + first_name + ' \", \"link\": \"' + link + ' \" }' 
    try:
        result = ses.send_templated_email(
            Source=emails[1],
            Destination={
                'ToAddresses': [email]
            },
            Template=template_name,
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

def update_item(item):
    guest_registration_id = item["registrationId"]
    first_name = item["firstName"]
    last_name = item['lastName']
    organization_name = item['organizationName']
    email = item['email']
    business_interests = item['businessInterests']
    technical_interests = item['technicalInterests']

    try:
        response = guest_registration_table.put_item(
            Item={
                    'registrationId': guest_registration_id,
                    'firstName': first_name,
                    'lastName': last_name,
                    'organizationName': organization_name,
                    'email': email,
                    'businessInterests': business_interests,
                    'technicalInterests': technical_interests,
                    'isCanceled': False
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
                    'technicalInterests': technical_interests ,
                    'isCanceled': False
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

    response = check_email_exists(email)
    if response["statusCode"] == 200:
        response = put_item(first_name, last_name, position, email, organization_name, business_interests, \
                                                             technical_interests) 
    
        if response["statusCode"] == 200:
            guest_registration_id = response["output"]
            response = send_ses(email, guest_registration_id, first_name)     
            if response["statusCode"] == 200:    
                response["output"] = guest_registration_id
                
    elif response["statusCode"] == 409:
        if response["output"]["isCanceled"] == True:
            response = update_item(response["output"])
            if response["statusCode"] == 200:
                guest_registration_id = response["output"]
                response = send_ses(email, guest_registration_id, first_name)
                if response["statusCode"] == 200:    
                    response["output"] = guest_registration_id

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