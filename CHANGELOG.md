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
