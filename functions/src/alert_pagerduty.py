#!/usr/bin/env python3

"""
Send an alert to PagerDuty via the API.
"""

import alert_common
import boto3
import json
import logging
import os
import urllib3

pagerduty_events_url = "https://events.pagerduty.com/v2/enqueue"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')


def main(event, _context):
    logger.info(json.dumps(event))

    pagerduty_integration_key = ssm.get_parameter(
        Name=os.environ['SSM_PATH_PAGERDUTY_INTEGRATION_KEY'],
        WithDecryption=True
    )['Parameter']['Value']

    for message in alert_common.parse_sns_event_records(event['Records']):
        logger.info(json.dumps(message))

        http = urllib3.PoolManager()
        headers = {'Content-Type': "application/json"}

        body = json.dumps({
            'routing_key': pagerduty_integration_key,
            'event_action': 'trigger',
            'payload': {
                'summary': "AWS Honey Token Alert: {}".format(message['event']['access_key_id']),
                'source': 'aws monitoring',
                'severity': 'error',
                'custom_details': {
                    'Access Key ID': message['event']['access_key_id'],
                    'Location': message['token']['location'],
                    'Description': message['token']['description'],
                    'Event Time': alert_common.parse_event_time(message['event']['event_time']),
                    'Action': message['event']['event_name'],
                    'Region': message['event']['event_region'],
                    'IP Address': message['event']['source_ip_address'],
                    'User Agent': message['event']['user_agent']
                }
            }
        }).encode('utf-8')

        r = http.request('POST', pagerduty_events_url, body=body, headers=headers)
        logger.info(r.data.decode('utf-8'))

    return True
