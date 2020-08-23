# 1.2.1 (August 22, 2020)

IMPROVEMENTS:

* Update AWS provider to 3.3.0.

BUG FIXES:

* Lambda logging permissions with the new aws_cloudwatch_log_group ARN format.

# 1.2.0 (August 15, 2020)

FEATURES:

* Pushover support. New tfvars are `alert_pushover_user_key` and `alert_pushover_api_key`.
* Test alert API endpoint: `/test-alert`.

IMPROVEMENTS:

* Remove `trimsuffix` from Route 53 zone name.

# 1.1.0 (August 13, 2020)

IMPROVEMENTS:

* Artwork!
* Change directory structure. Terraform code now has its own directory.
  * If you previously had SpaceSiren set up, delete your `functions-pkg/`
    directory and move the following files/dirs to the `terraform/` directory:
    * `.terraform/`
    * `terraform-local.tf`
    * `terraform.tfvars`

# 1.0.0 (August 9, 2020)

Initial release.

STARTING FEATURES

* Alerts to Email, PagerDuty, and Slack.
