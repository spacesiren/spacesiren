# API Documentation

While SpaceSiren doesn't have a pretty frontend (yet), you can use the API to
create and manage tokens and authentication keys, along with viewing events
from honey tokens. You can interact with the API using your tool of choice,
such as Postman, Insomnia, or good ol'-fashioned curl.

## Authentication

Requests to the API are authenticated with a key pair, the elements of which
are passed in via the HTTP request headers. For example, your key pair headers
may look like this:

```
X-Key-ID: 203d2ee3-f503-4f2f-a034-66193fe4d48c
X-Secret-ID: uP1UaA6SYOLhQ1/N8U37rgV+znmON5prBrFy1KL4NtM=
```

The Key ID is a random UUID, and the Secret ID is a base64 encoded string of
32 bytes.

**To generate your first key pair, see the POST /key endpoint.**

## Request format

The body of all requests must be in JSON format, except for requests that do
not require a body. They must also have the appropriate Content-Type header
set:

```
Content-Type: application/json
```

# Endpoints

There are three main endpoints:

* `/key` for managing authentication keys
* `/token` for managing honey tokens
* `/event` for viewing honey token events

## Endpoint: /key

The `/key` endpoint manages authentication keys and supports all four "CRUD"
operations. 

**Admin required:** Yes

### POST /key

Create a new API key.

#### Provision Key

This endpoint accepts a special header:

```
X-Provision-Key: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Since SpaceSiren will initially have no keys after setup, you may use the
`X-Provision-Key` header to set up your first authentication key. The value for
the provision key can be found in
[SSM Parameter Store](https://console.aws.amazon.com/systems-manager/parameters/?region=us-east-1)
under `/spacesiren/api/provision_key` by default. Keep this key safe, as it grants
full access to your SpaceSiren instance.

#### Request Options

```json
{
  "active": true,
  "admin": false,
  "expire_time": 0,
  "description": ""
}
```

##### Required

*none*

##### Optional

* `active (bool)`: Marks the key as active or inactive. Only active keys may
  authenticate.
* `admin (bool)`: Grants administrative access to the key, which allows it to
  create and manage itself and other keys.
* `expire_time (int)`: Epoch timestamp of when the key should expire and no
  longer be able to authenticate. Expired keys are not deleted automatically;
  they must be manually deleted or they can be restored by setting a new
  expiration value.
* `description (str)`: Custom description.

#### Response

```json
{
  "key": {
    "key_id": "59ee279b-941b-4312-89c4-35030caba89a",
    "secret_id": "LiNasGp5g8hgNo0GvebYnNyqLJ50bMqSLYe97jdjsWw=",
    "expire_time": 0,
    "active": true,
    "admin": false,
    "description": ""
  }
}
```

* `key_id`: The Key ID of your new API key. Used in the `X-Key-ID` HTTP
  authentication header.
* `secret_id`: The Secret ID of your new API key. Used in the `X-Secret-ID`
  HTTP authentication header. **If you lose the secret, you will need to generate
  a new key.
  

### GET /key

Get information about one or all API key(s).

#### Request Options

```json
{
  "key_id": ""
}
```

##### Required

*none*

##### Optional

* `key_id (str)`: Include this option to get details about a single key.
  Omit or leave blank to fetch all keys. Returns 404 if given a key that
  does not exist.
  
#### Response

##### Single key
```json
{
  "key": {
    "key_id": "59ee279b-941b-4312-89c4-35030caba89a",
    "create_time": 1596695618,
    "expire_time": 0,
    "active": true,
    "admin": false,
    "description": ""
  }
}
```

##### All keys
```json
{
  "count": 1,
  "keys": [
    {
      "key_id": "59ee279b-941b-4312-89c4-35030caba89a",
      "secret_id": "LiNasGp5g8hgNo0GvebYnNyqLJ50bMqSLYe97jdjsWw=",
      "expire_time": 0,
      "active": true,
      "admin": false,
      "description": ""
    }
  ]
}
```

### PATCH /key

Modify an API key.

#### Request Options

```json
{
  "key_id": "59ee279b-941b-4312-89c4-35030caba89a",
  "active": true,
  "admin": false,
  "expire_time": 0,
  "description": ""
}
```

##### Required

* `key_id (str)`: The ID of the key to modify. Returns 404 if given a key that
  does not exist.
  
##### Optional

Missing attributes will not be modified.

* `active (bool)`: Marks the key as active or inactive. Only active keys may
  authenticate.
* `admin (bool)`: Grants administrative access to the key, which allows it to
  create and manage itself and other keys.
* `expire_time (int)`: Epoch timestamp of when the key should expire and no
  longer be able to authenticate. Expired keys are not deleted automatically;
  they must be manually deleted or they can be restored by setting a new
  expiration value.
* `description (str)`: Custom description.

#### Response

```json
{
  "key": {
    "key_id": "59ee279b-941b-4312-89c4-35030caba89a",
    "create_time": 1596695618,
    "expire_time": 0,
    "active": true,
    "admin": false,
    "description": ""
  }
}
```

### DELETE /key

Delete an API key.

#### Request Options

```json
{
  "key_id": "59ee279b-941b-4312-89c4-35030caba89a"
}
```

##### Required

* `key_id (str)`: The ID of the key to delete. Returns 404 if given a key that
  does not exist.
  
##### Optional

*none*

#### Response

None. Returns 204 on success or 404 if given a key that does not exist.

## Endpoint: /token

The `/token` endpoint manages honey tokens and supports all four "CRUD"
operations.

**Admin required:** No

### POST: /token

Create a new honey token.

#### Request Options

```json
{
  "active": true,
  "expire_time": 0,
  "location": "",
  "description": ""
}
```

##### Required

*none*

##### Optional

* `active (bool)`: Marks the token as active or inactive. Only active tokens will
  record events or trigger alerts.
* `expire_time (int)`: Epoch timestamp of when the token should expire and no
  longer be record events or trigger alerts. Expired tokens are not deleted
  automatically; they must be manually deleted or they can be restored by
  setting a new expiration value.
* `location (str)`: Custom location. Used to keep track of where the key is
  intended to be placed.
* `description (str)`: Custom description.

#### Response

```json
{
  "access_key_id": "AKIARVLMFKK3C2D32XXS",
  "secret_access_key": "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",
  "create_time": 1596944078,
  "expire_time": 0,
  "user": {
    "username": "8d5843ff-47af-4a7d-9d68-fee5553bf0da",
    "create_time": 1596944077,
    "account_id": "111222333444",
    "num_tokens": 1
  },
  "active": true,
  "location": "",
  "description": ""
}
```

* `access_key_id`: The AWS IAM Access Key ID of your new honey token.
* `secret_access_key`: The AWS IAM Secret Access Key of your new honey token.
  This value is recoverable if lost.
* `user`: Represents the IAM User where your token is stored. Not necessary,
  but perhaps helpful for troubleshooting database inconsistency.

### GET /token

Get information about one or all honey token(s).

#### Request Options

```json
{
  "access_key_id": "AKIARVLMFKK3C2D32XXS"
}
```

##### Required

*none*

##### Optional

* `access_key_id (str)`: Include this option to get details about a single honey
  token. Omit or leave blank to fetch all honey tokens. Returns 404 if given a 
  token that does not exist.
  
#### Response

##### Single Honey Token
```json
{
  "token": {
    "access_key_id": "AKIARVLMFKK3C2D32XXS",
    "secret_access_key": "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",
    "create_time": 1596944078,
    "expire_time": 0,
    "user": {
      "username": "8d5843ff-47af-4a7d-9d68-fee5553bf0da",
      "create_time": 1596944077,
      "account_id": "111222333444",
      "num_tokens": 1
    },
    "active": true,
    "location": "",
    "description": ""
  }
}
```

##### All Honey Tokens
```json
{
  "count": 1,
  "tokens": [
    {
      "access_key_id": "AKIARVLMFKK3C2D32XXS",
      "create_time": 1596944078,
      "expire_time": 0,
      "username": "8d5843ff-47af-4a7d-9d68-fee5553bf0da",
      "secret_access_key": "FkxwoYhRBccM3AXzX5G7T88ikKlZyooRhYefs4Dl",
      "active": true,
      "location": "",
      "description": ""
    }
  ]
}
```

* `username`: Name of the IAM User that the token belongs to. Not usually
  necessary unless troubleshooting database consistency.

### PATCH /token

Modify a honey token.

#### Request Options

```json
{
  "access_key_id": "AKIARVLMFKK3C2D32XXS",
  "active": true,
  "expire_time": 0,
  "location": "",
  "description": ""
}
```

##### Required

* `access_key_id (str)`: The Access Key ID of the token to modify. Returns 404 if
  given a key that does not exist.

##### Optional

* `active (bool)`: Marks the token as active or inactive. Only active tokens will
  record events or trigger alerts.
* `expire_time (int)`: Epoch timestamp of when the token should expire and no
  longer be record events or trigger alerts. Expired tokens are not deleted
  automatically; they must be manually deleted or they can be restored by
  setting a new expiration value.
* `location (str)`: Custom location. Used to keep track of where the key is
  intended to be placed.
* `description (str)`: Custom description.

#### Response

```json
{
  "key": {
    "access_key_id": "AKIARVLMFKK3C2D32XXS",
    "secret_access_key": "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",
    "create_time": 1596944078,
    "expire_time": 0,
    "user": {
      "username": "8d5843ff-47af-4a7d-9d68-fee5553bf0da",
      "create_time": 1596944077,
      "account_id": "111222333444",
      "num_tokens": 2
    },
    "active": true,
    "location": "",
    "description": ""
  }
}
```

* `user`: Represents the IAM User where your token is stored. Not necessary,
  but perhaps helpful for troubleshooting database inconsistency.

### DELETE /token

Delete a honey token.

#### Request Options

```json
{
  "access_key_id": "AKIARVLMFKK3C2D32XXS"
}
```

##### Required

* `access_key_id (str)`: The ID of the honey token to delete. Returns 404 if
  given a key that does not exist.
  
##### Optional

*none*

#### Response

None. Returns 204 on success or 404 if given a key that does not exist.

## Endpoint: /event

The `/event` endpoint gives information about requests attempted by honey tokens.

**Admin required:** No

### GET /event

Get information about a single event or all events for a honey token.

#### Request Options

```json
{
  "event_id": "8c90a152-00c2-44b1-9bce-758a32f7b02e",
  "access_key_id": "AKIARVLMFKK3C2D32XXS"
}
```

##### Required

* `event_id (str)`: The Event ID of a single event.

OR

* `access_key_id (str)`: The Access Key ID of a honey token to fetch all events
  for that token.
  
##### Optional

*none*

#### Response

##### Single Event

```json
{
  "event": {
    "event_id": "8c90a152-00c2-44b1-9bce-758a32f7b02e",
    "access_key_id": "AKIARVLMFKK3C2D32XXS",
    "alerted": true,
    "event_name": "GetCallerIdentity",
    "event_time": 1596928727,
    "event_region": "us-east-1",
    "request_parameters": null,
    "source_ip_address": "206.217.205.37",
    "user_agent": "aws-cli/1.18.105 Python/3.8.2 Linux/5.4.0-40-generic botocore/1.17.28"
  }
}
```

##### All Events for Honey Token

```json
{
  "count": 1,
  "access_key_id": "AKIARVLMFKK3C2D32XXS",
  "events": [
    {
      "event_id": "8c90a152-00c2-44b1-9bce-758a32f7b02e",
      "access_key_id": "AKIARVLMFKK3C2D32XXS",
      "alerted": true,
      "event_name": "GetCallerIdentity",
      "event_region": "us-east-1",
      "event_time": 1596928727,
      "request_parameters": null,
      "source_ip_address": "206.217.205.37",
      "user_agent": "aws-cli/1.18.105 Python/3.8.2 Linux/5.4.0-40-generic botocore/1.17.28"
    }
  ]
}
```

## Endpoint: /test-alert

The `/test-alert` endpoint fires a test alert to configured outputs.

**Admin required:** No

### POST /test-alert

Send a test alert.

#### Request Options

```json
{
  "description": "A token description"
}
```

##### Required

*none*
  
##### Optional

* `description (str)`: The description of the would-be honey token that triggered
  the alert. Helpful for describing your test alert to other recipients.

#### Response

```json
{
  "message": "Test alert sent."
}
```
