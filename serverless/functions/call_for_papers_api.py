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
cfp_table_name = os.environ['TABLE_NAME1']
cfp_table = dynamodb.Table(cfp_table_name)
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
        return {
            "output": response,
            "message" : "Success",
            "statusCode" : 200
        } 
        

def check_guest_registration_exists(email):
    response = scan("email", email)
    print(response)
    if len(response["output"]["Items"]) != 0:
        return {
            "message" : "Success",
            "statusCode" : 200,
            "output": response["output"]["Items"][0]
        } 
    else:
        return {
            "output": None,
            "message" : "User has not registered for the event",
            "statusCode" : 401
        } 
    return response

def check_presentation_exists(email):
    response = scan("email", email)
    return response

def send_ses(email, first_name):
    template_data = '{ \"name\": \"' + first_name + '\" }' 
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

def put_item(email, presentation_title, presentation_description, guest_registration_id):
    presentation_id = str(uuid.uuid4())
 
    try:
        response = cfp_table.put_item(
            Item={
                    'presentationId': presentation_id,
                    'email': email,
                    'presentationTitle': presentation_title,
                    'presentationDescription': presentation_description,
                    'registrationId': guest_registration_id
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
                "output": presentation_id
                }

    return response


def handler(event, context):
    email = event['json']['email']
    presentation_title = event['json']['presentationTitle']
    presentation_description = event['json']['presentationDescription']

    guest_registration_response = check_guest_registration_exists(email) #check if user exists in db
    if guest_registration_response["statusCode"] == 200:                 #if 200 -> next 
        guest_registration = guest_registration_response["output"]       #guest_registration
        if guest_registration["isCanceled"] == False:                    #check if user canceled or no
            # presentation_response = check_presentation_exists(email)     #if user registered check if this user added pesentation yet
            first_name = guest_registration["firstName"]
            registrationId = guest_registration["registrationId"]
            # if len(presentation_response["Items"][0]) == 0:             #if len == 0 it means user not added presentaiton yet
            response = put_item(email, presentation_title, presentation_description, registrationId) 
            if response["statusCode"] == 200:
                response = send_ses(email, first_name) 
            # else:
            #     reponse = update_item(email, presentation_title, presentation_description, registrationId) 
            #     if response["statusCode"] == 200:
            #         response = send_ses(email, first_name) 
    else:
        response = guest_registration_response

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