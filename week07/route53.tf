# dns router53 record -> ALB DNS name
# search - aws route53 record terraform
resource "aws_route53_record" "app_record" {
  zone_id = data.aws_route53_zone.public_zone.zone_id
  name    = "${var.app_name}.${var.domain_name}"
  type    = "A"
  alias {
    name                   = aws_lb.alb.dns_name
    zone_id                = aws_lb.alb.zone_id
    evaluate_target_health = true
  }

}

# ACM certificate for ALB
resource "aws_acm_certificate" "alb_cert" {
  domain_name       = "${var.app_name}.${var.domain_name}"
  validation_method = "DNS"
  lifecycle {
    create_before_destroy = true
  }
}


# DNS validation record for ACM certificate
resource "aws_route53_record" "alb_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.alb_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }
  zone_id = data.aws_route53_zone.public_zone.zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.record]

  depends_on = [aws_acm_certificate.alb_cert]
}
