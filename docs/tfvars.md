# Terraform Variables

The `terraform.tfvars` file contains SpaceSiren's configuration.

## Applying

To apply any changes you make to the configuration, you will need to re-run
Terraform apply:

```
$ terraform init
$ terraform apply
```

## Required Variables

These variables are required for SpaceSiren to run. They contain information
unique to your SpaceSiren instance.

| Variable            | Type   | Description |
|---------------------|--------|-----------------------------------------------------------|
| `cloudtrail_bucket` | string | The name of the S3 bucket used for CloudTrail delivery.   |
| `functions_bucket`  | string | The name of the S3 bucket used to store Lambda functions. |
| `dns_zone_name`     | string | The name of the DNS (sub)domain assigned to SpaceSiren. It must be properly delegated from the parent zone or registrar. Fake or internal-only DNS zones are not supported. |

## Alert Variables

Alert variables are **not required**, but they may be required for their group if you
decide to use a specific alert type. For example, `alert_email_to_address` is not
required if you do not wish to use email alerting, but it becomes required if
you do wish to have email alerts.

To enable or disable a specific alert type, set or unset its required variables.

### Email

| Variable                        | Type   | Required? | Default           | Description |
|---------------------------------|--------|-----------|-------------------|-------------|
| `alert_email_to_address`        | string | Yes       | -                 | The full TO email address of where alerts should be sent. |
| `alert_email_from_user`         | string | Yes       | -                 | The username of the FROM address, NOT the full email address. The domain of the address will be set by your `dns_zone_name` variable. |
| `alert_email_from_display`      | string | No        | SpaceSiren Alerts | The display name of the FROM address. |
| `alert_email_verify_to_address` | bool   | No        | true              | Attempt SES verification of the TO address. This will be mandatory for AWS accounts that have not been granted production SES access by AWS support. |

### PagerDuty

| Variable                          | Type   | Required? | Default | Description |
|-----------------------------------|--------|-----------|---------|-------------|
| `alert_pagerduty_integration_key` | string | Yes       | -       | Your PagerDuty integration key. |

### Slack

| Variable                   | Type   | Required? | Default | Description |
|----------------------------|--------|-----------|---------|-------------|
| `alert_slack_webhoook_url` | string | Yes       | -       | Your Slack Incoming Webhook URL. |

### Pushover

| Variable                          | Type   | Required? | Default | Description |
|-----------------------------------|--------|-----------|---------|-------------|
| `alert_pushover_user_key`         | string | Yes       | -       | Your Pushover user or group key. |
| `alert_pushover_api_key`          | string | Yes       | -       | Your Pushover API (application) key. |
| `alert_pushover_priority`         | string | No        | 0       | The priority of the Pushover notification. -2 is the lowest and 2 is the highest. |
| `alert_pushover_emergency_retry`  | string | No        | 300     | If priority=2, how often in seconds to retry notification. |
| `alert_pushover_emergency_expire` | string | Yes       | 10800   | If priority=2, after how long in seconds to stop retrying. |

## Optional Variables

These optional variables may be configured if you would like to tweak your
SpaceSiren installation.

| Variable                 | Type        | Default    | Description |
|--------------------------|-------------|------------|-------------|
| `alert_cooldown`         | number      | 1800       | The amount of time in seconds after an alert is triggered for a honey token to suppress future alerts for that token. Defaults to 30 minutes. Set 0 to alert on all events, or -1 to alert only once per token. |
| `api_burst_limit`        | number      | 10         | Your API Gateway burst limit. Read more in the [AWS API Gateway documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html) |
| `api_rate_limit`         | number      | 10         | Your API Gateway rate limit.
| `app_name`               | string      | spacesiren | The app name serves as a prefix for all resources created. Could be used to manage multiple SpaceSiren instances in a single AWS account, although it is not tested or supported. |
| `cloudwatch_expire_days` | number      | 30         | The retention period for CloudWatch Log Groups, which mostly serve as debug log outputs for Lambda functions. |
| `default_tags`           | map(string) | `{}`       | A default set of tags to apply to resources created by SpaceSiren. Reserved tags include `Name` and `<app_name>-honey-user>`. Compliance with AWS Organizations Tag Policies is not yet supported. |
