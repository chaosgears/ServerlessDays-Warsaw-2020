import boto3
import os
import json
import csv 
import uuid
import logging
from botocore.exceptions import ClientError
from botocore.exceptions import ParamValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
env = os.environ.copy()
region = os.environ['REGION']
dynamodb = boto3.resource('dynamodb')
public_bucket = os.environ['BUCKET_NAME']
s3 = boto3.client('s3', region_name = region) 
guest_registration_table_name = os.environ['TABLE_NAME']
guest_registration_table = dynamodb.Table(guest_registration_table_name)

def convert_json_to_csv(json_file):
    data_file = open('/tmp/guests_list.csv', 'w') 
    csv_writer = csv.writer(data_file) # create the csv writer object 
      
    # Counter variable used for writing  
    # headers to the CSV file 
    count = 0
    for item in json_file: 
        if count == 0: 
            header = item.keys() # Writing headers of CSV file 
            csv_writer.writerow(header) 
            count += 1
    
        csv_writer.writerow(item.values()) # Writing data of CSV file 
      
    data_file.close() 
    s3.upload_file(data_file, public_bucket, data_file)

def handler(event, context):
    try:
        response = guest_registration_table.scan()
        data = response['Items']
        print(data)
    except ClientError as err:
        logger.critical("----Client error: {0}".format(err))
        logger.critical(
            "----HTTP code: {0}".format(err.response['ResponseMetadata']['HTTPStatusCode']))
        items = None
        message = err.response['Error']['Message']
        statusCode = err.response['ResponseMetadata']['HTTPStatusCode']
    else:
        items = data
        message = "Success"
        statusCode = 200

    convert_json_to_csv(data)
    
    response = {
        "statusCode": statusCode,
        "message": message,
        "output": items,        
        "headers": {
            "Content-Type": 'application/json',
            "X-Requested-With": '*',
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with,x-correlation-id,x-session-id',
            "Access-Control-Allow-Origin": '*',
            "Access-Control-Allow-Methods": 'POST,GET,OPTIONS'
        }
    }
    
    return response