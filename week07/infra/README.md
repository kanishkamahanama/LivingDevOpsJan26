# jan26-bootcamp — Student Portal ECS Deployment

Terraform project that provisions a full AWS 2-tier infrastructure deploying a containerised
Student Portal application on ECS Fargate with a PostgreSQL RDS backend, secured behind an
Application Load Balancer with HTTPS via ACM and Route53.

**Live URL:** `https://student-portal.kanishkadevops.fun`

---

## Architecture

```
Internet
    │
    │ HTTPS (443) / HTTP (80)
    ▼
Route53 (student-portal.kanishkadevops.fun)
    │
    ▼
ACM Certificate (DNS validated)
    │
    ▼
ALB — Application Load Balancer
Public Subnets: 10.0.1.0/24 (us-east-1a)
                10.0.2.0/24 (us-east-1b)
    │
    │ forwards to Target Group (health check: /login)
    ▼
ECS Fargate — 2 tasks (desired count)
Private Subnets: 10.0.3.0/24 (us-east-1a)
                 10.0.4.0/24 (us-east-1b)
    │
    ├── Pulls image from ECR
    │   589613068744.dkr.ecr.us-east-1.amazonaws.com/jan26-bootcamp-student-portal:1.0
    │
    ├── Writes logs to CloudWatch
    │   /ecs/jan26week5-studentportal
    │
    └── Connects to RDS via DB_LINK env var
            │
            ▼
        RDS PostgreSQL 15.14 (db.t3.micro)
        RDS Subnets: 10.0.5.0/24 (us-east-1a)
                     10.0.6.0/24 (us-east-1b)
            │
            ▼
        Password stored in AWS Secrets Manager
        jan26-bootcamp-student-portal-db
```

---

## CIDR Planning

```
VPC: 10.0.0.0/16

Subnet          CIDR            AZ          Purpose
──────────────────────────────────────────────────────
public1         10.0.1.0/24     us-east-1a  ALB
public2         10.0.2.0/24     us-east-1b  ALB
private1        10.0.3.0/24     us-east-1a  ECS Tasks
private2        10.0.4.0/24     us-east-1b  ECS Tasks
rds1            10.0.5.0/24     us-east-1a  RDS
rds2            10.0.6.0/24     us-east-1b  RDS
```

---

## File Structure

```
project/
├── versions.tf       # Terraform version (1.12.1) + provider requirements
├── providers.tf      # AWS provider + S3 remote backend config
├── variables.tf      # All input variables with defaults
├── data.tf           # Data sources (Route53 public hosted zone)
├── network.tf        # VPC, subnets, IGW, NAT GW, EIP, route tables
├── sg.tf             # Security groups (ALB, ECS, RDS)
├── iam.tf            # ECS task execution role + custom policy
├── ecs.tf            # ECR repo, ECS cluster, task definition, service
├── rds.tf            # RDS instance, subnet group, random password, Secrets Manager
├── alb.tf            # ALB, target group, HTTP + HTTPS listeners
├── route53.tf        # ACM cert, DNS validation records, Route53 A record
├── importstuff._tf   # Terraform import block (manual task definition import)
└── importedstuff._tf # Auto-generated config from terraform plan -generate-config-out
```

---

## Remote State Backend

```hcl
backend "s3" {
  bucket  = "km-state-bucket-devops"
  key     = "jan26/week6/terraform.tfstate"
  region  = "us-east-1"
  encrypt = true
}
```

State file stored in S3 with encryption enabled. The S3 key path `jan26/week6/` keeps this
project isolated from other projects in the same bucket.

---

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aws_region` | `us-east-1` | AWS region |
| `vpc_name` | `jan26week6` | VPC name tag |
| `primary_az` | `us-east-1a` | Primary availability zone |
| `secondary_az` | `us-east-1b` | Secondary availability zone |
| `app_name` | `student-portal` | Application name |
| `prefix` | `jan26-bootcamp` | Resource name prefix |
| `image` | ECR URI `:1.0` | Docker image to deploy |
| `container_port` | `8000` | Container listening port |
| `domain_name` | `kanishkadevops.fun` | Base domain name |
| `alb_zone_id` | `Z35SXDOTRQ7X7K` | ALB hosted zone ID (us-east-1) |

---

## Security Group Rules

```
ALB SG (alb-sg)
├── Inbound:  80  TCP  0.0.0.0/0   (HTTP from internet)
├── Inbound:  443 TCP  0.0.0.0/0   (HTTPS from internet)
└── Outbound: ALL      0.0.0.0/0

ECS SG (ecs-sg)
├── Inbound:  8000 TCP  ALB SG only  (traffic from ALB only)
└── Outbound: ALL       0.0.0.0/0

