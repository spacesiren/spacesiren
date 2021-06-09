#!/usr/bin/env python3

"""
Common classes and functions for the whole application.
"""

import boto3
import base64
import decimal
import hashlib
import json
import logging
import os
import secrets
import time
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
iam = boto3.client('iam')
sts = boto3.client('sts')


class APIKey:
    table = dynamodb.Table("{}-api-keys".format(os.environ['APP_NAME']))

    @classmethod
    def get_all_keys(cls):
        response = cls.table.scan()
        items = response.get('Items', [])

        while response.get('LastEvaluatedKey') is not None:
            response = cls.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        keys = []
        for item in items:
            keys.append({
                'key_id': item['KeyID'],
                'create_time': int(item['CreateTime']),
                'expire_time': int(item['ExpireTime']),
                'active': bool(item['Active']),
                'admin': bool(item['Admin']),
                'description': item['Description']
            })

        return keys

    # This functionality was rejected in favor of maintaining expired keys
    # for restoration later.
    # @classmethod
    # def delete_expired_keys(cls, current_time):
    #     response = cls.table.scan(
    #         IndexName='ExpireTime',
    #         Select='ALL_PROJECTED_ATTRIBUTES',
    #         FilterExpression="ExpireTime <= :expire0 and ExpireTime <> :expire1",
    #         ExpressionAttributeValues={
    #             ':expire0': current_time,
    #             ':expire1': 0
    #         }
    #     )
    #
    #     for item in response.get('Items', []):
    #         token = APIKey(item['KeyID'])
    #         token.delete()

    def __init__(self, key_id=None):
        self.exists = False
        self.key_id = key_id
        self.secret_id = None
        self.secret_hash = None
        self.create_time = None
        self.expire_time = None
        self.active = None
        self.admin = None
        self.description = None

        if self.key_id:
            self.__read()

    def __read(self):
        response = self.table.get_item(Key={'KeyID': self.key_id})

        if 'Item' not in response:
            return

        item = response['Item']
        self.exists = True
        self.secret_hash = item.get('SecretHash', None)
        self.create_time = item.get('CreateTime', None)
        self.expire_time = item.get('ExpireTime', None)
        self.active = item.get('Active', None)
        self.admin = item.get('Admin', None)
        self.description = item.get('Description', None)

    def __write(self):
        self.table.put_item(Item={
            'KeyID': self.key_id,
            'SecretHash': self.secret_hash,
            'CreateTime': self.create_time,
            'ExpireTime': self.expire_time,
            'Active': self.active,
            'Admin': self.admin,
            'Description': self.description
        })
        self.exists = True

    def __delete(self):
        self.table.delete_item(Key={'KeyID': self.key_id})
        self.exists = False
        self.key_id = None
        self.secret_id = None
        self.secret_hash = None
        self.create_time = None
        self.expire_time = None
        self.active = None
        self.admin = None
        self.description = None

    def __hash_secret_id(self):
        salt = secrets.token_bytes(32)
        hash_bytes = hashlib.pbkdf2_hmac('sha256', self.secret_id.encode('utf-8'), salt, 100000)
        secret_hash = salt + hash_bytes
        self.secret_hash = base64.b64encode(secret_hash).decode('utf-8')

    def generate(self):
        # Check if key already exists. Very unlikely.
        while True:
            self.key_id = str(uuid.uuid4())
            check_key = APIKey(self.key_id)
            if check_key.exists:
                continue
            break

        # Populate the rest of the key's values.
        self.secret_id = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
        self.__hash_secret_id()
        self.create_time = int(time.time())
        self.set_expire_time()
        self.set_admin()
        self.set_description()

    def verify_secret(self, secret_id):
        if not self.exists:
            return False

        secret_hash = base64.b64decode(self.secret_hash.encode('utf-8'))
        salt = secret_hash[:32]
        hash_bytes = secret_hash[32:]
        verify_bytes = hashlib.pbkdf2_hmac('sha256', secret_id.encode('utf-8'), salt, 100000)
        return hash_bytes == verify_bytes

    def get_dict(self):
        return {
            'key_id': self.key_id,
            'create_time': int(self.create_time),
            'expire_time': int(self.expire_time),
            'active': self.get_active(),
            'admin': self.get_admin(),
            'description': self.description
        }

    def set_expire_time(self, expire_time=0):
        try:
            expire_time = max(0, int(expire_time))
        except (ValueError, TypeError):
            expire_time = 0

        self.expire_time = expire_time

    def get_active(self):
        return bool(self.active)

    def get_admin(self):
        return bool(self.admin)

    def set_active(self, active=True):
        if active is None:
            active = True

        self.active = bool(active)

    def set_admin(self, admin=False):
        self.admin = bool(admin)

    def set_description(self, description=""):
        if not description:
            description = ""

        self.description = str(description)[:100].strip()

    def save(self):
        self.expire_time = self.expire_time or 0
        self.active = self.active or False
        self.admin = self.admin or False
        self.description = self.description or ""
        self.__write()

    def delete(self):
        if self.exists:
            self.__delete()


