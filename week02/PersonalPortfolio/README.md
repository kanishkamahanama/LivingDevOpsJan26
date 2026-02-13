# Personal Portfolio Web Application

A professional portfolio website built with Flask, deployed on AWS EC2 with Nginx reverse proxy and Gunicorn WSGI server.

## 📋 Description
This is Kanishka Mahanama's personal portfolio website showcasing:
- Professional background (15+ years IT experience)
- Network engineering expertise
- DevOps transition journey
- Technical skills in Azure, Terraform, Linux, Cisco, and more

## 🏗️ Architecture
- **Frontend**: Flask with embedded HTML/CSS (single-page design)
- **WSGI Server**: Gunicorn with 4 worker processes
- **Web Server**: Nginx as reverse proxy
- **Deployment**: Automated bash script

## 🚀 Quick Start on EC2

### Prerequisites
- AWS EC2 instance (Amazon Linux 2023 or Ubuntu)
- Python 3.8+
- Nginx installed
- Security group allowing inbound traffic on port 80

### 1. Connect to EC2
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

### 2. Clone Only This Project (Sparse Checkout)
```bash
# Clone without checking out files
git clone --no-checkout https://github.com/yourusername/LivingDevOpsJan26.git
cd LivingDevOpsJan26

# Enable sparse checkout
git sparse-checkout init --cone
git sparse-checkout set week01/PersonalPortfolio

# Checkout the files
git checkout main

# Navigate to project
cd week01/PersonalPortfolio
```

### 3. Install Nginx
```bash
# Amazon Linux 2023
sudo yum install nginx -y

# Ubuntu
sudo apt update && sudo apt install nginx -y

# Enable nginx to start on boot
sudo systemctl enable nginx
```

### 4. Configure Nginx
```bash
# Copy nginx config
sudo cp nginx-http.conf /etc/nginx/nginx.conf

# Test nginx configuration
sudo nginx -t

# If test passes, restart nginx
sudo systemctl restart nginx
```

### 5. Run the Application
```bash
# Make run script executable
chmod +x run.sh

# Run the deployment script
./run.sh
```

The application will be running on `http://your-ec2-public-ip`

### 6. Run in Background (Optional)
```bash
# Stop the foreground process (Ctrl+C)

# Run gunicorn in background with nohup
nohup gunicorn -w 4 -b 0.0.0.0:8000 app:app > gunicorn.log 2>&1 &

# Check if it's running
ps aux | grep gunicorn
```

## 📁 Project Structure
```
PersonalPortfolio/
├── app.py              # Flask application with embedded HTML
├── requirements.txt    # Python dependencies
├── nginx-http.conf     # Nginx reverse proxy configuration
├── run.sh              # Automated deployment script
└── README.md           # This file
```

## 🔧 Configuration Details

### Flask App (app.py)
- Runs on port 8000
- `/` - Main portfolio page
- `/health` - Health check endpoint

### Nginx (nginx-http.conf)
- Listens on port 80
- Proxies all traffic to Gunicorn on port 8000

### Gunicorn
- 4 worker processes
- Binds to 0.0.0.0:8000
- Production-ready WSGI server

## 🛡️ Security Considerations
- Currently running on HTTP (port 80)
- For production with HTTPS, you'll need:
  - Domain name
  - SSL certificate (Let's Encrypt)
  - Updated nginx config for SSL

## 🔍 Troubleshooting

### Check if Gunicorn is running
```bash
ps aux | grep gunicorn
```

### Check Nginx status
```bash
sudo systemctl status nginx
```

### View Nginx error logs
```bash
sudo tail -f /var/log/nginx/error.log
```

### Check if port 8000 is listening
```bash
sudo netstat -tulpn | grep 8000
# or
sudo ss -tulpn | grep 8000
```

### Stop Gunicorn
```bash
pkill gunicorn
```

### Restart Nginx
```bash
sudo systemctl restart nginx
```

## 📝 Development Notes
- Virtual environment is created in `.venv/` (gitignored)
- Dependencies are locked in `requirements.txt`
- The `run.sh` script handles complete setup automatically

## 🚦 Accessing the Application

Once deployed:
- **Website**: `http://your-ec2-public-ip`
- **Health Check**: `http://your-ec2-public-ip/health`

## 📈 Future Enhancements
- [ ] Add HTTPS support with SSL certificate
- [ ] Dockerize the application
- [ ] Add CI/CD pipeline
- [ ] Implement automated backups
- [ ] Add monitoring and logging

## 👤 Author
Kanishka Mahanama
- Senior IT Professional | Network Engineer | DevOps Enthusiast
- Twitter: [@__kanishka__](https://x.com/__kanishka__)
