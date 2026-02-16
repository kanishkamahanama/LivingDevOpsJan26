# EC2 Instance Setup and AMI Creation

Complete guide to launch an EC2 instance with user data and create an AMI from it.

---

## Step 1: Launch EC2 Instance with User Data

### Go to EC2 Console

AWS Console → EC2 → Instances → **Launch instances**

### Configure Instance

```
┌─────────────────────────────────────────────┐
│ Name: flask-app-setup                       │
├─────────────────────────────────────────────┤
│ AMI: Amazon Linux 2023                      │
│                                             │
│ Instance type: t2.micro (or t3.micro)       │
│                                             │
│ Key pair: Select your existing key          │
│                                             │
│ Network settings:                           │
│ - VPC: Your VPC                             │
│ - Subnet: Any public subnet                 │
│ - Auto-assign public IP: Enable             │
│                                             │
│ Security group:                             │
│ - Allow SSH (22) from your IP               │
│ - Allow HTTP (80) from anywhere             │
│ - Allow Custom TCP (8000) from anywhere     │
└─────────────────────────────────────────────┘
```

### Add User Data

1. Expand **"Advanced details"** (scroll down)
2. Scroll to **"User data"** section at the bottom
3. Paste this script:

```bash
#!/bin/bash

# Wait 30 seconds for EC2 instance to fully initialize after boot
sleep 30

# Change to ec2-user home directory
cd /home/ec2-user

# Log the current directory path
echo "$(pwd)" >> /home/ec2-user/install-logs.txt

# Install Git
sudo yum install git -y

# Clone the repository without checking out files
git clone --no-checkout https://github.com/kanishkamahanama/LivingDevOpsJan26.git

# Navigate into the cloned repository directory
cd LivingDevOpsJan26

# Initialize sparse checkout in cone mode
git sparse-checkout init --cone

# Configure sparse checkout
git sparse-checkout set week03/day1

# Checkout the main branch
git checkout main

# Navigate into the project directory
cd week03/day1

# Log current directory
echo "$(pwd)" >> /home/ec2-user/install-logs.txt

# Add execute permission to run.sh
chmod u+x run.sh

# IMPORTANT: Run in background so user data completes
nohup ./run.sh > /home/ec2-user/app-output.log 2>&1 &

# Wait for app to start
sleep 10

# Log completion
echo "Setup complete at $(date)" >> /home/ec2-user/install-logs.txt
```

**Key change:** Added `nohup ./run.sh > /home/ec2-user/app-output.log 2>&1 &` to run in background

4. Click **"Launch instance"**

---

## Step 2: Wait for User Data to Complete

### Wait 5-10 minutes for instance to launch and user data to run

### Monitor Progress

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@<instance-public-ip>

# Check user data logs
sudo cat /var/log/cloud-init-output.log

# Check your install logs
cat /home/ec2-user/install-logs.txt

# Check if app is running
ps aux | grep python
# or
ps aux | grep gunicorn

# Test the app
curl http://localhost:8000/
```

### Verify Everything Works

```bash
# Check if repo cloned
ls -la /home/ec2-user/LivingDevOpsJan26/week03/day1/

# Check if virtual environment created
ls -la /home/ec2-user/LivingDevOpsJan26/week03/day1/.venv/

# Check app logs
cat /home/ec2-user/app-output.log

# Test from browser
http://<instance-public-ip>:8000
```

---

## Step 3: Stop the Running App (Important for AMI)

Before creating AMI, we need to stop the app and set it up as a systemd service:

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@<instance-public-ip>

# Find and kill the running app
pkill -f gunicorn
# or
pkill -f python

# Create systemd service
sudo tee /etc/systemd/system/flask-app.service > /dev/null << 'EOF'
[Unit]
Description=Flask Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/LivingDevOpsJan26/week03/day1
Environment="PATH=/home/ec2-user/LivingDevOpsJan26/week03/day1/.venv/bin"
ExecStart=/home/ec2-user/LivingDevOpsJan26/week03/day1/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable flask-app
sudo systemctl start flask-app

# Verify service is running
sudo systemctl status flask-app

# Test app
curl http://localhost:8000/
```

---