class Event:
    table = dynamodb.Table("{}-events".format(os.environ['APP_NAME']))

    @classmethod
    def get_should_alert_next(cls, access_key_id, event_time, cooldown):
        if cooldown == 0:
            return True

        key_conditions = {
            'AccessKeyID': {
                'AttributeValueList': [access_key_id],
                'ComparisonOperator': 'EQ'
            }
        }
        if cooldown > -1:
            key_conditions.update({
                'EventTime': {
                    'AttributeValueList': [int(event_time - cooldown)],
                    'ComparisonOperator': 'GT'
                }
            })

        num_recent_events = cls.table.query(
            IndexName='AccessKeyID-EventTime',
            Select='COUNT',
            KeyConditions=key_conditions,
            QueryFilter={
                'Alerted': {
                    'AttributeValueList': [True],
                    'ComparisonOperator': 'EQ'
                }
            }
        )

        return num_recent_events['Count'] == 0

    @classmethod
    def get_all_events_for_token(cls, access_key_id):
        response = cls.table.query(
            IndexName='AccessKeyID-EventTime',
            Select='ALL_ATTRIBUTES',
            KeyConditions={'AccessKeyID': {
                'AttributeValueList': [access_key_id],
                'ComparisonOperator': 'EQ'
            }}
        )
        items = response.get('Items', [])

        while response.get('LastEvaluatedKey') is not None:
            response = cls.table.query(
                IndexName='AccessKeyID-EventTime',
                Select='ALL_ATTRIBUTES',
                KeyConditions={'AccessKeyID': {
                    'AttributeValueList': [access_key_id],
                    'ComparisonOperator': 'EQ'
                }}
            )
            items.extend(response.get('Items', []))

        events = []
        for item in items:
            events.append({
                'event_id': item['EventID'],
                'access_key_id': item['AccessKeyID'],
                'alerted': bool(item['Alerted']),
                'event_name': item['EventName'],
                'event_region': item['EventRegion'],
                'event_time': int(item['EventTime']),
                'request_parameters': item.get('RequestParameters'),
                'source_ip_address': item['SourceIPAddress'],
                'user_agent': item['UserAgent']
            })

        return events


    @classmethod
    def delete_events_for_token(cls, access_key_id):
        events = cls.table.query(
            IndexName='AccessKeyID-EventTime',
            Select='SPECIFIC_ATTRIBUTES',
            AttributesToGet=[
                'EventID'
            ],
            KeyConditions={'AccessKeyID': {
                'AttributeValueList': [access_key_id],
                'ComparisonOperator': 'EQ'
            }}
        )

        for item in events.get('Items', []):
            event = Event(item['EventID'])
            event.delete()

    def __init__(self, event_id=None):
        self.exists = False
        self.event_id = event_id
        self.access_key_id = None
        self.alerted = None
        self.event_name = None
        self.event_time = None
        self.event_region = None
        self.request_parameters = None
        self.source_ip_address = None
        self.user_agent = None

        if self.event_id:
            self.__read()

    def __read(self):
        response = self.table.get_item(Key={'EventID': self.event_id})

        if 'Item' not in response:
            return

        item = response['Item']
        self.exists = True
        self.access_key_id = item.get('AccessKeyID')
        self.alerted = item.get('Alerted')
        self.event_name = item.get('EventName')
        self.event_time = item.get('EventTime')
        self.event_region = item.get('EventRegion')
        self.request_parameters = item.get('RequestParameters')
        self.source_ip_address = item.get('SourceIPAddress')
        self.user_agent = item.get('UserAgent')

    def __write(self):
        self.table.put_item(Item={
            'EventID': self.event_id,
            'AccessKeyID': self.access_key_id,
            'Alerted': self.alerted,
            'EventName': self.event_name,
            'EventTime': self.event_time,
            'EventRegion': self.event_region,
            'RequestParameters': self.request_parameters,
            'SourceIPAddress': self.source_ip_address,
            'UserAgent': self.user_agent
        })
        self.exists = True

    def __delete(self):
        self.table.delete_item(Key={'EventID': self.event_id})
        self.exists = False
        self.event_id = None
        self.access_key_id = None
        self.alerted = None
        self.event_name = None
        self.event_time = None
        self.event_region = None
        self.request_parameters = None
        self.source_ip_address = None
        self.user_agent = None

    def get_dict(self):
        return {
            'event_id': self.event_id,
            'access_key_id': self.access_key_id,
            'alerted': bool(self.alerted),
            'event_name': self.event_name,
            'event_time': int(self.event_time),
            'event_region': self.event_region,
            'request_parameters': self.request_parameters,
            'source_ip_address': self.source_ip_address,
            'user_agent': self.user_agent,
        }

    def save(self):
        self.__write()

    def delete(self):
        if self.exists:
            self.__delete()


