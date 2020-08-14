#!/usr/bin/env python3

"""
Common functions for the application API.
"""

import app_common
import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')


def authenticate_user(current_time, key_id, secret_id, provision_key=None):
    if provision_key:
        ssm = boto3.client('ssm')
        verify = ssm.get_parameter(
            Name="/{}/api/provision_key".format(os.environ['APP_NAME']),
            WithDecryption=True
        )['Parameter']['Value']
        if provision_key == verify:
            return {'auth': True, 'admin': True}

    if not key_id or not secret_id:
        return {'auth': False, 'admin': False}

    key = app_common.APIKey(key_id)

    # Fail if not exists, not active, or expired.
    if not key.exists or not key.active or (key.expire_time != 0 and key.expire_time <= current_time):
        return {'auth': False, 'admin': False}

    return {
        'auth': key.verify_secret(secret_id),
        'admin': key.get_admin()
    }


def check_request(event):
    if 'body' in event:
        if event.get('headers').get('content-type', None) != "application/json":
            raise Exception("Content-Type header must be application/json.")

        try:
            json.loads(event['body'])
        except json.decoder.JSONDecodeError:
            raise Exception("Could not decode json request.")


def build_response(status_code=200, body=None, headers=None):
    if body is None:
        body = {}

    default_headers = {
        'Content-Type': "application/json"
    }

    if isinstance(headers, dict):
        headers = {**default_headers, **headers}
    else:
        headers = default_headers

    return {
        'isBase64Encoded': False,
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(body, cls=app_common.DecimalEncoder)
    }