## Step 4: Clean Up Before Creating AMI

```bash
# Still in SSH session

# Clear bash history
history -c

# Clear temporary files
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Clear logs (optional)
sudo rm -f /var/log/cloud-init*.log

# Clear SSH host keys (they'll regenerate on new instances)
sudo rm -f /etc/ssh/ssh_host_*

# Exit SSH
exit
```

---

## Step 5: Create AMI from EC2 Console

1. **Go to EC2 → Instances**

2. **Select your instance** (flask-app-setup)

3. **Actions → Image and templates → Create image**

```
┌────────────────────────────────────────────┐
│ Create image                               │
├────────────────────────────────────────────┤
│ Image name: flask-app-week3-day1-v1       │
│                                            │
│ Image description:                         │
│ Flask app with all dependencies installed │
│ From LivingDevOpsJan26/week03/day1        │
│                                            │
│ Instance volumes:                          │
│ ☑ /dev/xvda (root)  8 GiB                 │
│                                            │
│ Tags:                                      │
│ Key: Name  Value: flask-app-ami-v1        │
│ Key: Version  Value: 1.0                  │
│ Key: Date  Value: 2026-02-16              │
│                                            │
│ ☐ No reboot                                │
│   (Leave unchecked - recommended)          │
│                                            │
│         [Cancel]  [Create image]           │
└────────────────────────────────────────────┘
```

4. Click **"Create image"**

5. **Go to AMIs section** to monitor progress:
   - EC2 → Images → AMIs
   - Status will show: **pending** → **available** (5-10 minutes)

---

## Step 6: Test Your AMI

Once AMI is **available**:

1. **EC2 → Images → AMIs**

2. **Select your AMI** (flask-app-week3-day1-v1)

3. **Actions → Launch instance from AMI**

4. **Configure:**
   - Name: test-ami-instance
   - Instance type: t2.micro
   - Key pair: your key
   - Security group: Allow port 8000
   - **NO user data needed!** (everything is in the AMI)

5. **Launch and wait 1-2 minutes**

6. **Test:**

```bash
# SSH to new instance
ssh -i your-key.pem ec2-user@<new-instance-ip>

# Check if service is running
sudo systemctl status flask-app

# Test app
curl http://localhost:8000/

# From browser
http://<new-instance-ip>:8000
```

**Should work immediately!** ⚡

---

## Why This Approach is Cleaner

### Using systemd Service Instead of User Data Scripts

This approach is considered a **production best practice** for several important reasons:

#### 1. **Separation of Concerns** 🎯
- **User data:** One-time setup (install dependencies, clone code)
- **systemd:** Application lifecycle management (start, stop, restart, monitor)
- **Clear responsibility:** User data prepares the environment, systemd runs the application

#### 2. **Reliability and Auto-Recovery** 🔄
```bash
# systemd automatically restarts your app if it crashes
[Service]
Restart=always
RestartSec=3
```
- If your Flask app crashes, systemd restarts it automatically
- User data scripts don't provide this safety net
- No manual intervention needed for recovery

#### 3. **Boot Persistence** 🚀
- systemd services start automatically on every boot
- User data only runs once (or needs complex configuration to run always)
- Instance stop/start cycles don't break your application

#### 4. **Standard Linux Management** 🐧
```bash
# Standard operations that work across all Linux systems
sudo systemctl start flask-app
sudo systemctl stop flask-app
sudo systemctl restart flask-app
sudo systemctl status flask-app
```
- Uses industry-standard tools and practices
- Any Linux admin knows how to work with systemd
- Integration with monitoring tools (CloudWatch, Datadog, etc.)

#### 5. **Clean Logs and Monitoring** 📊
```bash
# Structured logging via journald
sudo journalctl -u flask-app -f          # Follow logs in real-time
sudo journalctl -u flask-app --since today
sudo journalctl -u flask-app -n 100      # Last 100 lines
```
- systemd integrates with journald for centralized logging
- Better than scattered log files in /home/ec2-user/
- Easy to ship logs to CloudWatch, ELK, or other monitoring systems

