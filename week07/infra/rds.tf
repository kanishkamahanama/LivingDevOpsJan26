# rds.tf

# subnet group
# search - terraform aws subnet group
resource "aws_db_subnet_group" "default" {
  name       = "${var.prefix}-${var.app_name}-db-subnet-group"
  subnet_ids = [aws_subnet.rds1.id, aws_subnet.rds2.id]
}

# password (A-Za-z0-9) -> secrets manager
# search - terraform random for password
resource "random_password" "password" {
  length  = 10
  special = false
}

output "password" {
  value     = random_password.password.result
  sensitive = true
}

#  secret manager create

resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.prefix}-${var.app_name}-db"
  recovery_window_in_days = 0
}

# create secret in secret manager (version)
# "postgresql://postgres:<PASSWORD>@jan26week5-studentportal-instance.<INSTANCE_ID>.us-east-1.rds.amazonaws.com:5432/studentportal_db"

resource "aws_secretsmanager_secret_version" "db_password_version" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    db_link = "postgresql://${aws_db_instance.postgres.username}:${random_password.password.result}@${aws_db_instance.postgres.address}:5432/${aws_db_instance.postgres.db_name}"
  })
}


# rds instance

resource "aws_db_instance" "postgres" {
  identifier             = "${var.prefix}-${var.app_name}-db"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "15.14"
  instance_class         = "db.t3.micro"
  db_name                = "stdentportal"
  username               = "postgres"
  password               = random_password.password.result
  db_subnet_group_name   = aws_db_subnet_group.default.name
  skip_final_snapshot    = true
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.rds.id]
}

output "dbhost" {
  value = aws_db_instance.postgres.address
}