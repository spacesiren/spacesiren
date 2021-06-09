#!/usr/bin/env python3

"""
Honey resource management endpoints for the application API.
"""

import app_common
import api_common
import json
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

current_time = int(time.time())


# FIXME there's a lot of duplicated code with api_token.py, should use class inheritance

def validate_input(event):
    api_common.check_request(event)

    body = json.loads(event.get('body', "{}"))
    if not isinstance(body.get('resource_arn', ""), str):
        raise Exception("Parameter 'resource_arn' must be of type string.")


def get_request(body):
    if body.get('resource_arn'):
        # Fetch single token
        token = app_common.HoneyResource(body['resource_arn'])

        if not token.exists:
            return api_common.build_response(404, {'error': "Honey resource not found."})

        return api_common.build_response(200, {'token': token.get_dict()})

    # Fetch all tokens
    tokens = app_common.HoneyResource.get_all_tokens()
    response = {'count': len(tokens), 'tokens': tokens}
    return api_common.build_response(200, response)


def post_request(body):
    if 'resource_arn' not in body:
        return api_common.build_response(400, {'error': "Parameter 'resource_arn' is required."})
    
    token = app_common.HoneyResource(body.get('resource_arn'))

    try:
        token.generate()
    except Exception as e:
        return api_common.build_response(429, {'error': str(e)})

    if body:
        token.set_expire_time(body.get('expire_time'))
        token.set_active(body.get('active'))
        token.set_location(body.get('location'))
        token.set_description(body.get('description'))

    token.save()

    return api_common.build_response(200, token.get_dict())


def patch_request(body):
    if 'resource_arn' not in body:
        return api_common.build_response(400, {'error': "Parameter 'resource_arn' is required."})

    token = app_common.HoneyResource(body['resource_arn'])
    if not token.exists:
        return api_common.build_response(404, {'error': "Honey resource not found."})

    if 'expire_time' in body:
        token.set_expire_time(body['expire_time'])
    if 'active' in body:
        token.set_active(body['active'])
    if 'location' in body:
        token.set_location(body['location'])
    if 'description' in body:
        token.set_description(body['description'])

    token.save()

    return api_common.build_response(200, {'key': token.get_dict()})


def delete_request(body):
    if 'resource_arn' not in body:
        return api_common.build_response(400, {'error': "Parameter 'resource_arn' is required."})

    token = app_common.HoneyResource(body['resource_arn'])
    if not token.exists:
        return api_common.build_response(404, {'error': "Honey resource not found."})

    token.delete()
    return api_common.build_response(204)


def main(event, _context):
    request_method = event['requestContext']['http']['method']
    headers = event.get('headers', {})

    # Authentication
    auth = api_common.authenticate_user(current_time, headers.get('x-key-id'), headers.get('x-secret-id'))
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
        'GET': get_request,
        'POST': post_request,
        'PATCH': patch_request,
        'DELETE': delete_request,
    }

    # Response
    return methods[request_method](body)