class Honey:

    def __init__(self):
        self.exists = False
        self.create_time = None
        self.expire_time = None
        self.active = None
        self.location = None
        self.description = None

    @classmethod
    def get_all_tokens(cls):
        pass

    def __read(self):
        pass

    def __write(self):
        pass

    def __delete(self):
        pass

    def generate(self):
        pass

    def get_dict(self):
        pass

    def set_expire_time(self, expire_time=0):
        try:
            expire_time = max(0, int(expire_time))
        except (ValueError, TypeError):
            expire_time = 0

        self.expire_time = expire_time

    def set_active(self, active=None):
        if active is None:
            active = True

        self.active = bool(active)

    def set_location(self, location=""):
        if not location:
            location = ""

        self.location = str(location)[:100].strip()

    def set_description(self, description=""):
        if not description:
            description = ""

        self.description = str(description)[:300].strip()

    def save(self):
        self.__write()

    def delete(self):
        pass

class HoneyToken(Honey):
    table = dynamodb.Table(f"{os.environ['APP_NAME']}-honey-tokens")

    def __init__(self, access_key_id=None):
        self.user = None
        self.access_key_id = access_key_id
        self.secret_access_key = None

        if access_key_id:
            self.__read()

        super().__init__()

    @classmethod
    def get_all_tokens(cls):
        response = cls.table.scan()
        items = response.get('Items', [])

        while response.get('LastEvaluatedKey') is not None:
            response = cls.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        tokens = []
        for item in items:
            tokens.append({
                'access_key_id': item['AccessKeyID'],
                'create_time': int(item['CreateTime']),
                'expire_time': int(item['ExpireTime']),
                'username': item['Username'],
                'secret_access_key': item['SecretAccessKey'],
                'active': bool(item['Active']),
                'location': item['Location'],
                'description': item['Description']
            })

        return tokens

    def __read(self):
        response = self.table.get_item(Key={'AccessKeyID': self.access_key_id})

        if 'Item' not in response:
            return

        item = response['Item']
        self.exists = True
        self.create_time = item.get('CreateTime', None)
        self.expire_time = item.get('ExpireTime', None)
        self.user = IAMUser(item.get('Username', None))
        self.secret_access_key = item.get('SecretAccessKey', None)
        self.active = item.get('Active', None)
        self.location = item.get('Location', None)
        self.description = item.get('Description', None)

    def __write(self):
        self.table.put_item(Item={
            'AccessKeyID': self.access_key_id,
            'CreateTime': self.create_time,
            'ExpireTime': self.expire_time,
            'Username': self.user.username,
            'SecretAccessKey': self.secret_access_key,
            'Active': self.active,
            'Location': self.location,
            'Description': self.description
        })
        self.exists = True

    def __delete(self):
        self.table.delete_item(Key={'AccessKeyID': self.access_key_id})
        self.exists = False
        self.access_key_id = None
        self.create_time = None
        self.expire_time = None
        self.user = None
        self.secret_access_key = None
        self.active = None
        self.location = None
        self.description = None

    def generate(self):
        # Create
        self.user = IAMUser.get_next_user()
        access_key = iam.create_access_key(UserName=self.user.username)

        try:
            self.user.increment_token_count()
        except Exception as e:
            iam.delete_access_key(UserName=self.user.username, AccessKeyId=access_key['AccessKey']['AccessKeyId'])
            raise e

        self.access_key_id = access_key['AccessKey']['AccessKeyId']
        self.secret_access_key = access_key['AccessKey']['SecretAccessKey']

        # Set attrs
        self.create_time = int(time.time())
        self.set_expire_time()
        self.set_active()
        self.set_location()
        self.set_description()

        self.__write()

    def get_dict(self):
        return {
            'access_key_id': self.access_key_id,
            'secret_access_key': self.secret_access_key,
            'create_time': int(self.create_time),
            'expire_time': int(self.expire_time),
            'user': self.user.get_dict(),
            'active': bool(self.active),
            'location': self.location,
            'description': self.description
        }

    def delete(self):
        if self.exists:
            # Delete real IAM access key and decrement user token count in database.
            iam.delete_access_key(UserName=self.user.username, AccessKeyId=self.access_key_id)
            self.user.decrement_token_count()

            # Scrub events table.
            Event.delete_events_for_token(self.access_key_id)

            self.__delete()

