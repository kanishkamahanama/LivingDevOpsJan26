# public hosted zone
# search - aws public hosted zone terraform data source
data "aws_route53_zone" "public_zone" {
  name         = var.domain_name
  private_zone = false
}

output "public_hosted_zone" {
  value = data.aws_route53_zone.public_zone.name
}


