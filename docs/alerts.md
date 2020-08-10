# Alerts

← [Home](../README.md)

Supported alert outputs include:

* [Email](alerts/email.md)
* [PagerDuty](alerts/pagerduty.md)
* [Slack](alerts/slack.md)

You can alert to any combination of the supported outputs, but only one alert can
be sent to each output type. For example, you can configure alerts to email and
Slack, but not multiple email addresses or Slack channels.

To add, change, or remove an alert output, reconfigure your `terraform.tfvars`
file and re-run `terraform apply`.

## Timeliness of Alerts

Be aware, alerts for honey token actions will not trigger instantly. Due to a
limitation in
[CloudTrail](https://aws.amazon.com/cloudtrail/faqs/#Event_payload.2C_timeliness.2C_and_delivery_frequency),
it will typically take about 15 minutes to receive an alert from your honey
token.

If you delete a honey token between the time it was used and when you would have
received an alert, you will not receive an alert at all.