RDS SG (rds-sg)
├── Inbound:  5432 TCP  ECS SG only  (PostgreSQL from ECS only)
└── Outbound: ALL       0.0.0.0/0
```

---

## IAM — ECS Task Execution Role

**Trust Policy** — WHO can assume this role:
```
ecs-tasks.amazonaws.com
```

**Custom Policy** — WHAT it can do (least privilege):
```
ecr:GetAuthorizationToken       pull images from ECR
ecr:BatchCheckLayerAvailability
ecr:GetDownloadUrlForLayer
ecr:BatchGetImage
logs:CreateLogGroup             create CloudWatch log group
logs:CreateLogStream            create log stream
logs:PutLogEvents               write container logs
```

Note: Custom policy used instead of AWS managed `AmazonECSTaskExecutionRolePolicy`
for least privilege — only exact permissions ECS needs.

---

## ECS Task Definition

- **Family:** `jan26-bootcamp-student-portal-task`
- **Launch type:** FARGATE
- **CPU:** 1024 (1 vCPU)
- **Memory:** 2048 MB
- **Network mode:** awsvpc
- **Image:** ECR `jan26-bootcamp-student-portal:1.0`
- **Port:** 8000

**Environment variables passed to container:**
```
Owner   = Kanishka
DB_LINK = postgresql://<user>:<password>@<rds-endpoint>:5432/<db>
          (dynamically built from RDS outputs + random_password)
```

**CloudWatch logging:**
```
Log group:  /ecs/jan26week5-studentportal
Region:     us-east-1
Driver:     awslogs
```

**ECS Service:**
- Desired count: 2 tasks
- Subnets: private1 + private2
- No public IP assigned (private subnets only)
- Connected to ALB via `load_balancer` block (auto-registers dynamic task IPs)

**Auto Scaling (commented out — ready to enable):**
```
Min capacity: 2
Max capacity: 4
Scale out at: 70% CPU utilisation
Scale out cooldown: 300s
Scale in cooldown:  100s
```

---

## RDS

- **Engine:** PostgreSQL 15.14
- **Instance:** db.t3.micro
- **Storage:** 20GB gp2
- **DB name:** stdentportal
- **Username:** postgres
- **Password:** auto-generated by `random_password` (10 chars, alphanumeric)
- **Subnet group:** rds1 + rds2 (private, no public access)
- **skip_final_snapshot:** true (dev environment)

**Secrets Manager:**
- Secret name: `jan26-bootcamp-student-portal-db`
- Stores full DB connection string as JSON:
```json
{
  "db_link": "postgresql://postgres:<password>@<endpoint>:5432/stdentportal"
}
```

---

## ALB + HTTPS

- **Health check path:** `/login`
- **Target type:** `ip` (required for Fargate — registers dynamic container IPs)
- **HTTP Listener (80):** forwards to target group
- **HTTPS Listener (443):** forwards to target group with ACM certificate

**ACM Certificate:**
- Domain: `student-portal.kanishkadevops.fun`
- Validation: DNS via Route53
- Uses `for_each` on `domain_validation_options` for automatic DNS record creation

**Route53:**
- Data source: public hosted zone `kanishkadevops.fun`
- A record: `student-portal.kanishkadevops.fun` → ALB (alias)

---

## Terraform Import

This project demonstrates importing existing AWS resources into Terraform state:

```bash
# Generate config from existing resource
terraform plan -generate-config-out=importedstuff.tf
```

`importstuff._tf` contains the import block:
```hcl
import {
  to = aws_ecs_task_definition.manualimport
  id = "arn:aws:ecs:us-east-1:589613068744:task-definition/jan26week5-studentportal-td:5"
}
```

Terraform auto-generated the full resource config in `importedstuff._tf` — showing the
difference between the manually created task definition (from earlier week) and the
Terraform-managed one in this project.

---

## Terraform Workflow

```bash
terraform init          # download providers, configure S3 backend
terraform fmt           # auto-format all .tf files
terraform validate      # check syntax and config
terraform plan          # dry run — shows what will change
terraform apply         # creates all infrastructure
terraform destroy       # tears down all resources
```

### Useful commands:
```bash
# Save plan to file (safer for production)
terraform plan -out myplan
terraform apply myplan

# Preview destroy without deleting
terraform plan -destroy

# Force recreate a specific resource
terraform apply -replace="aws_ecs_service.service"

# Unlock stuck state (after Ctrl+C interrupt)
rm .terraform.tfstate.lock.info

# Check resource values interactively
terraform console
> aws_lb.alb.dns_name
> aws_db_instance.postgres.address
> nonsensitive(random_password.password.result)
> module.vpc.vpc_id

# Full debug logging
export TF_LOG=TRACE
export TF_LOG_PATH="terraform_log.txt"
terraform plan
unset TF_LOG
unset TF_LOG_PATH

