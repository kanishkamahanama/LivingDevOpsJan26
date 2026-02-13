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
├── nginx-http.conf     # Nginx reverse proxy configuration (HTTP)
├── nginx-https.conf    # Nginx configuration with SSL/TLS (HTTPS)
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

## 🔐 Setting Up HTTPS with SSL Certificate

### Prerequisites for HTTPS
- Domain name pointing to your EC2 instance
- SSL certificate files (certificate.txt, certificate_chain.txt, private_key.txt)
- Security group allowing inbound traffic on port 443

### Step 1: Create SSL Directory and Copy Certificates
```bash
# Create SSL directory
sudo mkdir -p /etc/nginx/ssl

# Copy and rename the certificate files
sudo cp certificate.txt /etc/nginx/ssl/certificate.crt
sudo cp certificate_chain.txt /etc/nginx/ssl/certificate_chain.crt
sudo cp private_key.txt /etc/nginx/ssl/private.key

# Set proper permissions
sudo chmod 600 /etc/nginx/ssl/private.key
sudo chmod 644 /etc/nginx/ssl/certificate.crt
sudo chmod 644 /etc/nginx/ssl/certificate_chain.crt
sudo chown root:root /etc/nginx/ssl/*
```

### Step 2: Combine Certificate and Chain
```bash
# Combine certificate and chain into one file
sudo cat /etc/nginx/ssl/certificate.crt /etc/nginx/ssl/certificate_chain.crt | sudo tee /etc/nginx/ssl/fullchain.crt

# Set permissions
sudo chmod 644 /etc/nginx/ssl/fullchain.crt
```

### Step 3: Decrypt Private Key (if encrypted)
```bash
# Check if the key has a passphrase
sudo grep -q "ENCRYPTED" /etc/nginx/ssl/private.key && echo "Key is encrypted" || echo "Key is not encrypted"

# If encrypted, decrypt the key
sudo openssl rsa -in /etc/nginx/ssl/private.key -out /etc/nginx/ssl/private_decrypted.key
# Enter your passphrase when prompted

# Replace the encrypted key with decrypted one
sudo mv /etc/nginx/ssl/private_decrypted.key /etc/nginx/ssl/private.key
sudo chmod 600 /etc/nginx/ssl/private.key
```

### Step 4: Update Nginx Configuration for HTTPS
Create a new nginx configuration file `nginx-https.conf`:

```nginx
events {}

http {
    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Certificate (combined certificate + chain)
        ssl_certificate /etc/nginx/ssl/fullchain.crt;
        ssl_certificate_key /etc/nginx/ssl/private.key;

        # SSL Configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
        ssl_prefer_server_ciphers off;
        
        # SSL Session Cache
        ssl_session_timeout 1d;
        ssl_session_cache shared:MozSSL:10m;
        ssl_session_tickets off;

        # Security Headers
        add_header Strict-Transport-Security "max-age=63072000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port $server_port;
        }
    }
}
```

### Step 5: Apply HTTPS Configuration
```bash
# Copy the HTTPS nginx config
sudo cp nginx-https.conf /etc/nginx/nginx.conf

# Verify certificate and key match
sudo openssl x509 -noout -modulus -in /etc/nginx/ssl/certificate.crt | openssl md5
sudo openssl rsa -noout -modulus -in /etc/nginx/ssl/private.key | openssl md5
# These two should output the same hash

# Test nginx configuration
sudo nginx -t

# If successful, restart nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

### Step 6: Configure Firewall for HTTPS
```bash
# Ubuntu/Debian
sudo ufw allow 443/tcp

# Amazon Linux/RHEL/CentOS
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Also update AWS Security Group to allow inbound TCP traffic on port 443
```

### Step 7: Verify HTTPS Setup
```bash
# Test from command line
curl -I https://yourdomain.com

# Check certificate details
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Test in browser
# Visit https://yourdomain.com
```

## 🛡️ Security Considerations
- Production deployment uses HTTPS (port 443) with SSL/TLS encryption
- HTTP traffic (port 80) automatically redirects to HTTPS
- Modern TLS protocols (TLSv1.2 and TLSv1.3) enabled
- Security headers configured (HSTS, X-Frame-Options, X-Content-Type-Options)
- SSL session caching enabled for performance
- Private keys stored with restricted permissions (600)

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

### SSL Certificate Issues
```bash
# Verify certificate chain
sudo openssl verify -CAfile /etc/nginx/ssl/certificate_chain.crt /etc/nginx/ssl/certificate.crt

# Check certificate expiration
sudo openssl x509 -in /etc/nginx/ssl/certificate.crt -noout -dates

# Test SSL connection
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

## 📝 Development Notes
- Virtual environment is created in `.venv/` (gitignored)
- Dependencies are locked in `requirements.txt`
- The `run.sh` script handles complete setup automatically
- Keep SSL certificate files secure and never commit them to version control

## 🚦 Accessing the Application

Once deployed:
- **HTTP (development)**: `http://your-ec2-public-ip`
- **HTTPS (production)**: `https://yourdomain.com`


## 👤 Author
Kanishka Mahanama
- Senior IT Professional | Network Engineer | DevOps Enthusiast
- Twitter: [@__kanishka__](https://x.com/__kanishka__)

## 📄 License
This project is open source and available for personal and educational use.