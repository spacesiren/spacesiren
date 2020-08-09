#!/usr/bin/env python3

"""
Send an email alert using SES.
"""

import alert_common
import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses = boto3.client('ses')


def get_alert_text(message):
    return \
        "An AWS honey token was used. " + \
        "It may have been publicly exposed or its location compromised.\n\n" + \
        "Access Key ID: {}\n".format(message['event']['access_key_id']) + \
        "Location: {}\n".format(message['token']['location']) + \
        "Description: {}\n\n".format(message['token']['description']) + \
        "Event Time: {}\n".format(alert_common.parse_event_time(message['event']['event_time'])) + \
        "Action: {}\n".format(message['event']['event_name']) + \
        "Region: {}\n\n".format(message['event']['event_region']) + \
        "IP Address: {}\n".format(message['event']['source_ip_address']) + \
        "User Agent: {}\n".format(message['event']['user_agent'])


def get_alert_html(message):
    return \
        "<p>An AWS honey token was used. " + \
        "It may have been publicly exposed or its location compromised.</p>\n\n" + \
        "<p><b>Access Key ID:</b> {}<br>\n".format(message['event']['access_key_id']) + \
        "<b>Location:</b> {}<br>\n".format(message['token']['location']) + \
        "<b>Description:</b> {}</p>\n\n".format(message['token']['description']) + \
        "<p><b>Event Time:</b> {}<br>\n".format(alert_common.parse_event_time(message['event']['event_time'])) + \
        "<b>Action:</b> {}<br>\n".format(message['event']['event_name']) + \
        "<b>Region:</b> {}</p>\n\n".format(message['event']['event_region']) + \
        "<p><b>IP Address:</b> {}<br>\n".format(message['event']['source_ip_address']) + \
        "<b>User Agent:</b> {}</p>\n".format(message['event']['user_agent'])


def main(event, _context):
    logger.info(json.dumps(event))

    for message in alert_common.parse_sns_event_records(event['Records']):
        logger.info(json.dumps(message))
        ses.send_email(
            Source="{} <{}>".format(
                os.environ['ALERT_EMAIL_FROM_DISPLAY'],
                os.environ['ALERT_EMAIL_FROM_ADDRESS']
            ),
            Destination={
                'ToAddresses': [
                    os.environ['ALERT_EMAIL_TO_ADDRESS']
                ]
            },
            Message={
                'Subject': {
                    'Data': 'AWS Honey Token Alert',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': get_alert_text(message),
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': get_alert_html(message),
                        'Charset': 'UTF-8'
                    }
                }
            }
        )

    return True