class HoneyResource(Honey):
    table = dynamodb.Table(f"{os.environ['APP_NAME']}-honey-resources")

    def __init__(self, resource_arn):
        self.resource_arn = resource_arn

        super().__init__()

    @classmethod
    def get_all_tokens(cls):
        response = cls.table.scan()
        items = response.get('Items', [])

        while response.get('LastEvaluatedKey') is not None:
            response = cls.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        tokens = []
        for item in items:
            tokens.append({
                'resource_arn': item['ResourceARN'],
                'create_time': int(item['CreateTime']),
                'expire_time': int(item['ExpireTime']),
                'active': bool(item['Active']),
                'location': item['Location'],
                'description': item['Description']
            })

        return tokens

    def __read(self):
        response = self.table.get_item(Key={'ResourceARN': self.resource_arn})

        if 'Item' not in response:
            return

        item = response['Item']
        self.exists = True
        self.create_time = item.get('CreateTime', None)
        self.expire_time = item.get('ExpireTime', None)
        self.active = item.get('Active', None)
        self.location = item.get('Location', None)
        self.description = item.get('Description', None)

    def __write(self):
        self.table.put_item(Item={
            'ResourceARN': self.resource_arn,
            'CreateTime': self.create_time,
            'ExpireTime': self.expire_time,
            'Active': self.active,
            'Location': self.location,
            'Description': self.description
        })
        self.exists = True

    def __delete(self):
        self.table.delete_item(Key={'ResourceARN': self.resource_arn})
        self.exists = False
        self.create_time = None
        self.expire_time = None
        self.active = None
        self.location = None
        self.description = None

    def generate(self):
        # Set attrs
        self.create_time = int(time.time())
        self.set_expire_time()
        self.set_active()
        self.set_location()
        self.set_description()

        self.__write()

    def get_dict(self):
        return {
            'resource_arn': self.resource_arn,
            'create_time': int(self.create_time),
            'expire_time': int(self.expire_time),
            'active': bool(self.active),
            'location': self.location,
            'description': self.description
        }

    def delete(self):
        if self.exists:

            # FIXME support resources in events
            # Scrub events table.
            Event.delete_events_for_token(self.access_key_id)

            self.__delete()

