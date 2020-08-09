#!/usr/bin/env python3

"""
API authentication key management endpoints for the application API.
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
    if not isinstance(body.get('key_id', ""), str):
        raise Exception("Parameter 'key_id' must be of type string.")


def get_request(body):
    if body.get('key_id'):
        # Fetch single key
        key = app_common.APIKey(body['key_id'])

        if not key.exists:
            return api_common.build_response(404, {'error': "Key not found."})

        return api_common.build_response(200, {'key': key.get_dict()})

    # Fetch all keys
    keys = app_common.APIKey.get_all_keys()
    response = {'count': len(keys), 'keys': keys}
    return api_common.build_response(200, response)


def post_request(body):
    # Create key
    key = app_common.APIKey()
    key.generate()

    # Set key properties
    if body:
        key.set_expire_time(body.get('expire_time'))
        key.set_active(body.get('active'))
        key.set_admin(body.get('admin'))
        key.set_description(body.get('description'))

    # Write key to DB
    key.save()

    return api_common.build_response(200, {'key': {
        'key_id': key.key_id,
        'secret_id': key.secret_id,
        'expire_time': key.expire_time,
        'active': key.get_active(),
        'admin': key.get_admin(),
        'description': key.description
    }})


def patch_request(body):
    if 'key_id' not in body:
        return api_common.build_response(400, {'error': "Parameter 'key_id' is required."})

    key = app_common.APIKey(body['key_id'])
    if not key.exists:
        return api_common.build_response(404, {'error': "Key not found."})

    if 'expire_time' in body:
        key.set_expire_time(body['expire_time'])
    if 'active' in body:
        key.set_active(body['active'])
    if 'admin' in body:
        key.set_admin(body['admin'])
    if 'description' in body:
        key.set_description(body['description'])

    key.save()

    return api_common.build_response(200, {'key': key.get_dict()})


def delete_request(body):
    if 'key_id' not in body:
        return api_common.build_response(400, {'error': "Parameter 'key_id' is required."})

    key = app_common.APIKey(body['key_id'])
    if not key.exists:
        return api_common.build_response(404, {'error': "Key not found."})

    key.delete()
    return api_common.build_response(204)


def main(event, _context):
    request_method = event['requestContext']['http']['method']
    headers = event.get('headers', {})

    # Authentication w/ admin
    provision_key = headers.get('x-provision-key') if request_method == "POST" else None
    auth = api_common.authenticate_user(
        current_time, headers.get('x-key-id'), headers.get('x-secret-id'), provision_key)
    if not auth['auth']:
        return api_common.build_response(401, {'error': "Authentication failed."})
    if not auth['admin']:
        return api_common.build_response(403, {'error': "Access denied."})

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
