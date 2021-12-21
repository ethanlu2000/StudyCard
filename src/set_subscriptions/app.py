import os
import json
import boto3
import datetime

import user_service

# region_name specified in order to mock in unit tests
cognito_client = boto3.client('cognito-idp', region_name = 'us-east-1')
table = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION']).Table(os.environ['DYNAMODB_TABLE_NAME'])

# Set subscriptions and create user if none exists yet
def lambda_handler(event, context):
    print(event)

    event_body = json.loads(event["body"])
    date = str(datetime.datetime.now().isoformat())

    error_message = {
        'statusCode': 502,
        'headers': {
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Origin': '*',
        },
        'body': '{"success" : false}'
    }

    if event_body['cognito_id'] == "":
        try:
            user_cognito_id = look_up_cognito_id(event_body)
        except Exception as e:
            print(f'Failed to find user Cognito ID - {event_body}, {e} ')
            return error_message
        event_body['cognito_id'] = user_cognito_id

    try:
        create_user(date, event_body['cognito_id'], event_body['email'], event_body['character_set_preference'])
    except Exception as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            # User already exists, skip
            print(f"User already exists- {event_body['email'][5:]}.")
            pass
        else: 
            print(f"Error: Failed to create user - {event_body['email'][5:]}, {event_body['cognito_id']}.")
            print(e)
            return error_message

    # Get a list of ids for all lists the user is currently subscribed to
    user_data = user_service.get_user_data(event_body['cognito_id'])
    print(user_data['user_data'])
    current_user_lists = user_data['lists']
    if user_data['lists']:
        for list in current_user_lists:
            list['unique_id'] = list['list_id'] + "#" + list['character_set'].upper()

    # API call will pass all of the users current lists
    # It will call subscribe for all lists and do nothing (ConditionExpression = "attribute_not_exists(PK)")
    # if the subscription is already stored
    # It will check if there are any existing lists not in the new list and it will unsubscribe
    new_list_ids = []
    for list in event_body['lists']:
        new_list_ids.append(list['list_id'] + "#" + list['character_set'].upper())


    # TODO: Currently making an API call per update. Batch updates?
    for list in event_body['lists']:
        try:
            subscribe(date, event_body['cognito_id'], list)
            print(f"sub {list['list_id']}, {list['character_set']}")
        except Exception as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                # Subscription already exists, skip
                print(f"Subcription already exists- {event_body['email'][5:]}, {list['list_id']}.")
                pass
            else: 
                print(f"Error: Failed to subscribe user - {event_body['email'][5:]}, {list['list_id']}.")
                print(e)
                return error_message
    # does existing list check for simplified/traditional?
    for existing_list in current_user_lists:
        if existing_list['unique_id'] not in new_list_ids and existing_list['status'] == "subscribed":
            try:
                unsubscribe(date, event_body['cognito_id'], existing_list)
                print(f"unsub, {existing_list['unique_id']}")
            except Exception as e:
                print(f"Error: Failed to unsubscribe user - {event_body['email'][5:]}, {existing_list['list_id']}.")
                print(e)
                return error_message

    return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Origin': '*',
            },
            'body': '{"success" : true}'
        }

# Write new contact to Dynamo if it doesn't already exist
def create_user(date, cognito_id, email_address, character_set_preference):

    response = table.put_item(
        Item = {
                'PK': "USER#" + cognito_id,
                'SK': "USER#" + cognito_id,
                'Email address': email_address,
                'Date created': date,
                'Last login': date,
                'Character set preference': character_set_preference,
                'User alias': "Not set",
                'User alias pinyin': "Not set",
                'User alias emoji': "Not set",
                'GSI1PK': "USER",
                'GSI1SK': "USER#" + cognito_id
            },
            ConditionExpression = "attribute_not_exists(PK)"
        )
    return response

def subscribe(date, cognito_id, list_data):

    # PutItem will overwrite an existing item with the same key
    response = table.put_item(
        Item={
                'PK': "USER#" + cognito_id,
                'SK': "LIST#" + list_data['list_id'] + "#" + list_data['character_set'].upper(),
                'List name': list_data['list_name'],
                'Date subscribed': date,
                'Status': 'subscribed',
                'Character set': list_data['character_set'],
                'GSI1PK': "USER",
                'GSI1SK': "USER#" + cognito_id + "#LIST#" + list_data['list_id'] + "#" + list_data['character_set'].upper()
        }
    )

    return response

def unsubscribe(date, cognito_id, list_data):

    response = table.update_item(
        Key = {
            "PK": "USER#" + cognito_id,
            "SK": "LIST#" + list_data['list_id'] + "#" + list_data['character_set'].upper()
        },
        UpdateExpression = "set #s = :status, #d = :date",
        ExpressionAttributeValues = {
            ":status": "unsubscribed",
            ":date": date
        },
        ExpressionAttributeNames = {
            "#s": "Status",
            "#d": "Date unsubscribed"
        },
        ReturnValues = "UPDATED_NEW"
        )

    return response

def look_up_cognito_id(event_body):
    print('looking up cognito id...', event_body)
    try:
        response = cognito_client.admin_get_user(
            UserPoolId=os.environ['USER_POOL_ID'],
            Username=event_body['email']
        )
    except Exception as e:
        if e.response['Error']['Code'] == "UserNotFoundException":
            print(f'Error retrieving Cognito Id: user not found for email {event_body["email"]}')
            raise
        else:
            print(f'Error retrieving Cognito Id for user {event_body["email"]}')
            raise

    return response['Username']
