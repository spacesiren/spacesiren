#!/usr/bin/env python3

"""
Parses all CloudTrail events, finds honey token actions,
and sends them to the honey token event task.
"""

import app_common
import task_common
import boto3
import gzip
import json
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
sns = boto3.client('sns')
current_time = int(time.time())


def download_cloudtrail_files(sns_messages):
    """
    Download CloudTrail files mentioned in SNS event.
    """
    files = []

    download_dir = '/tmp/cloudtrail'
    os.makedirs(download_dir, exist_ok=True)

    for message in sns_messages:
        for object_key in message['s3ObjectKey']:
            cloudtrail_file = "{}/{}".format(download_dir, object_key.split('/')[-1])
            s3.download_file(message['s3Bucket'], object_key, cloudtrail_file)
            files.append(cloudtrail_file)

    return files


def parse_cloudtrail_files(files):
    """
    Extract CloudTrail events that were performed with an IAM user key.
    """
    records = []

    for file in files:
        with gzip.open(file, 'rb') as f:
            cloudtrail_records = json.load(f)

        for record in cloudtrail_records['Records']:
            if 'accessKeyId' in record['userIdentity']:
                records.append(record)

    return records


def parse_user_events(cloudtrail_user_events):
    """
    Filter user events for those performed with honey tokens.
    Honey token must be marked active and have an expiration time of
    0 or greater than now.
    """
    honey_events = []

    for ct_event in cloudtrail_user_events:
        access_key_id = ct_event['userIdentity']['accessKeyId']
        token = app_common.HoneyToken(access_key_id)

        if token.exists and token.active and (token.expire_time == 0 or token.expire_time > current_time):
            honey_events.append({
                'honey_event': ct_event,
                'token': token.get_dict()
            })

    return honey_events


def honey_event_notify(honey_events):
    """
    Forward honey events to honey event SNS topic.
    """
    sns_topic_arn = os.environ['HONEY_EVENT_SNS_TOPIC_ARN']

    for honey_event in honey_events:
        logger.info("FOUND HONEY TOKEN EVENT!")
        logger.info(json.dumps(honey_event, cls=app_common.DecimalEncoder))
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps(honey_event, cls=app_common.DecimalEncoder)
        )


def main(event, _context):
    """
    Lambda handler function
    """
    logger.info("Start cloudtrail-event function.")
    logger.info(json.dumps(event))

    sns_messages = task_common.parse_sns_event_records(event['Records'])
    cloudtrail_files = download_cloudtrail_files(sns_messages)
    cloudtrail_user_events = parse_cloudtrail_files(cloudtrail_files)
    honey_events = parse_user_events(cloudtrail_user_events)
    honey_event_notify(honey_events)

    logger.info(json.dumps({'honey_events': honey_events}))
    logger.info("End cloudtrail-event function.")

    return {
        'status': "success",
        'num_honey_events': len(honey_events)
    }
