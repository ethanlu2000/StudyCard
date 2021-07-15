import os
import json
import boto3
from boto3.dynamodb.conditions import Key

table = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION']).Table(os.environ['DYNAMODB_TABLE_NAME'])

# For a given user (requires sign-in), update user metadata
def lambda_handler(event, context):

    print('event', event)
    cognito_user_id = event['requestContext']['authorizer']['claims']['sub']
    print('user id',cognito_user_id)

    body = json.loads(event["body"])

    try:
        update_user_data(cognito_user_id, body)
    except Exception as e:
        print(f"Error: Failed to update user data - {cognito_user_id}.")
        print(e)

    return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Origin': '*',
            },
            'body': '{"success" : true}'
        }

def update_user_data(cognito_user_id, body):

    response = table.update_item(
        Key={
            'PK': "USER#" + cognito_user_id,
            'SK': "USER#" + cognito_user_id
        },
        UpdateExpression="set 'User alias' = :u, 'User alias pinyin' = :p, 'User alias emoji' = :e, 'Character set preference' = :c",
        ExpressionAttributeValues={
            ':u': body['user_alias'],
            ':p': body['user_alias_pinyin'],
            ':e': body['user_alias_emoji'],
            ':c': body['character_set_preference']
        },
        ReturnValues="UPDATED_NEW"
    )

    return response