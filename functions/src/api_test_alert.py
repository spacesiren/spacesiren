#!/usr/bin/env python3

"""
Test honey event API.
"""

import app_common
import api_common
import boto3
import json
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

current_time = int(time.time())

sns = boto3.client('sns')


def validate_input(event):
    api_common.check_request(event)


def get_test_message(description):
    return {
        'event': {
            'event_id': "00000000-0000-0000-0000-000000000000",
            'access_key_id': "AKIATESTACCESSKEYID0",
            'alerted': True,
            'event_name': "TestAlert",
            'event_time': current_time,
            'event_region': "us-east-1",
            'request_parameters': None,
            'source_ip_address': "127.0.0.1",
            'user_agent': "test-alert-api-function"
        },
        'token': {
            "access_key_id": "AKIATESTACCESSKEYID0",
            "secret_access_key": "0000000000000000000000000000000000000000",
            "create_time": current_time,
            "expire_time": 0,
            "user": {
                "username": "00000000-0000-0000-0000-000000000000",
                "create_time": current_time,
                "account_id": "000000000000",
                "num_tokens": 0
            },
            "active": True,
            "location": "Nowhere",
            "description": description
        }
    }


def post_request(body):
    test_message = get_test_message(body.get('description', "A token description"))

    try:
        sns.publish(
            TopicArn=os.environ['HONEY_ALERT_SNS_TOPIC_ARN'],
            Message=json.dumps(test_message)
        )
    except Exception as e:
        logger.info("Test alert failed: {}".format(e))
        api_common.build_response(500, {'error': "Could not send test alert."})

    return api_common.build_response(200, {'message': "Test alert sent."})


def main(event, _context):
    request_method = event['requestContext']['http']['method']
    headers = event.get('headers', {})

    # Authentication
    auth = api_common.authenticate_user(
        current_time, headers.get('x-key-id'), headers.get('x-secret-id'))
    if not auth['auth']:
        return api_common.build_response(401, {'error': "Authentication failed."})

    # Input validation
    try:
        validate_input(event)
    except Exception as e:
        return api_common.build_response(400, {'error': str(e)})

    body = json.loads(event.get('body', "{}"))

    # Routing
    methods = {
        'POST': post_request
    }

    # Response
    return methods[request_method](body)
