# Student Registration Application

A Flask-based web application for managing student registrations with PostgreSQL database backend, deployed on AWS EC2 with RDS.

## 🎯 Overview

This application provides a simple interface for:
- Viewing a personal portfolio homepage
- Registering students with name and email
- Viewing all registered students
- Automatic database initialization and table creation

## 🏗️ Architecture

```
Internet
    ↓
AWS EC2 Instance (Public Subnet)
    ↓
AWS RDS PostgreSQL (Public Access Enabled)
```

**Components:**
- **Frontend**: HTML/CSS with animated UI
- **Backend**: Flask (Python)
- **Database**: PostgreSQL (AWS RDS)
- **Web Server**: Gunicorn
- **ORM**: SQLAlchemy

## 📋 Prerequisites

### AWS Resources
- AWS Account with permissions to create EC2 and RDS instances
- AWS RDS PostgreSQL instance (publicly accessible)
- AWS EC2 instance (Amazon Linux 2 or Ubuntu)

### Required Information
- RDS endpoint URL
- Database name
- Master username and password
- EC2 instance public IP or DNS

## 🚀 Deployment Guide

### Step 1: Create RDS PostgreSQL Instance

1. **Go to AWS RDS Console**
2. **Click "Create database"**
3. **Select:**
   - Engine: PostgreSQL
   - Template: Free tier (or your preference)
   - DB instance identifier: `jan26week3-db-instance`
   - Master username: `postgres`
   - Master password: (set a strong password)
   - **Public access: Yes** ← Important for this setup
   - VPC security group: Create new or use existing

4. **Configure Security Group:**
   - Add inbound rule:
     ```
     Type: PostgreSQL
     Port: 5432
     Source: 0.0.0.0/0 (for public access) or Your IP
     ```
   - **Note**: For production, restrict to specific IPs or EC2 security groups

5. **Wait for RDS instance to become "Available"**
6. **Note down the endpoint URL** (e.g., `jan26week3-db-instance.c4hw00gywz3b.us-east-1.rds.amazonaws.com`)

### Step 2: Create EC2 Instance

1. **Launch EC2 Instance:**
   - AMI: Amazon Linux 2 or Ubuntu 20.04+
   - Instance type: t2.micro (free tier eligible)
   - Key pair: Create or use existing
   - Security group: Allow SSH (22) and HTTP (8000)

2. **Configure EC2 Security Group:**
   ```
   Inbound Rules:
   - SSH (22) from Your IP
   - Custom TCP (8000) from 0.0.0.0/0
   ```

3. **Note down the public IP address**

### Step 3: Deploy Using User Data (Automated)

**Option A: Use EC2 User Data at Launch**

When launching EC2, paste the `user-data.sh` script into the User Data field:

```bash
#!/bin/bash
sleep 30
cd /home/ec2-user
echo "$(pwd)" >> /home/ec2-user/install-logs.txt
sudo yum install git -y
git clone --no-checkout https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
git sparse-checkout init --cone
git sparse-checkout set week03/day2
git checkout main
cd week03/day2
echo "$(pwd)" >> /home/ec2-user/install-logs.txt
chmod u+x run.sh
./run.sh
```

**Before launching:**
1. Update the GitHub repository URL
2. Update database credentials in `run.sh` (see Step 4)

**Option B: Manual Deployment**

See "Manual Deployment Steps" section below.

### Step 4: Configure Database Connection

Update `run.sh` with your RDS details:

```bash
#!/bin/bash

# Database Configuration - Update with your RDS details
export DB_HOST="jan26week3-db-instance.c4hw00gywz3b.us-east-1.rds.amazonaws.com"
export DB_NAME="jan26week3db"
export DB_USER="postgres"
export DB_PASSWORD="Admin1234"  # Change this to your RDS password
export DB_PORT="5432"
export DB_SSL_MODE="require"

# ... rest of script
```

### Step 5: Access Your Application

1. **Wait 3-5 minutes** for user data script to complete
2. **Check logs** (if needed):
   ```bash
   ssh -i your-key.pem ec2-user@YOUR-EC2-IP
   cat /home/ec2-user/install-logs.txt
   cat /var/log/cloud-init-output.log
   ```

3. **Access the application:**
   ```
   http://YOUR-EC2-PUBLIC-IP:8000
   ```

4. **Test the application:**
   - Home page should load with your portfolio
   - Click "Students" in navigation
   - Register a new student
   - Verify student appears in the list

## 📁 Project Structure

```
week03/day2/
├── app.py                  # Main Flask application
├── init_db.py             # Database initialization script
├── requirements.txt        # Python dependencies
├── run.sh                 # Application startup script
├── user-data.sh           # EC2 user data for automated deployment
└── README.md              # This file
```

## 🔧 Manual Deployment Steps

If not using user data script:

### 1. SSH into EC2 Instance

```bash
ssh -i your-key.pem ec2-user@YOUR-EC2-IP
```

### 2. Clone Repository

```bash
cd /home/ec2-user
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO/week03/day2
```

### 3. Update Database Configuration

```bash
# Edit run.sh with your RDS credentials
nano run.sh

# Update these lines:
export DB_HOST="your-rds-endpoint.amazonaws.com"
export DB_NAME="your-database-name"
export DB_USER="postgres"
export DB_PASSWORD="your-password"
```

### 4. Make Scripts Executable

```bash
chmod +x run.sh
chmod +x init_db.py
```

### 5. Run the Application

```bash
./run.sh
```

The script will:
1. Create a Python virtual environment
2. Install dependencies
3. Initialize the database
4. Create the `students` table
5. Start the Gunicorn server on port 8000