#### 6. **Resource Management** 💻
```bash
# Can set resource limits (optional)
[Service]
MemoryLimit=512M
CPUQuota=50%
```
- systemd can enforce resource limits
- Prevents runaway processes from consuming all resources
- Better for multi-tenant or shared environments

#### 7. **Dependency Management** 🔗
```bash
[Unit]
After=network.target
Requires=postgresql.service  # Example: wait for database
```
- Control startup order
- Ensure dependencies are available before starting your app
- Prevents race conditions during boot

#### 8. **Professional Production Pattern** 🏢
- This is how production applications are deployed on Linux
- Same pattern used by nginx, postgresql, redis, etc.
- Aligns with DevOps and SRE best practices
- Makes your infrastructure maintainable by other engineers

### Comparison: User Data Script vs systemd

| Aspect | User Data Script | systemd Service |
|--------|------------------|-----------------|
| **Runs on every boot** | No (by default) | Yes ✅ |
| **Auto-restart on crash** | No | Yes ✅ |
| **Standard Linux tool** | No | Yes ✅ |
| **Centralized logging** | No | Yes (journald) ✅ |
| **Resource limits** | No | Yes ✅ |
| **Dependency management** | No | Yes ✅ |
| **Easy to manage** | No | Yes ✅ |
| **Production-ready** | No | Yes ✅ |

### Why This Creates a Better AMI

When you create an AMI with systemd services:

1. **Self-contained:** Everything needed to run the app is in the image
2. **Predictable:** Instances always start the same way
3. **Fast:** No user data processing needed on launch
4. **Reliable:** systemd handles all lifecycle management
5. **Maintainable:** Standard tools and patterns

This is why major companies and AWS best practices recommend this approach! 🎯

---

## Application Logging: Options and Best Practices

### Overview of Logging Strategies

Your Flask application needs proper logging for debugging, monitoring, and compliance. Here are the best practices:

---

### Option 1: systemd + journald (Simplest) ⭐ **Recommended for Starting**

