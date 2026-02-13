# Living DevOps Bootcamp - January 2026

This repository contains all my DevOps bootcamp projects organized by week.

## 📁 Repository Structure
```
LivingDevOpsJan26/
├── week01/
│   └── PersonalPortfolio/  # Flask portfolio app with Nginx + Gunicorn
├── week02/
│   └── DockerProject/      # Docker containerization project
├── week03/
│   └── KubernetesProject/  # Kubernetes deployment
└── README.md
```

## 🚀 How to Use This Repo

### Clone Entire Repository
```bash
git clone https://github.com/yourusername/LivingDevOpsJan26.git
```

### Clone Only Specific Project (Sparse Checkout)
```bash
# Clone without checking out files
git clone --no-checkout https://github.com/yourusername/LivingDevOpsJan26.git
cd LivingDevOpsJan26

# Enable sparse checkout
git sparse-checkout init --cone

# Specify which project to pull
git sparse-checkout set week01/PersonalPortfolio

# Checkout the files
git checkout main
```

## 📚 Weekly Projects

### Week 01 - Personal Portfolio Web Application
- Flask-based personal portfolio website
- Production deployment with Nginx reverse proxy and Gunicorn
- Automated deployment script
- [View Project](week01/PersonalPortfolio/)

### Week 02 - Docker Project
- Coming soon...

### Week 03 - Kubernetes Project
- Coming soon...

## 🛠️ Technologies Used
- AWS EC2
- Python Flask
- Nginx
- Gunicorn
- Docker
- Kubernetes
- Git & GitHub

## 📝 Notes
- Each week's project is self-contained in its own directory
- Use sparse checkout to pull only specific projects on EC2 instances
- All sensitive data (credentials, keys) are gitignored

## 👤 Author
Kanishka Mahanama - DevOps Bootcamp January 2026
- Twitter: [@__kanishka__](https://x.com/__kanishka__)
