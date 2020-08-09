#!/usr/bin/env python3

"""
Common functions for event tasks.
"""

import json


def parse_sns_event_records(records):
    messages = []

    for record in records:
        messages.append(json.loads(record['Sns']['Message']))

    return messages
