import os
import boto3
from boto3.dynamodb.conditions import Key

import sys
sys.path.insert(0, '/opt')

table = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION']).Table(os.environ['DYNAMODB_TABLE_NAME'])

# For a given user (requires sign-in), return their metadata, subscribed lists, and the past two weeks of quizzes and sentences
def lambda_handler(event, context):

    cognito_user_id = event['requestContext']['authorizer']['claims']['sub']
    user_data = get_user_data(cognito_user_id)

    return

def get_user_data(user):

    response = table.query(
        KeyConditionExpression=Key('PK').eq(user)
    )
    print(response['Items'])
    return response['Items']