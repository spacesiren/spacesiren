# Getting Started

* [Alerts](alerts.md)
* [API Documentation](api.md)
* [Terraform Variables](tfvars.md)

Unfortunately, there is no "quick start". Please read and follow each step carefully.
I promise it'll be worth it or your money back.<sup>1</sup>

## Clone Repository

Clone this repository to your local machine.

```
$ git clone https://github.com/spacesiren/spacesiren.git 
```

## Terraform

Make sure you have Terraform >= 0.13 installed somewhere in your PATH.

```
$ terraform -v
```

## AWS Account

It is highly recommended that you use a dedicated AWS account for this application,
as you will be disseminating credentials tied to the account. The credentials should
not grant any privileges, but a separate account is still a good idea.

It is also recommended that you authenticate to the SpaceSiren account using an IAM
Role, as opposed to an IAM User or the root credentials. This can be easily done using
AWS Organizations, or you may make a new standalone account and create a cross-account
IAM Role to connect into it. While you may still use an IAM User or the root credentials,
IAM Users should be reserved only for honey tokens, and best practice dictates that the
root account be used as little as possible.

Once your new AWS account is set up, configure your local AWS CLI config using profile
name "**spacesiren**". It may look something like this:

```ini
# ~/.aws/config
[profile default]
[profile spacesiren]
source_profile = default
role_arn = arn:aws:iam::111222333444:role/OrganizationAccountAccessRole
region = us-east-1

# ~/.aws/credentials
[default]
aws_access_key_id = AKIAXXXXXXXXXXXXXXXX
aws_secret_access_key = YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
```

Once it's set up, ensure that you can authenticate to the new account.

```
$ aws sts get-caller-identity --profile spacesiren
```

The 12-digit account ID of your new SpaceSiren account should be in the response.

## DNS

You will need to have your own domain. If you do not have one, you will need to 
register a new one. If you are using an existing domain, you will need the ability
to manage DNS for it or contact someone who can.

1. In your SpaceSiren AWS account, go to Route 53 and create a new public hosted
   zone for this application. For example, if you own `example.com`, create a
   new subdomain zone for `spacesiren.example.com`. You may name the subdomain
   anything you wish. If you are registering a new domain, make a new hosted zone
   matching the name of your new domain.
2. **If you are using a subdomain**, create a new NS record in its parent zone for
   your subdomain and values assigned to you from the new Route 53 hosted zone.
3. **If you registered a new domain**, configure your domain's custom nameservers
   to match those given to you by the new Route 53 zone.
   
## S3 Buckets

SpaceSiren requires at least 2 S3 buckets to work: one for CloudTrail records and
the other for Lambda functions. A 3rd bucket is also recommended for storing your
Terraform states, which this guide will cover.

Create 3 new S3 buckets in the US East (N. Virginia) region. You may name them
anything you like. Enable object versioning, AES-256 (SSE-S3) encryption, and all
blocking of public access on each bucket. Take note of the names of your new
buckets. For example, your bucket names may look like this:

```
mycompany-spacesiren-cloudtrail
mycompany-spacesiren-functions
mycompany-spacesiren-terraform-states
```

## DynamoDB Table for Terraform

This step is optional, but recommended.

In your SpaceSiren account and region us-east-1, create a new DynamoDB table with
name "**spacesiren-terraform-lock**" and primary key "**LockID**" (string). The
rest of the options can be adjusted to your liking; you shouldn't need more than 1
provisioned capacity for each read and write. On-demand will also work and should
not incur any measurable cost.

## Configuration

**Switch to the `terraform/` directory for the Configuration and Run steps.**

### Terraform Backend

Copy the `terraform-local.tf.example` file to `terraform-local.tf` and replace
the value for `bucket` with the name of your Terraform states bucket.

### Terraform Variables

Copy the `terraform.tfvars.example` file to `terraform.tfvars`, and review and fill
each option.

Required variables include:

* `cloudtrail_bucket`: The name of your new CloudTrail bucket from the setup steps.
* `functions_bucket`: The name of your Lambda functions bucket.
* `dns_zone_name`: The name of your Route 53 hosted zone.

Optional variables you may also wish to configure are:

