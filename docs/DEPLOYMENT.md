# Deployment Guide

<!--
Letta Chatbot Deployment Guide
Copyright (C) 2025 Mark Hopkins
Licensed under CC-BY-SA 4.0
-->

Complete guide for deploying Letta Chatbot to production environments.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Environment Configuration](#environment-configuration)
- [Deployment Methods](#deployment-methods)
  - [Traditional Server](#traditional-server-deployment)
  - [Docker](#docker-deployment)
  - [Docker Compose](#docker-compose-deployment)
  - [Kubernetes](#kubernetes-deployment)
  - [Cloud Platforms](#cloud-platform-deployment)
- [Reverse Proxy Setup](#reverse-proxy-setup)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Performance Optimization](#performance-optimization)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Security Hardening](#security-hardening)
- [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] All environment variables are properly configured
- [ ] Secret keys are strong and unique
- [ ] SSL/TLS certificates are obtained and configured
- [ ] Letta server is accessible from the deployment environment
- [ ] Database backups are configured (if using separate DB)
- [ ] Monitoring and logging are set up
- [ ] Rate limiting is configured appropriately
- [ ] Security headers are enabled
- [ ] CORS policies are properly configured
- [ ] Error pages are customized
- [ ] Performance testing is completed

## Environment Configuration

### Production Environment Variables

Create a `.env.production` file:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_SECRET_KEY=your-very-long-and-random-secret-key-here

# Letta Configuration
LETTA_BASE_URL=https://your-letta-server.com:8283
LETTA_API_KEY=your-production-api-key

# Feature Flags
USE_COOKIE_BASED_AUTHENTICATION=true
CREATE_AGENTS_FROM_UI=true

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# Performance
CACHE_TYPE=redis
REDIS_URL=redis://localhost:6379/0
```

### Generating Secret Keys

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Environment-Specific Settings

```python
# config.py
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
```

## Deployment Methods

### Traditional Server Deployment

#### Using Gunicorn

1. **Install Gunicorn**
   ```bash
   pip install gunicorn gevent
   ```

2. **Create systemd service**
   
   `/etc/systemd/system/letta-chatbot.service`:
   ```ini
   [Unit]
   Description=Letta Chatbot Flask Application
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/letta-chatbot
   Environment="PATH=/var/www/letta-chatbot/venv/bin"
   EnvironmentFile=/var/www/letta-chatbot/.env.production
   ExecStart=/var/www/letta-chatbot/venv/bin/gunicorn \
     --workers 4 \
     --worker-class gevent \
     --bind 127.0.0.1:5000 \
     --timeout 120 \
     --access-logfile /var/log/letta-chatbot/access.log \
     --error-logfile /var/log/letta-chatbot/error.log \
     wsgi_production:app

   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start service**
   ```bash
   sudo systemctl enable letta-chatbot
   sudo systemctl start letta-chatbot
   sudo systemctl status letta-chatbot
   ```

#### Using uWSGI

1. **Install uWSGI**
   ```bash
   pip install uwsgi
   ```

2. **Create uWSGI configuration**
   
   `uwsgi.ini`:
   ```ini
   [uwsgi]
   module = wsgi_production:app
   master = true
   processes = 4
   threads = 2
   socket = 127.0.0.1:5000
   chmod-socket = 660
   vacuum = true
   die-on-term = true
   logto = /var/log/letta-chatbot/uwsgi.log
   ```

3. **Run uWSGI**
   ```bash
   uwsgi --ini uwsgi.ini
   ```

### Docker Deployment

#### Dockerfile

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/api/runtime')"

# Run application
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "--timeout=120", "wsgi_production:app"]
```

#### Build and Run

```bash
# Build image
docker build -t letta-chatbot:latest .

# Run container
docker run -d \
  --name letta-chatbot \
  -p 5000:5000 \
  -e LETTA_BASE_URL="https://your-server.com:8283" \
  -e LETTA_API_KEY="your_key" \
  -e FLASK_SECRET_KEY="your_secret" \
  --restart unless-stopped \
  letta-chatbot:latest
```

#### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  letta-chatbot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - LETTA_BASE_URL=${LETTA_BASE_URL}
      - LETTA_API_KEY=${LETTA_API_KEY}
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/runtime"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - letta-chatbot
    restart: unless-stopped

volumes:
  redis-data:
```

Run with:

```bash
docker-compose up -d
```

### Kubernetes Deployment

#### Deployment YAML

`k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: letta-chatbot
  labels:
    app: letta-chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: letta-chatbot
  template:
    metadata:
      labels:
        app: letta-chatbot
    spec:
      containers:
      - name: letta-chatbot
        image: your-registry/letta-chatbot:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: LETTA_BASE_URL
          valueFrom:
            secretKeyRef:
              name: letta-secrets
              key: base-url
        - name: LETTA_API_KEY
          valueFrom:
            secretKeyRef:
              name: letta-secrets
              key: api-key
        - name: FLASK_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: letta-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/runtime
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/runtime
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: letta-chatbot
spec:
  selector:
    app: letta-chatbot
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

#### Create Secrets

```bash
kubectl create secret generic letta-secrets \
  --from-literal=base-url='https://your-server.com:8283' \
  --from-literal=api-key='your_api_key' \
  --from-literal=secret-key='your_secret_key'
```

#### Deploy

```bash
kubectl apply -f k8s/deployment.yaml
```

### Cloud Platform Deployment

#### AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB application**
   ```bash
   eb init -p python-3.11 letta-chatbot
   ```

3. **Create environment**
   ```bash
   eb create letta-chatbot-prod
   ```

4. **Set environment variables**
   ```bash
   eb setenv LETTA_BASE_URL=https://your-server.com:8283 \
            LETTA_API_KEY=your_key \
            FLASK_SECRET_KEY=your_secret
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

#### Google Cloud Platform (App Engine)

Create `app.yaml`:

```yaml
runtime: python311
entrypoint: gunicorn -b :$PORT wsgi_production:app

env_variables:
  FLASK_ENV: 'production'
  LETTA_BASE_URL: 'https://your-server.com:8283'

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6
```

Deploy:

```bash
gcloud app deploy
```

#### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create letta-chatbot-prod

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set LETTA_BASE_URL=https://your-server.com:8283
heroku config:set LETTA_API_KEY=your_key
heroku config:set FLASK_SECRET_KEY=your_secret

# Deploy
git push heroku main
```

## Reverse Proxy Setup

### Nginx Configuration

`/etc/nginx/sites-available/letta-chatbot`:

```nginx
upstream letta_chatbot {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/letta-chatbot-access.log;
    error_log /var/log/nginx/letta-chatbot-error.log;

    # Max upload size
    client_max_body_size 10M;

    location / {
        proxy_pass http://letta_chatbot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # WebSocket support (for future use)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files
    location /static/ {
        alias /var/www/letta-chatbot/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/letta-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Apache Configuration

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName your-domain.com

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/your-domain.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/your-domain.com/privkey.pem

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/

    <Location />
        ProxyPass http://127.0.0.1:5000/
        ProxyPassReverse http://127.0.0.1:5000/
    </Location>
</VirtualHost>
```

## SSL/TLS Configuration

### Using Let's Encrypt

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Manual Certificate

```nginx
ssl_certificate /path/to/fullchain.pem;
ssl_certificate_key /path/to/privkey.pem;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers on;
```

## Performance Optimization

### Gunicorn Configuration

```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/letta-chatbot/access.log"
errorlog = "/var/log/letta-chatbot/error.log"
loglevel = "info"

# Process naming
proc_name = "letta-chatbot"

# Server mechanics
daemon = False
pidfile = "/var/run/letta-chatbot.pid"
```

Run with:

```bash
gunicorn -c gunicorn.conf.py wsgi_production:app
```

### Redis Caching

```python
# config.py
class ProductionConfig(Config):
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300
```

### CDN Integration

Configure CDN for static assets:

```python
# config.py
CDN_DOMAIN = 'cdn.your-domain.com'
CDN_HTTPS = True
```

## Monitoring and Logging

### Application Logging

```python
# config.py
import logging

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/letta-chatbot/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'default',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console']
    }
}
```

### Health Check Endpoint

The app includes a health check at `/api/runtime`:

```bash
curl http://localhost:5000/api/runtime
```

### Monitoring with Prometheus

Install `prometheus-flask-exporter`:

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

Access metrics at `/metrics`.

### Log Aggregation (ELK Stack)

Use Filebeat to ship logs to Elasticsearch:

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/letta-chatbot/*.log
  fields:
    app: letta-chatbot

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

## Backup and Recovery

### Application Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/letta-chatbot"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup application code
tar -czf "$BACKUP_DIR/app_$DATE.tar.gz" /var/www/letta-chatbot

# Backup environment file
cp /var/www/letta-chatbot/.env.production "$BACKUP_DIR/env_$DATE"

# Keep only last 30 days of backups
find "$BACKUP_DIR" -type f -mtime +30 -delete
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /usr/local/bin/backup.sh
```

## Security Hardening

### Security Headers

```python
from flask_talisman import Talisman

Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "unpkg.com"],
        'style-src': ["'self'", "'unsafe-inline'"],
    }
)
```

### Input Validation

All inputs are validated:
- XSS prevention via HTML escaping
- CSRF protection via Flask-WTF
- SQL injection prevention (not applicable - no SQL)
- Rate limiting on all endpoints

### Secrets Management

Use environment variables or secret management services:

```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id letta-chatbot-secrets

# HashiCorp Vault
vault kv get secret/letta-chatbot
```

## Troubleshooting

### Common Issues

#### Application Won't Start

```bash
# Check logs
sudo journalctl -u letta-chatbot -n 50

# Check permissions
ls -la /var/www/letta-chatbot
sudo chown -R www-data:www-data /var/www/letta-chatbot

# Verify environment
source venv/bin/activate
python wsgi_production.py
```

#### High Memory Usage

```bash
# Check memory usage
ps aux | grep gunicorn

# Reduce workers
# gunicorn.conf.py
workers = 2  # Reduce from 4
```

#### Slow Response Times

```bash
# Enable query logging
# Check Letta server performance
# Enable caching
# Add CDN for static assets
```

#### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Check certificate
openssl s_client -connect your-domain.com:443

# Verify nginx config
sudo nginx -t
```

### Performance Profiling

```python
# Add profiling
from werkzeug.middleware.profiler import ProfilerMiddleware

app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
```

### Debug Mode (Development Only!)

```python
# NEVER use in production
app.config['DEBUG'] = True
```

---

**For more information, see the [main README](../README.md) or [API Documentation](API.md).**

