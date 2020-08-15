#!/usr/bin/env python3

"""
Send an alert to Pushover via the API.
"""

import alert_common
import boto3
import json
import logging
import os
import urllib3

pushover_api_url = "https://api.pushover.net/1/messages.json"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')


def get_ssm_parameter(name):
    return ssm.get_parameter(
        Name=name,
        WithDecryption=True
    )['Parameter']['Value']


def get_alert_body(message):
    return \
        "An AWS honey token was used. " + \
        "It may have been publicly exposed or its location compromised.\n\n" + \
        "<b>Access Key ID:</b> {}\n".format(message['event']['access_key_id']) + \
        "<b>Location:</b> {}\n".format(message['token']['location']) + \
        "<b>Description:</b> {}\n\n".format(message['token']['description']) + \
        "<b>Event Time:</b> {}\n".format(alert_common.parse_event_time(message['event']['event_time'])) + \
        "<b>Action:</b> {}\n".format(message['event']['event_name']) + \
        "<b>Region:</b> {}\n\n".format(message['event']['event_region']) + \
        "<b>IP Address:</b> {}\n".format(message['event']['source_ip_address']) + \
        "<b>User Agent:</b> {}\n".format(message['event']['user_agent'])


def main(event, _context):
    logger.info(json.dumps(event))

    pushover_keys = {
        'user': get_ssm_parameter(os.environ['SSM_PATH_PUSHOVER_USER_KEY']),
        'api': get_ssm_parameter(os.environ['SSM_PATH_PUSHOVER_API_KEY'])
    }

    for message in alert_common.parse_sns_event_records(event['Records']):
        logger.info(json.dumps(message))

        http = urllib3.PoolManager()
        headers = {'Content-Type': "application/json"}

        priority = int(os.environ['PUSHOVER_PRIORITY'])
        payload = {
            'token': pushover_keys['api'],
            'user': pushover_keys['user'],
            'message': get_alert_body(message),
            'html': 1,
            'priority': priority
        }
        if priority == 2:
            payload.update({
                'retry': os.environ['PUSHOVER_EMERGENCY_RETRY'],
                'expire': os.environ['PUSHOVER_EMERGENCY_EXPIRE']
            })

        body = json.dumps(payload).encode('utf-8')

        r = http.request('POST', pushover_api_url, body=body, headers=headers)
        logger.info(r.data.decode('utf-8'))

    return True
