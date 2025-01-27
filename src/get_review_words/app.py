import os
import json
import boto3
from datetime import datetime
from datetime import timedelta
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

import vocab_list_service
import review_word_service

table = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION']).Table(os.environ['TABLE_NAME'])

all_lists = vocab_list_service.get_vocab_lists()

def lambda_handler(event,context):

  params = event.get('queryStringParameters') or {}
  list_id_param = params.get('list_id', None)
  date_range_param = params.get('date_range', None)

  review_words = review_word_service.get_review_words(list_id=list_id_param, date_range=date_range_param)

  # todays_date = format_date(datetime.today())

  # # Extract query string parameters
  # # Query string parameters should be a the list name (ex, HSKLevel1) and a number of days (ex, 7)
  # if 'queryStringParameters' in event and event['queryStringParameters'] is not None:

  #   # Set word list
  #   if 'list_id' in event['queryStringParameters']:
  #     list_id = event["queryStringParameters"]['list_id']

  #     # Set date range
  #     if 'date_range' in event["queryStringParameters"]:
  #       date_range = event["queryStringParameters"]['date_range']

  #       from_date = format_date(datetime.today() - timedelta(days=int(date_range)))

  #       # TODO Add error response if date range is longer than a certain quantity?

  #     # If no date param given, set to 90 days
  #     else:
  #       from_date = format_date(datetime.today() - timedelta(days=int(90)))

  #     items = pull_words_with_params(list_id, from_date, todays_date)

  # # If no params passed, get all lists words from the last 7 days
  # else:
  #   items = pull_words_no_params(todays_date)

  return {
          'statusCode': 200,
          'headers': {
              'Access-Control-Allow-Methods': 'GET,OPTIONS',
              # 'Access-Control-Allow-Origin': os.environ['DomainName'],
              'Access-Control-Allow-Origin': '*',
          },
          'body': json.dumps(review_words)
        }

# def pull_words_with_params(list_id, from_date, todays_date):

#   try:
#       response = table.query(
#         KeyConditionExpression=Key('PK').eq("LIST#" + list_id) & Key('SK').between("DATESENT#" + str(from_date),"DATESENT#" + str(todays_date))
#       )
#   except Exception as e:
#     print(e.response['Error']['Message'])
#     raise e
#   else:
#     words = response['Items']
#     print(json.dumps(words, indent=4))

#   return {list_id : words}

# def pull_words_no_params(todays_date):

#   completed_item_list = {}

#   from_date = format_date(datetime.today() - timedelta(days=int(7)))

#   for list_id in all_lists:
#     try:
#         response = table.query(
#           KeyConditionExpression=Key('PK').eq("LIST#" + list_id) & Key('SK').between("DATESENT#" + str(from_date),"DATESENT#" + str(todays_date))
#         )
#     except ClientError as e:
#       print(e.response['Error']['Message'])
#     else:
#       completed_item_list[list_id] = response['Items']

#   print(json.dumps(completed_item_list, indent=4))
#   return completed_item_list

# def format_date(date_object):

#   formatted_date = date_object.strftime('%Y-%m-%d')

#   return formatted_date