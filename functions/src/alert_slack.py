#!/usr/bin/env python3

"""
Send an alert to Slack via the API.
"""

import alert_common
import boto3
import json
import logging
import os
import urllib3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')


def main(event, _context):
    logger.info(json.dumps(event))

    slack_webhook_url = ssm.get_parameter(
        Name=os.environ['SSM_PATH_SLACK_WEBHOOK_URL'],
        WithDecryption=True
    )['Parameter']['Value']

    for message in alert_common.parse_sns_event_records(event['Records']):
        logger.info(json.dumps(message))

        http = urllib3.PoolManager()
        headers = {'Content-Type': "application/json"}

        body = json.dumps({
            'blocks': [
                {
                    'type': "section",
                    'text': {
                        'type': "mrkdwn",
                        'text': "*An AWS honey token was used.*\n" +
                                "It may have been publicly exposed or its location compromised."
                    }
                },
                {
                    'type': "divider"
                },
                {
                    'type': "section",
                    'text': {
                        'type': "mrkdwn",
                        'text': "*Access Key ID:* {}\n".format(message['event']['access_key_id']) +
                                "*Location:* {}\n".format(message['token']['location']) +
                                "*Description:* {}".format(message['token']['description'])
                    }
                },
                {
                    'type': "section",
                    'text': {
                        'type': "mrkdwn",
                        'text': "*Event Time:* {}\n"
                                .format(alert_common.parse_event_time(message['event']['event_time'])) +
                                "*Action:* {}\n".format(message['event']['event_name']) +
                                "*Region:* {}".format(message['event']['event_region'])
                    }
                },
                {
                    'type': "section",
                    'text': {
                        'type': "mrkdwn",
                        'text': "*IP Address:* {}\n".format(message['event']['source_ip_address']) +
                                "*User Agent:* {}".format(message['event']['user_agent'])
                    }
                },
                {
                    'type': "divider"
                }
            ]
        }).encode('utf-8')

        r = http.request('POST', slack_webhook_url, body=body, headers=headers)
        logger.info(r.data.decode('utf-8'))

    return True
