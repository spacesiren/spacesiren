# SpaceCrab Critique

← [Home](../README.md)

After seeing SpaceSiren, you may remember a similar project called
"[SpaceCrab](https://bitbucket.org/asecurityteam/spacecrab/src/master/)" from
Atlassian. I'll admit that this project was heavily inspired by SpaceCrab.

While I love the idea of SpaceCrab, there were a few issues with it that I
found difficult to get past. Namely...

* It's written in Python 2, a language that is now end-of-life and was already
  nearing deprecation when the project began.
* It uses AWS CloudFormation to provision the stack. The documentation even
  admits that it may fail randomly for no reason. Plus I'm more fond of Terraform
  just out of personal preference.
* It requires an RDS instance and a VPC NAT Gateway to operate. While that may
  be a drop in the bucket for most businesses, it's expensive for an individual
  to run on their own.
* Lack of alert integration options; only sends to email and PagerDuty.
* Each individual action performed with a honey token triggers its own alert.
  If an attacker attempts 5 actions, you will receive 5 emails or PagerDuty
  alerts.
* The project was active for only a year and has had no substantial commits
  within the last two years as of this writing.

In response, I've made the following improvements for SpaceSiren:

* It's written in Python 3.8, the latest stable version at the time the
  SpaceSiren project began.
* It uses Terraform to provision the stack.
* It's completely serverless! It's all powered on Lambda, DynamoDB, and API
  Gateway, all of which are pay-as-you-go. No full-time servers to run!
* In addition to email and PagerDuty, it supports Slack webhooks for alerts.
* Supports alert "cooldown", meaning it will suppress notifications for future
  events for a user-defined time after the first alert is triggered.
* While I can't sign a commitment to SpaceSiren's future development, I plan to
  keep it maintained for the foreseeable future. Plus I hope contributors will
  be more inclined to propose changes since the project is not run by a large
  company.

Just as I've taken inspiration from Atlassian for SpaceSiren, I hope they can
take inspiration from this project to improve SpaceCrab.
