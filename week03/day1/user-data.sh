#!/bin/bash

# Wait 30 seconds for EC2 instance to fully initialize after boot
sleep 30

# Change to ec2-user home directory (ensures we're in correct location)
cd /home/ec2-user

# Log the current directory path to install-logs.txt file for debugging
echo "$(pwd)" >> /home/ec2-user/install-logs.txt

# Install Git using yum package manager with automatic yes to prompts
sudo yum install git -y

# Clone the repository without checking out files (for sparse checkout setup)
git clone --no-checkout https://github.com/kanishkamahanama/LivingDevOpsJan26.git

# Navigate into the cloned repository directory
cd LivingDevOpsJan26

# Initialize sparse checkout in cone mode to checkout only specific folders
git sparse-checkout init --cone

# Configure sparse checkout to only pull the week03/day1 directory
git sparse-checkout set week03/day1

# Checkout the main branch and download the files specified by sparse-checkout
git checkout main

# Navigate into the week03/day1 project directory
cd week03/day1

# Log current directory to verify we're in the correct location
echo "$(pwd)" >> /home/ec2-user/install-logs.txt

# Add execute permission to run.sh script for the user
chmod u+x run.sh

# Execute the run.sh script to start the application
./run.sh