### 6. Verify Deployment

```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Test locally
curl http://localhost:8000/health

# Should return: {"status":"ok"}
```

## 🗄️ Database Schema

### Students Table

| Column      | Type         | Constraints              |
|-------------|--------------|--------------------------|
| id          | INTEGER      | PRIMARY KEY, AUTO INCREMENT |
| name        | VARCHAR(100) | NOT NULL                 |
| email       | VARCHAR(120) | UNIQUE, NOT NULL         |
| created_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP |

## 🔐 Security Considerations

### Current Setup (Development/Demo)
- ✅ RDS with public access enabled
- ✅ SSL/TLS encryption required
- ⚠️ Security groups allow 0.0.0.0/0 (not recommended for production)

### Production Recommendations

1. **Network Security:**
   - Move RDS to private subnet
   - Use VPC peering or private connectivity
   - Restrict security groups to specific IPs
   - Use AWS PrivateLink or VPN

2. **Database Security:**
   - Use AWS Secrets Manager for credentials
   - Enable RDS encryption at rest
   - Enable automated backups
   - Set up Multi-AZ deployment

3. **Application Security:**
   - Use environment variables (never commit credentials)
   - Implement rate limiting
   - Add CSRF protection
   - Use HTTPS with SSL certificate
   - Set strong `SECRET_KEY`

4. **Access Control:**
   - Use IAM database authentication
   - Implement least privilege access
   - Enable CloudTrail logging
   - Set up CloudWatch alarms

## 🛠️ Troubleshooting

### Connection Timeout

**Symptom:** `Connection timed out` when accessing RDS

**Solutions:**
1. Check RDS security group allows inbound on port 5432
2. Verify RDS "Publicly accessible" is set to "Yes"
3. Check EC2 can reach internet (for public RDS)
4. Verify endpoint URL is correct

**Test:**
```bash
nc -zv your-rds-endpoint.amazonaws.com 5432
```

### SSL Connection Error

**Symptom:** `no pg_hba.conf entry ... no encryption`

**Solution:**
- Ensure `DB_SSL_MODE="require"` is set in run.sh

### Authentication Failed

**Symptom:** `password authentication failed`

**Solutions:**
1. Verify DB_USER and DB_PASSWORD in run.sh
2. Check RDS master credentials in AWS Console
3. Ensure database name exists

### Table Does Not Exist

**Symptom:** `relation "students" does not exist`

**Solution:**
```bash
source .venv/bin/activate
python init_db.py
```

### Port 8000 Not Accessible

**Symptom:** Cannot access http://ec2-ip:8000

**Solutions:**
1. Check EC2 security group allows inbound on port 8000
2. Verify Gunicorn is running: `ps aux | grep gunicorn`
3. Check application logs

### Gunicorn Won't Start

**Check logs:**
```bash
# Check if port is already in use
sudo lsof -i :8000

# Kill existing process
pkill gunicorn

# Restart
./run.sh
```

## 📊 Monitoring and Logs

### Application Logs

```bash
# View Gunicorn logs
journalctl -u gunicorn -f

# Check user data execution
cat /var/log/cloud-init-output.log

# Check install logs
cat /home/ec2-user/install-logs.txt
```

### RDS Monitoring

- CloudWatch Metrics: CPU, Connections, Free Storage
- RDS Events: Check for maintenance or issues
- Performance Insights: Query performance

### Health Check Endpoint

```bash
curl http://localhost:8000/health
# Returns: {"status":"ok"}
```

## 🔄 Updating the Application

```bash
cd /home/ec2-user/YOUR-REPO/week03/day2
git pull origin main
pkill gunicorn
./run.sh
```

## 🧪 Testing

### Test Database Connection

```bash
source .venv/bin/activate
python init_db.py
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Home page
curl http://localhost:8000/

# Students page
curl http://localhost:8000/students
```

## 📝 Environment Variables

The application uses the following environment variables:

| Variable       | Description                    | Default     | Required |
|---------------|--------------------------------|-------------|----------|
| DB_HOST       | RDS endpoint URL               | localhost   | Yes      |
| DB_NAME       | Database name                  | students_db | Yes      |
| DB_USER       | Database username              | postgres    | Yes      |
| DB_PASSWORD   | Database password              | postgres    | Yes      |
| DB_PORT       | Database port                  | 5432        | No       |
| DB_SSL_MODE   | SSL mode (require/prefer/etc)  | prefer      | Yes      |
| SECRET_KEY    | Flask secret key               | dev-key     | No       |

## 🚧 Known Limitations

1. **Single Server**: No load balancing or high availability
2. **No HTTPS**: Uses HTTP only (add ALB/CloudFront for HTTPS)
3. **No Authentication**: No user login or access control
4. **Public RDS**: Database is publicly accessible
5. **No Input Validation**: Minimal form validation
6. **No Data Backup**: Manual backups required

## 📚 Technology Stack

- **Language**: Python 3.9+
- **Framework**: Flask 3.1.0
- **Database**: PostgreSQL (AWS RDS)
- **ORM**: SQLAlchemy (via Flask-SQLAlchemy)
- **Web Server**: Gunicorn
- **Cloud Provider**: AWS (EC2, RDS)
- **OS**: Amazon Linux 2

## 📄 License

This project is for educational purposes.

## 👤 Author

Kanishka Mahanama
- Twitter: [@__kanishka__](https://x.com/__kanishka__)
- Senior IT Professional | Network Engineer | DevOps Enthusiast

## 📖 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

**Note**: This setup uses RDS with public access for demonstration purposes. For production deployments, always use private subnets with appropriate security controls.

© 2026 Kanishka Mahanama
