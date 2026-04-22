#!/bin/bash
# AGROS Automated Deployment Script for AWS EC2 (Ubuntu 22.04/24.04)
# Make sure you have cloned your project and are inside the 'agros' directory.
#
# USAGE: 
#   chmod +x deploy_agros.sh
#   sudo ./deploy_agros.sh

echo "==========================================="
echo " AGROS Automated Deployment Script"
echo "==========================================="

if [ "$EUID" -ne 0 ]; then
  echo "ERROR: Please run as root (sudo ./deploy_agros.sh)"
  exit
fi

PROJECT_DIR=$(pwd)
DOMAIN_OR_IP=$(curl -s http://checkip.amazonaws.com)

echo "Detected IP Address: $DOMAIN_OR_IP"
echo "Project Directory: $PROJECT_DIR"

# 1. System Updates and Dependencies
echo ">>> Installing System Dependencies..."
apt update && apt upgrade -y
apt install -y python3-pip python3-venv python3-dev default-libmysqlclient-dev build-essential pkg-config nginx mysql-server

# 2. Database Configuration
echo ">>> Configuring MySQL Database..."
mysql -u root -e "CREATE DATABASE IF NOT EXISTS agros CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -e "CREATE USER IF NOT EXISTS 'agros'@'localhost' IDENTIFIED BY 'agrospassword';"
mysql -u root -e "GRANT ALL PRIVILEGES ON agros.* TO 'agros'@'localhost';"
mysql -u root -e "FLUSH PRIVILEGES;"

# 3. Python Environment Setup
echo ">>> Setting up Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

echo ">>> Installing Python Requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "ERROR: requirements.txt not found. Attempting basic install."
    pip install Django mysqlclient django-widget-tweaks reportlab gunicorn
fi

# 4. Django Configuration Updates
echo ">>> Updating Django settings.py for Production..."
SETTINGS_FILE="$PROJECT_DIR/agros/settings.py"

# Update ALLOWED_HOSTS
sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = \['*', '$DOMAIN_OR_IP'\]/g" "$SETTINGS_FILE"

# Update Database Credentials safely
sed -i "s/\"USER\": \"root\"/\"USER\": \"agros\"/g" "$SETTINGS_FILE"
sed -i "s/\"PASSWORD\": \"root\"/\"PASSWORD\": \"agrospassword\"/g" "$SETTINGS_FILE"

# 5. Execute Django Core Operations
echo ">>> Running Migrations and Collecting Static Files..."
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# 6. Seed Database
echo ">>> Seeding Database with Professional Data..."
python seed_professional_data.py

# 7. Configure Gunicorn Systemd Service
echo ">>> Configuring Gunicorn Service..."
cat > /etc/systemd/system/gunicorn.service << EOF
[Unit]
Description=gunicorn daemon for AGROS
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:$PROJECT_DIR/agros.sock agros.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start gunicorn
systemctl enable gunicorn

# 8. Configure Nginx Server Block
echo ">>> Configuring Nginx..."
cat > /etc/nginx/sites-available/agros << EOF
server {
    listen 80;
    server_name $DOMAIN_OR_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root $PROJECT_DIR;
    }
    
    location /media/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/agros.sock;
    }
}
EOF

ln -s /etc/nginx/sites-available/agros /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

echo "==========================================="
echo " Deployment Complete!"
echo " You can now access AGROS at: http://$DOMAIN_OR_IP"
echo " (Note: It may take a minute for DNS/IP propagation)"
echo "==========================================="
