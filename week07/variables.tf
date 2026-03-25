# variables.tf

variable "aws_region" {
  type        = string
  description = "aws region"
  default     = "us-east-1"
}

variable "vpc_name" {
  type        = string
  description = "vpc name"
  default     = "jan26week6"
}

variable "primary_az" {
  type        = string
  description = "primary AZ"
  default     = "us-east-1a"
}

variable "secondary_az" {
  type        = string
  description = "secondar AZ"
  default     = "us-east-1b"
}

variable "app_name" {
  type    = string
  default = "student-portal"
}

variable "prefix" {
  type    = string
  default = "jan26-bootcamp"
}

variable "image" {
  type    = string
  default = "589613068744.dkr.ecr.us-east-1.amazonaws.com/jan26week5-studentportal:1.0"
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "db_link" {
  type    = string
  default = "postgresql://postgres:<password>@jan26week5-studentportal-instance.<INSTANCE_ID>.us-east-1.rds.amazonaws.com:5432/studentportal_db"
}

variable "domain_name" {
  type    = string
  default = "kanishkadevops.fun"
}

variable "alb_zone_id" {
  type        = string
  description = "Zone ID for the ALB hosted zone"
  default     = "Z35SXDOTRQ7X7K"
}