class IAMUser:
    table = dynamodb.Table("{}-iam-users".format(os.environ['APP_NAME']))
    group_name = "{}-honey-users".format(os.environ['APP_NAME'])

    @classmethod
    def get_next_user(cls):
        # Fetch or generate a user for use with a new token.
        response = cls.table.query(
            IndexName="NumTokens",
            KeyConditions={
                'NumTokens': {
                    'AttributeValueList': [1],
                    'ComparisonOperator': 'EQ'
                }
            },
            Limit=1
        )

        # If user exists, length will be 1.
        for item in response['Items']:
            return IAMUser(item['Username'])

        # No suitable user exists. Create new.
        new_user = IAMUser()
        new_user.generate()
        return new_user

    def __init__(self, username=None):
        self.exists = False
        self.username = username
        self.create_time = None
        self.account_id = None
        self.num_tokens = None

        if self.username:
            self.__read()

    def __read(self):
        response = self.table.get_item(
            Key={'Username': self.username},
            ConsistentRead=True
        )

        if 'Item' not in response:
            return

        item = response['Item']
        self.exists = True
        self.create_time = item.get('CreateTime', None)
        self.account_id = item.get('AccountID', None)
        self.num_tokens = item.get('NumTokens', None)

    def __write(self):
        self.table.put_item(Item={
            'Username': self.username,
            'CreateTime': self.create_time,
            'AccountID': self.account_id,
            'NumTokens': self.num_tokens
        })
        self.exists = True

    def __delete(self):
        self.table.delete_item(Key={'Username': self.username})
        self.exists = False
        self.username = None
        self.account_id = None
        self.num_tokens = None

    def generate(self):
        # Check if key already exists. Very unlikely.
        while True:
            self.username = str(uuid.uuid4())
            check_user = IAMUser(self.username)
            if check_user.exists:
                continue
            break

        self.create_time = int(time.time())
        self.account_id = sts.get_caller_identity()['Account']
        self.num_tokens = 0

        iam.create_user(
            UserName=self.username,
            Tags=[
                {'Key': "{}-honey-user".format(os.environ['APP_NAME']), 'Value': "true"}
            ]
        )
        iam.add_user_to_group(UserName=self.username, GroupName=self.group_name)

        self.__write()

    def get_dict(self):
        return {
            'username': self.username,
            'create_time': int(self.create_time),
            'account_id': self.account_id,
            'num_tokens': int(self.num_tokens)
        }

    def increment_token_count(self):
        if not self.exists:
            raise Exception("User does not exist when incrementing token count.")

        if self.num_tokens >= 2:
            raise Exception("Too many tokens for user '{}'".format(self.username))

        self.num_tokens += 1
        self.__write()

    def decrement_token_count(self):
        if not self.exists:
            raise Exception("User does not exist when decrementing token count.")

        self.num_tokens -= 1

        if self.num_tokens <= 0:
            self.delete()
        else:
            self.__write()

    def delete(self):
        if self.exists:
            if self.num_tokens > 0:
                raise Exception("Tried to delete user with honey tokens.")

            iam.remove_user_from_group(UserName=self.username, GroupName=self.group_name)
            iam.delete_user(UserName=self.username)

            self.__delete()


class DecimalEncoder(json.JSONEncoder):
    """
    Assists in converting Decimal objects to int/float for DynamoDB attributes.
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
