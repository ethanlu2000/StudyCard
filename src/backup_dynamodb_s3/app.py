import os
import json
import boto3
from datetime import datetime

s3 = boto3.resource('s3')
bucket = s3.Bucket(os.environ['BACKUPS_BUCKET_NAME'])

# region_name specified in order to mock in unit tests
dynamo_client = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
table = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION']).Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):

    all_contacts_data = scan_contacts_table()

    todays_date = format_date(datetime.today())

    data_rows = convert_to_rows(all_contacts_data, todays_date)

    response = write_to_s3(data_rows, todays_date)

def scan_contacts_table():

    # Loop through contacts in Dynamo
    results = table.scan(
        Select = "ALL_ATTRIBUTES"
    )

    all_contacts = results['Items']

    return all_contacts

def convert_to_rows(all_contacts_data, todays_date):

    data_rows = []

    # append today's date to each item as date of data pull
    for item in all_contacts_data:
        item['Reporting date'] = todays_date
        data_rows.append(item)

    return data_rows

def write_to_s3(data_rows, todays_date):
    
    response = bucket.put_object(
        Body = json.dumps(data_rows).encode('UTF-8'),
        Key = f'{todays_date}.json'
    )

    return response

def format_date(date_object):

    formatted_date = date_object.strftime('%Y-%m-%d')

    return formatted_date