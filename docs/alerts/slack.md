# Slack Alerts

← [Home](../../README.md) / [Alerts](../alerts.md)

> ![PagerDuty alert](../screenshots/alert-slack.png)

You can configure SpaceSiren to send alerts to an existing Slack channel using an
Incoming Webhook.

Create a new Incoming Webhook in your Slack workspace's app directory and set the
webhook variable in your `terraform.tfvars` file:

```
alert_slack_webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
```

Re-run Terraform to apply your changes:

```
$ terraform init
$ terraform apply
```