* `alert_cooldown`: How long (in seconds) after the first alert for a honey token
  you would like to suppress future notifications. 0 for no cooldown, and -1 for
  infinite cooldown (i.e., only one alert per honey token).
* `default_tags`: A map of tags to apply to all provisioned AWS resources.

Alert variables are covered below.

## Alerts

Alerts are optional, but a big part of what make SpaceSiren useful. This Getting
Started guide will only cover email alerts. Visit the [Alerts](alerts.md) page
for information on all supported alert types.

In your `terraform.tfvars` file, set the following options:

* `alert_email_from_user` to your preferred FROM address username. The domain
  will match what you set in `dns_zone_name`.
* `alert_email_to_address` to your preferred TO full email address. You will need
  to verify this address before receiving any alerts to it. You should
  automatically receive a verification email after SpaceSiren setup is complete.
  For now, continue on.
  
For example, with the following config...

```
dns_zone_name = "spacesiren.example.com"

alert_email_from_user  = "alerts"
alert_email_to_address = "security@example.com"
```

Alert email messages would come from `alerts@spacesiren.example.com` and be sent
to `security@example.com`.

## Run

Finally, apply the Terraform configuration.

```
$ terraform init
$ terraform apply
```

The apply shouldn't take long, but it may take up to a few minutes.

If the apply went well, setup of SpaceSiren is complete! At the end of the run
output, you will see your new API endpoint for creating tokens.

## Your First Honey Token

You can use your SpaceSiren API to create and manage tokens, but first you must
set up an authentication key.

### Authentication Key Pair

If you are starting fresh, there will be no authentication keys present. To
create your first key pair, you will need your Provision Key. In your SpaceSiren
AWS account, go to the
[SSM Parameter Store](https://console.aws.amazon.com/systems-manager/parameters?region=us-east-1)
and find the parameter named `/spacesiren/api/provision_key`. Show the value
and take note of it.

Using your preferred API client (such as Postman, Insomnia, or curl), create a
new **POST** request to your API endpoint as the destination and `/key` as the
path, like so:

```
https://api.spacesiren.example.com/key
```

Include the following request headers, replacing the value for `X-Provision-Key`
with your own from Parameter Store.

```http request
Content-Type: application/json
X-Provision-Key: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Set the request body type to **JSON** and include these options:

```json
{
  "admin": true,
  "description": "My first API key"
}
```

You may replace the description with anything you like, or omit it entirely.

Submit the request, and you should receive a response with the following
attributes:

```json
{
  "key": {
    "key_id": "59ee279b-941b-4312-89c4-35030caba89a",
    "secret_id": "LiNasGp5g8hgNo0GvebYnNyqLJ50bMqSLYe97jdjsWw=",
    "_etc": "etc."
  }
}
```

The values for `key_id` and `secret_id` comprise your authentication key pair.
Take note of them and keep at least the Secret ID secret. You will use them for
the next API call.

### Honey Token

Once you have your authentication key pair, it's time to create your first token.

Create a new HTTP **POST** request to your API endpoint with `/token` as the path,
like so:

```
https://api.spacesiren.example.com/token
```

Set the request headers again, but instead of using the Provision Key like last
time, use your authentication key pair.

```http request
Content-Type: application/json
X-Key-ID: 59ee279b-941b-4312-89c4-35030caba89a
X-Secret-ID: LiNasGp5g8hgNo0GvebYnNyqLJ50bMqSLYe97jdjsWw=
```

Make a **JSON** body with the following options:

```json
{
  "description": "My first honey token",
  "location": "Where no one should find it"
}
```

You may replace `description` and `location` with anything you like or omit them.

Submit the request, and you should receive a response with the following
attributes:

```json
{
  "access_key_id": "AKIARVLMFKK3C2D32XXS",
  "secret_access_key": "FkxwoYhRBccM3AXzX5G7T88ikKlZyooRhYefs4Dl",
  "_etc": "etc."
}
```

If you did, congratulations on creating your first honey token! SpaceSiren will
track these IAM User credentials and you will receive a notification to the alert
output(s) you've set up if they are ever used.

---

## Footnotes

1. Get it? Because it's free. I won't be able to reimburse your AWS costs, so
   contact AWS billing support for a refund.
