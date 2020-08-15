# Pushover Alerts

← [Home](../../README.md) / [Alerts](../alerts.md)

You can configure SpaceSiren to send alerts to your mobile device or desktop
client via [Pushover](https://pushover.net).

## Setup

You will need a Pushover account and a license for at least one device type.
Once you create your account, you will receive your **user key**.

Next, create a new application. Name and describe it however you like and take
note of the **API key**.

## Configure

In your `terraform.tfvars` file, add the following lines, replacing the values
of the keys with your own:

```
alert_pushover_user_key = "uol4oib2ohseo7loo3choocaefohso"
alert_pushover_api_key  = "aicah8eikough3uiraa9oocohziel1"
```

You may substitute a Pushover group key for the user key to notify a group of
Pushover users.

### Priority

Pushover supports prioritization for notifications. For more information, refer
to the [Pushover API documentation](https://pushover.net/api#priority).

You may set notification priority between -2 (lowest) and 2 (highest). The
default value is 0 for normal priority.

```
alert_pushover_priority = 0
```

If you set the priority to 2, the recipient will be forced to acknowledge the
notification and there will be additional options available to you.

```
alert_pushover_emergency_retry  = 300
alert_pushover_emergency_expire = 10800
```

Each numeric value above is time in seconds. The first is the retry interval for
how often the recipient should be notified again for the same alert, and the
second is how long after the first alert to stop retrying. The default values are
shown, which retry notification every 5 minutes for 3 hours.

## Apply

Re-run Terraform to apply your changes:

```
$ terraform init
$ terraform apply
```
