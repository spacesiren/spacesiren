# SpaceSiren

SpaceSiren is a [honey token](https://en.wikipedia.org/wiki/Honeypot_(computing)) 
manager and alert system for AWS. With this fully serverless application,
you can create and manage honey tokens at scale -- up to 10,000 per SpaceSiren
instance -- at close to no cost.<sup>1</sup>

![Token API screenshot](docs/screenshots/token-api.png)

Supported alert outputs include:

* Email
* PagerDuty
* Slack

## Documentation Pages

* [Getting Started](docs/getting-started.md)
* [Alerts](docs/alerts.md)
* [API Documentation](docs/api.md)
* [Terraform Variables](docs/tfvars.md)

## Requirements

As with any open source project, this one assumes you have the required
foundational tools and knowledge, mainly in AWS and Terraform.

### Resources

* Terraform >= 0.13
* AWS CLI
* A dedicated AWS account with admin access
* A registered domain

### Knowledge

* Basic Terraform
* Basic REST API
* Basic AWS CLI, S3, and Route 53
* Basic AWS Organizations and IAM Roles for cross-account access
* Intermediate DNS (delegating a (sub)domain with NS records)

## Attributions

Special thanks to:

* Atlassian for [Project SpaceCrab](https://bitbucket.org/asecurityteam/spacecrab), the
  inspiration for this project. If you want to read about why I started SpaceSiren,
  please see my [SpaceCrab critique](docs/spacecrab.md) page.
* Anyone who volunteered to test this application for me.

---

## Footnotes

1. While SpaceSiren was designed to run as cheaply as possible, even for
   individuals, it will not be entirely free of operating costs. You will incur
   nominal costs for DynamoDB, Lambda, API Gateway, Route 53, and perhaps
   CloudTrail, depending on your configuration. You should expect to spend
   between $1 and $5 per month to run SpaceSiren. Of course, the project's
   maintainers are not responsible for any actual costs you incur. Please closely
   monitor your AWS bill while it is in use. 