# Import existing resource
terraform plan -generate-config-out=importedstuff.tf
terraform apply
```

---

## Outputs

| Output | Value |
|--------|-------|
| `repo_link` | ECR repository URL |
| `password` | RDS password (sensitive) |
| `dbhost` | RDS endpoint address |
| `public_hosted_zone` | Route53 hosted zone name |

---

## Key Concepts Learned

### Terraform Core
- **Settings block** lives in `versions.tf` / `terraform.tf` — not just `main.tf`
- **Block types:** terraform, provider, resource, data, variable, locals, output, module
- **Implicit dependencies** — Terraform detects resource attribute references automatically
- **Explicit dependencies** — `depends_on` for hidden dependencies (IAM, IGW ordering)
- **Lifecycle rules** — `prevent_destroy`, `create_before_destroy`, `ignore_changes`
- **Interpolation** — `"${var.prefix}-${var.app_name}"` same concept as Python f-strings
- **`jsonencode`** — converts HCL maps/lists to JSON strings for freeform AWS API arguments (IAM policies, ECS container definitions). AWS provider handles JSON automatically for fixed-structure resources
- **`nonsensitive()`** — reveals sensitive values in terraform console for debugging
- **Workspaces** — separate state per environment, `terraform.workspace` for dynamic values
- **tfenv** — manages multiple Terraform versions, pin per project with `.terraform-version`
- **Terraform import** — bring existing AWS resources under Terraform management with `terraform plan -generate-config-out`

### State Management
- `terraform.tfstate` is source of truth — never manually edit
- State locking prevents concurrent operations
  - DynamoDB for remote state
  - `.terraform.tfstate.lock.info` for local state — delete if stuck after Ctrl+C
- `terraform taint` (deprecated) → replaced by `terraform apply -replace`
- Remote backend (S3) — state stored securely, versioned, encrypted
- Each project uses different `key` path in same S3 bucket for isolation

### Networking
- `aws_route_table_association` with `subnet_id` → associates subnet to route table (standard)
- `aws_route_table_association` with `gateway_id` → attaches route table to IGW itself (advanced — gateway route tables for traffic inspection/firewall)
- `0.0.0.0/0 → IGW` must be inside the route block — NOT via a separate gateway association
- Public subnet EC2 → IGW → Internet (direct, free)
- Private subnet ECS → NAT Gateway → IGW → Internet (costs money — single NAT used here for cost saving)
- NAT Gateway needs `depends_on` IGW — explicit dependency because no direct attribute reference

### ECS + Fargate
- ECS cluster → ECS service → task definition → container
- `aws_lb_target_group_attachment` is for EC2/Lambda only — NOT Fargate
- ECS auto-registers dynamic task IPs into target group via `load_balancer` block in service
- `target_type = "ip"` required for Fargate (not `instance`)
- `execution_role_arn` — role ECS uses to pull images and write logs
- `jsonencode` required for `container_definitions` (freeform JSON blob)
- `awslogs-create-group = "true"` requires `logs:CreateLogGroup` permission in IAM policy
- Container Insights can be enabled on cluster for enhanced CloudWatch metrics (commented out)
- Auto scaling ready to enable — `aws_appautoscaling_target` + `aws_appautoscaling_policy`

### IAM
- IAM Role = WHO can use it (trust policy)
- IAM Policy = WHAT it can do (permissions)
- IAM Role Policy Attachment = glues role + policy together (all 3 needed)
- Least privilege — custom policy better than AWS managed `AmazonECSTaskExecutionRolePolicy`
- Minimum ECS permissions: ECR pull + CloudWatch logs (including `CreateLogGroup`)

### RDS
- `aws_db_subnet_group` required before RDS instance
- `random_password` with `special = false` for alphanumeric only
- Store connection string in Secrets Manager as JSON — apps retrieve at runtime
- `skip_final_snapshot = true` for dev, `false` for production
- `deletion_protection = true` for production
- PostgreSQL 15.4 reached end of standard support — use 15.12+ for new deployments

### ACM + Route53
- DNS validation requires 3 resources:
  1. `aws_acm_certificate`
  2. `aws_route53_record` (validation DNS record)
  3. `aws_acm_certificate_validation` — tells Terraform to WAIT until cert is ISSUED
- Without `aws_acm_certificate_validation` the cert stays PENDING forever
- `for_each` on `domain_validation_options` handles multiple domains automatically
- Route53 A record uses `alias` block (not `records`) to point to ALB

---

## Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `RouteConflict` on route table | IGW referenced in both inline route AND `aws_route_table_association gateway_id` | Remove `gateway_id` from association — use `subnet_id` only |
| `AccessDeniedException: logs:CreateLogGroup` | Missing IAM permission on execution role | Add `logs:CreateLogGroup` to task execution policy |
| ACM cert stuck PENDING | Missing `aws_acm_certificate_validation` resource | Add validation resource and use `certificate_arn` from it in HTTPS listener |
| State lock error after Ctrl+C | `.terraform.tfstate.lock.info` not cleaned up | `rm .terraform.tfstate.lock.info` |
| `force-unlock` fails on local state | Local state cannot be unlocked by another process | Delete lock file directly |
| `Version could not be resolved` (tfenv) | No Terraform version set in tfenv | `tfenv install 1.x.x && tfenv use 1.x.x` |
| EC2 forces replace when changing key | AWS injects key pair at launch time only via cloud-init | Use `ignore_changes = [key_name]` lifecycle rule |
| Provider version drift between projects | Different `.terraform/providers/` per project | Each project has isolated `.terraform/` — providers never shared |

---

## Author

**Kanishka Mahanama** — Senior IT / Network Engineer transitioning to DevOps
HashiCorp Certified: Terraform Associate (003)
Domain: [kanishkadevops.fun](https://kanishkadevops.fun) | Twitter: [@__kanishka__](https://twitter.com/__kanishka__)
