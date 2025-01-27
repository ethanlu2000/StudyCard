import os
import json
import boto3
from boto3.dynamodb.conditions import Key

table = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION']).Table(os.environ['TABLE_NAME'])

# Create or update daily practice sentences
def lambda_handler(event, context):
    print(event)
    cognito_id = event['requestContext']['authorizer']['claims']['sub']
    print('user id, ',cognito_id)

    error_message = {
        'statusCode': 502,
        'headers': {
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
            'Access-Control-Allow-Origin': '*',
        },
        'body': '{"success" : false}'
    }

    try:
        sentences_response = pull_user_sentences(cognito_id)
    except Exception as e:
        print(f"Error: Failed to get user sentences.")
        print(e)
        return error_message
    
    user_sentences = format_user_sentences(sentences_response)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(user_sentences)
    }

def pull_user_sentences(congito_id):

    user_key = "USER#" + congito_id

    response = table.query(
        KeyConditionExpression=Key('PK').eq(user_key) & Key('SK').begins_with('SENTENCE') 
    )
    print('dynamo response ', response['Items'])
    return response['Items']

def format_user_sentences(sentences_response):

    user_sentences = { "sentences" : [] }
    for item in sentences_response:
        sentence_dict = {}

        # sentence_dict['cognito_id'] = item['PK'][5:]
        sentence_dict['sentence_id'] = item['SK'][9:]
        sentence_dict['sentence'] = item['Sentence']
        sentence_dict['character_set'] = item['Character set']
        sentence_dict['date_created'] = item['Date created']

        user_sentences['sentences'].append(sentence_dict)

    return user_sentences