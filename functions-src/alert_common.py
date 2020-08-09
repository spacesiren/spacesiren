#!/usr/bin/env python3

"""
Common functions for alerting.
"""

import datetime
import json


def parse_sns_event_records(records):
    messages = []

    for record in records:
        messages.append(json.loads(record['Sns']['Message']))

    return messages


def parse_event_time(time):
    return datetime.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S UTC')
