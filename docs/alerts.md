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
