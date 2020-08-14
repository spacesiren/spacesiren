output "api_endpoint" {
  value = "https://${aws_route53_record.api.fqdn}"
}

output "message_from_dev" {
  value = "Thank you for using SpaceSiren! <3"
}