**How it works:**
- systemd captures stdout/stderr from your application
- Logs stored in journald (systemd's logging system)
- Easy to view and manage

**Configuration:**

Your current systemd service already does this:
```bash
[Service]
ExecStart=/home/ec2-user/LivingDevOpsJan26/week03/day1/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
# stdout/stderr automatically captured by journald
```

**View logs:**
```bash
# Real-time logs (like tail -f)
sudo journalctl -u flask-app -f

# Last 100 lines
sudo journalctl -u flask-app -n 100

# Logs from today
sudo journalctl -u flask-app --since today

# Logs from specific time range
sudo journalctl -u flask-app --since "2026-02-16 10:00" --until "2026-02-16 12:00"

# Search for errors
sudo journalctl -u flask-app | grep -i error

# Export logs to file
sudo journalctl -u flask-app --since today > flask-app-logs.txt
```

**Pros:**
- ✅ Zero configuration needed
- ✅ Built into Linux
- ✅ Works immediately
- ✅ Automatic log rotation

**Cons:**
- ⚠️ Logs disappear when instance terminates
- ⚠️ Limited to single instance (can't aggregate across ASG)

---

### Option 2: File-Based Logging with Log Rotation ✅ **Good for Single Instance**

**Setup:**

Update your systemd service to write to files:

```bash
sudo tee /etc/systemd/system/flask-app.service > /dev/null << 'EOF'
[Unit]
Description=Flask Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/LivingDevOpsJan26/week03/day1
Environment="PATH=/home/ec2-user/LivingDevOpsJan26/week03/day1/.venv/bin"
ExecStart=/home/ec2-user/LivingDevOpsJan26/week03/day1/.venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/flask-app/access.log \
    --error-logfile /var/log/flask-app/error.log \
    --log-level info \
    app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
```

**Create log directory:**
```bash
# Create directory
sudo mkdir -p /var/log/flask-app

# Set permissions
sudo chown ec2-user:ec2-user /var/log/flask-app
```

**Setup log rotation** (prevents logs from filling disk):
```bash
sudo tee /etc/logrotate.d/flask-app > /dev/null << 'EOF'
/var/log/flask-app/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ec2-user ec2-user
    sharedscripts
    postrotate
        systemctl reload flask-app > /dev/null 2>&1 || true
    endscript
}
EOF
```

**View logs:**
```bash
# Real-time access logs
tail -f /var/log/flask-app/access.log

# Real-time error logs
tail -f /var/log/flask-app/error.log

# Search for errors
grep -i "error" /var/log/flask-app/error.log

# View last 100 lines
tail -n 100 /var/log/flask-app/access.log
```

**Pros:**
- ✅ Persistent logs in standard location
- ✅ Automatic rotation (won't fill disk)
- ✅ Separate access and error logs
- ✅ Easy to analyze with standard tools (grep, awk, etc.)

**Cons:**
- ⚠️ Manual setup required
- ⚠️ Logs still lost when instance terminates
- ⚠️ Can't aggregate across multiple instances

---

### Option 3: CloudWatch Logs ☁️ ⭐ **Recommended for Production/ASG**

**Why CloudWatch:**
- ✅ Logs persist after instance termination
- ✅ Aggregate logs from multiple instances (perfect for ASG)
- ✅ Search, filter, and analyze across all instances
- ✅ Set up alarms based on log patterns
- ✅ Integrated with AWS ecosystem

**Setup CloudWatch Agent:**

```bash
# Install CloudWatch agent
sudo yum install amazon-cloudwatch-agent -y

# Create configuration
sudo tee /opt/aws/amazon-cloudwatch-agent/etc/config.json > /dev/null << 'EOF'
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/flask-app/access.log",
            "log_group_name": "/aws/ec2/flask-app/access",
            "log_stream_name": "{instance_id}",
            "timezone": "UTC"
          },
          {
            "file_path": "/var/log/flask-app/error.log",
            "log_group_name": "/aws/ec2/flask-app/error",
            "log_stream_name": "{instance_id}",
            "timezone": "UTC"
          }
        ]
      },
      "journal": {
        "log_group_name": "/aws/ec2/flask-app/systemd",
        "log_stream_name": "{instance_id}",
        "unit_whitelist": ["flask-app.service"]
      }
    }
  }
}
EOF

# Start CloudWatch agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json

# Enable on boot
sudo systemctl enable amazon-cloudwatch-agent
```

**Required IAM permissions** (attach to EC2 instance role):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

**View logs in CloudWatch:**
1. AWS Console → CloudWatch → Logs → Log groups
2. Select `/aws/ec2/flask-app/access` or `/aws/ec2/flask-app/error`
3. View all instances' logs in one place
4. Use CloudWatch Insights for advanced queries

**Example CloudWatch Insights query:**
```sql
# Find all 500 errors across all instances
fields @timestamp, @message
| filter @message like /500/
| sort @timestamp desc
| limit 100

# Count requests per instance
stats count() by instance_id
| sort count desc
```

**Pros:**
- ✅ Survives instance termination
- ✅ Multi-instance aggregation (perfect for ASG)
- ✅ Powerful search and filtering
- ✅ Alarms and notifications
- ✅ Long-term retention (configurable)

**Cons:**
- ⚠️ Additional cost (~$0.50/GB ingested + $0.03/GB stored)
- ⚠️ Requires IAM permissions
- ⚠️ More complex setup

---

### Option 4: Structured Logging in Application 🎯 **Best Practice**

Enhance your Flask app with proper structured logging:

**Add to your Flask app:**

```python
import logging
import sys
from pythonjsonlogger import jsonlogger

# Configure structured logging
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
)
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Use in your app
@app.route('/')
def home():
    logger.info('Home page accessed', extra={
        'user_ip': request.remote_addr,
        'path': request.path,
        'method': request.method
    })
    return "Hello World!"

@app.errorhandler(500)
def handle_500(error):
    logger.error('Internal server error', extra={
        'error': str(error),
        'path': request.path,
        'user_ip': request.remote_addr
    })
    return "Server Error", 500
```

**Install dependency:**
```bash
pip install python-json-logger
```

**Benefits:**
- ✅ Structured JSON logs (easy to parse and analyze)
- ✅ Includes context (user IP, path, method, etc.)
- ✅ Works with any log destination (CloudWatch, ELK, Datadog)
- ✅ Professional logging standard

---

### Recommended Logging Strategy by Use Case

#### For Learning/Development:
```
✅ Option 1: journald (systemd logs)
   - Zero setup
   - Good enough for single instance
   - Easy to view with journalctl
```

#### For Production Single Instance:
```
✅ Option 2: File-based logging with rotation
   + Option 3: CloudWatch Logs
   - Persistent local logs
   - CloudWatch for long-term retention
```

#### For Production with ASG (Multiple Instances):
```
✅ Option 3: CloudWatch Logs (required)
   + Option 4: Structured logging in app
   - Aggregate logs from all instances
   - Search and analyze centrally
   - Set up alarms for errors
```

#### Enterprise/High-Traffic:
```
✅ Option 3: CloudWatch Logs
   + Option 4: Structured logging
   + Third-party tools (Datadog, New Relic, ELK Stack)
   - Advanced analytics
   - APM (Application Performance Monitoring)
   - Distributed tracing
```

---

### Quick Setup Commands

**For your current setup (journald):**
```bash
# View logs - that's it! Already working
sudo journalctl -u flask-app -f
```

**Upgrade to file-based logging:**
```bash
# Create log directory
sudo mkdir -p /var/log/flask-app
sudo chown ec2-user:ec2-user /var/log/flask-app

# Update systemd service (add --access-logfile and --error-logfile)
# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart flask-app

# Setup log rotation
sudo tee /etc/logrotate.d/flask-app > /dev/null << 'EOF'
/var/log/flask-app/*.log {
    daily
    rotate 14
    compress
    missingok
    notifempty
}
EOF
```

**Upgrade to CloudWatch (for production ASG):**
```bash
# Install agent
sudo yum install amazon-cloudwatch-agent -y

# Configure (use config above)
# Attach IAM role with CloudWatch permissions
# Start agent
```

---

### Summary: Logging Best Practices ✅

1. **Start simple:** Use journald (already working)
2. **Add file logs:** When you need persistent local logs
3. **Use CloudWatch:** When using ASG or need centralized logs
4. **Add structured logging:** In your application code for production
5. **Set up log rotation:** To prevent disk from filling up
6. **Monitor errors:** Set up CloudWatch alarms for error patterns
7. **Retention policy:** Define how long to keep logs (compliance/cost)

Your current setup already has logging via journald - that's a great start! 🎯

---

## Complete Workflow Summary

```
1. Launch EC2 with user data
   ↓
2. Wait for setup to complete (5-10 min)
   ↓
3. Verify app works
   ↓
4. Create systemd service (cleaner, production-ready)
   ↓
5. Clean up for AMI
   ↓
6. Create AMI (5-10 min)
   ↓
7. Test AMI by launching test instance
   ↓
8. Done! Production-ready AMI ⚡
```

---

## Troubleshooting Tips

### If user data fails:

```bash
# Check cloud-init logs
sudo cat /var/log/cloud-init-output.log | less

# Check for errors
sudo grep -i error /var/log/cloud-init-output.log

# Check your install logs
cat /home/ec2-user/install-logs.txt
```

### If app doesn't start:

```bash
# Check if virtual env was created
ls -la /home/ec2-user/LivingDevOpsJan26/week03/day1/.venv/

# Check app output
cat /home/ec2-user/app-output.log

# Check what's running
ps aux | grep -E 'python|gunicorn'

# Check systemd service
sudo systemctl status flask-app
sudo journalctl -u flask-app -n 50
```

---

## Benefits of Your AMI

Once created, instances from your AMI will:
- ✅ Start in **30-60 seconds** (vs 5-10 minutes with user data)
- ✅ Have everything pre-installed
- ✅ Be **identical** every time
- ✅ Scale faster during traffic spikes
- ✅ Be more reliable (no installation failures)

---

## Notes

- **No manual stop needed:** AWS will automatically reboot the instance during AMI creation (with default "No reboot" unchecked setting)
- **AMI is regional:** Created in the region where your instance is running
- **Update AMI:** When your code changes, repeat this process to create a new version (v2, v3, etc.)
- **Cost:** AMI storage costs ~$0.05/GB/month (for an 8GB AMI = ~$0.40/month)

---

**Good luck! 🚀**
