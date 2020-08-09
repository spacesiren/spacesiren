#!/usr/bin/env python3

"""
Honey event API.
"""

import app_common
import api_common
import json
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

current_time = int(time.time())


def validate_input(event):
    api_common.check_request(event)

    body = json.loads(event.get('body', "{}"))
    if not isinstance(body.get('event_id', ""), str):
        raise Exception("Parameter 'event_id' must be of type string.")
    if not isinstance(body.get('access_key_id', ""), str):
        raise Exception("Parameter 'access_key_id' must be of type string.")


def get_request(body):
    if not (body.get('event_id') or body.get('access_key_id')):
        return api_common.build_response(400, {'error': "Must specify 'event_id' or 'access_key_id'."})

    if body.get('event_id'):
        # Fetch single event
        event = app_common.Event(body['event_id'])

        if not event.exists:
            return api_common.build_response(404, {'error': "Event not found."})

        return api_common.build_response(200, {'event': event.get_dict()})

    # Fetch all events for token
    token = app_common.HoneyToken(body['access_key_id'])
    if not token.exists:
        return api_common.build_response(404, {'error': "Token not found."})

    events = app_common.Event.get_all_events_for_token(body['access_key_id'])
    response = {
        'count': len(events),
        'access_key_id': body['access_key_id'],
        'events': events
    }
    return api_common.build_response(200, response)


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
        'GET': get_request
    }

    # Response
    return methods[request_method](body)
