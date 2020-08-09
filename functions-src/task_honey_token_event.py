#!/usr/bin/env python3

"""
Notified when a honey token event occurs, collects information
about the event and associated token, and forwards it to the alert
functions.
"""

import app_common
import task_common
import boto3
import dateutil.parser
import json
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

current_time = int(time.time())
cooldown = int(os.environ['ALERT_COOLDOWN'])

sns = boto3.client('sns')


def record_honey_token_event(message):
    honey_event = app_common.Event()
    honey_event.event_id = message['honey_event']['eventID']
    honey_event.access_key_id = message['token']['access_key_id']
    honey_event.event_time = int(dateutil.parser.parse(message['honey_event']['eventTime']).strftime('%s'))
    honey_event.event_name = message['honey_event']['eventName']
    honey_event.event_region = message['honey_event']['awsRegion']
    honey_event.request_parameters = message['honey_event']['requestParameters']
    honey_event.source_ip_address = message['honey_event']['sourceIPAddress']
    honey_event.user_agent = message['honey_event']['userAgent']

    honey_event.alerted = app_common.Event.get_should_alert_next(
        honey_event.access_key_id,
        honey_event.event_time,
        cooldown
    )

    honey_event.save()
    return honey_event.get_dict()


def main(event, _context):
    logger.info(json.dumps(event))
    sns_messages = task_common.parse_sns_event_records(event['Records'])

    for message in sns_messages:
        logger.info(json.dumps(message))
        recorded_event = record_honey_token_event(message)

        if recorded_event['alerted']:
            logger.info("SENDING ALERT")
            sns.publish(
                TopicArn=os.environ['HONEY_ALERT_SNS_TOPIC_ARN'],
                Message=json.dumps({
                    'event': recorded_event,
                    'token': message['token']
                }, cls=app_common.DecimalEncoder)
            )

    return True
