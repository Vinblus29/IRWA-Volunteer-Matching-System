# Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Intelligent Volunteer Matching System in various environments including development, staging, and production.

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **CPU**: 2+ cores
- **Memory**: 4GB+ RAM (8GB+ recommended for production)
- **Storage**: 20GB+ available space
- **Network**: Internet connectivity for external dependencies

### Required Software
- **Docker**: 20.10+ and Docker Compose 2.0+
- **Node.js**: 18+ (for local development)
- **Python**: 3.11+ (for local development)
- **Git**: Latest version

### External Services
- **MongoDB Atlas**: Database hosting
- **OpenAI API**: AI/LLM services
- **Redis**: Caching and session management
- **Email Service**: SMTP for notifications (optional)

## Environment Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd volunteer-matching-system
```

### 2. Environment Configuration

#### Backend Configuration
Create `backend/.env` from the template:
```bash
cp backend/.env.example backend/.env
```

Update the following variables:
```env
# Database Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_DATABASE=volunteer_matching

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-make-it-long-and-random
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
ALLOWED_HOSTS=your-domain.com,localhost

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@your-domain.com
```

#### Frontend Configuration
Create `frontend/.env` file:
```env
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_APP_NAME=Volunteer Matching System
```

## Development Deployment

### Using Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download required NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# Download spaCy model
python -m spacy download en_core_web_sm

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## Production Deployment

### 1. Server Setup

#### Ubuntu/Debian Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx (for reverse proxy)
sudo apt install nginx -y

# Install Certbot (for SSL)
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Application Deployment

#### Using Deployment Script
```bash
# Make script executable
chmod +x scripts/deploy.sh

# Deploy in production mode
./scripts/deploy.sh production

# Deploy with backup
./scripts/deploy.sh production --backup

# Deploy with data seeding
./scripts/deploy.sh production --seed
```

#### Manual Production Deployment
```bash
# Clone repository
git clone <repository-url>
cd volunteer-matching-system

# Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with production values

# Build and start services
docker-compose -f docker-compose.yml --profile production up -d

# Wait for services to be ready
sleep 30

# Run database migrations
docker-compose exec backend python -c "
import asyncio
from app.database import connect_to_mongo, create_indexes
async def setup():
    await connect_to_mongo()
    await create_indexes()
asyncio.run(setup())
"
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/volunteer-matching`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Documentation
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/volunteer-matching /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. SSL Certificate Setup
```bash
# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Cloud Deployment

### AWS EC2 Deployment

#### 1. Launch EC2 Instance
- AMI: Ubuntu 20.04 LTS
- Instance Type: t3.medium (minimum)
- Security Group: Allow HTTP (80), HTTPS (443), SSH (22)
- Storage: 20GB+ EBS volume

#### 2. Setup Script
```bash
#!/bin/bash
# User data script for EC2

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Nginx
apt install nginx -y

# Clone application
cd /home/ubuntu
git clone <repository-url>
chown -R ubuntu:ubuntu volunteer-matching-system
```

### Google Cloud Platform (GCP)

#### Using Cloud Run
```yaml
# cloudbuild.yaml
steps:
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/volunteer-backend', './backend']
  
  # Build frontend  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/volunteer-frontend', './frontend']
  
  # Push images
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/volunteer-backend']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/volunteer-frontend']
```

Deploy to Cloud Run:
```bash
# Backend
gcloud run deploy volunteer-backend \
  --image gcr.io/$PROJECT_ID/volunteer-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Frontend
gcloud run deploy volunteer-frontend \
  --image gcr.io/$PROJECT_ID/volunteer-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
# Create resource group
az group create --name volunteer-matching --location eastus

# Deploy backend
az container create \
  --resource-group volunteer-matching \
  --name volunteer-backend \
  --image your-registry/volunteer-backend:latest \
  --dns-name-label volunteer-backend \
  --ports 8000

# Deploy frontend
az container create \
  --resource-group volunteer-matching \
  --name volunteer-frontend \
  --image your-registry/volunteer-frontend:latest \
  --dns-name-label volunteer-frontend \
  --ports 3000
```

## Kubernetes Deployment

### 1. Kubernetes Manifests

#### Backend Deployment
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: volunteer-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: volunteer-backend
  template:
    metadata:
      labels:
        app: volunteer-backend
    spec:
      containers:
      - name: backend
        image: volunteer-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: mongodb-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: openai-api-key
---
apiVersion: v1
kind: Service
metadata:
  name: volunteer-backend-service
spec:
  selector:
    app: volunteer-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

#### Frontend Deployment
```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: volunteer-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: volunteer-frontend
  template:
    metadata:
      labels:
        app: volunteer-frontend
    spec:
      containers:
      - name: frontend
        image: volunteer-frontend:latest
        ports:
        - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: volunteer-frontend-service
spec:
  selector:
    app: volunteer-frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
```

#### Ingress Configuration
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: volunteer-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: volunteer-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: volunteer-backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: volunteer-frontend-service
            port:
              number: 3000
```

### 2. Deploy to Kubernetes
```bash
# Create secrets
kubectl create secret generic app-secrets \
  --from-literal=mongodb-url="your-mongodb-url" \
  --from-literal=openai-api-key="your-openai-key"

# Apply manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services
kubectl get ingress
```

## Monitoring and Logging

### 1. Health Checks
The application provides health check endpoints:
- Backend: `GET /health`
- Frontend: `GET /` (should return 200)

### 2. Application Monitoring

#### Docker Compose Monitoring
```yaml
# Add to docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

#### Log Aggregation
```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Export logs to file
docker-compose logs backend > backend.log
```

### 3. Performance Monitoring

#### Backend Metrics
- API response times
- Database query performance
- AI agent processing times
- Memory and CPU usage

#### Frontend Metrics
- Page load times
- JavaScript errors
- User interactions
- Bundle size analysis

## Backup and Disaster Recovery

### 1. Database Backup
```bash
# MongoDB backup
mongodump --uri="mongodb+srv://username:password@cluster.mongodb.net/volunteer_matching" --out=backup/

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
mongodump --uri="$MONGODB_URL" --out="$BACKUP_DIR"
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"
```

### 2. Application Backup
```bash
# Backup application data
docker-compose exec backend python scripts/backup_data.py

# File system backup
tar -czf app_backup_$(date +%Y%m%d).tar.gz \
  --exclude=node_modules \
  --exclude=__pycache__ \
  --exclude=.git \
  volunteer-matching-system/
```

### 3. Restore Procedures
```bash
# Restore database
mongorestore --uri="mongodb+srv://username:password@cluster.mongodb.net/volunteer_matching" backup/volunteer_matching/

# Restore application
tar -xzf app_backup_20240101.tar.gz
cd volunteer-matching-system
./scripts/deploy.sh production
```

## Security Considerations

### 1. Environment Security
- Use strong, unique passwords
- Enable firewall (UFW on Ubuntu)
- Regular security updates
- Disable root SSH access
- Use SSH keys instead of passwords

### 2. Application Security
- HTTPS enforcement
- Secure headers configuration
- Input validation
- Rate limiting
- Regular dependency updates

### 3. Database Security
- MongoDB Atlas security features
- Connection string encryption
- Access control lists
- Regular security audits

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check container logs
docker-compose logs <service-name>

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart <service-name>
```

#### 2. Database Connection Issues
```bash
# Test MongoDB connection
docker-compose exec backend python -c "
import asyncio
from app.database import connect_to_mongo
asyncio.run(connect_to_mongo())
print('Database connection successful')
"
```

#### 3. API Not Responding
```bash
# Check backend health
curl http://localhost:8000/health

# Check container networking
docker network ls
docker network inspect volunteer-matching-system_default
```

#### 4. Frontend Build Issues
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check build logs
npm run build
```

### Performance Issues

#### 1. Slow Database Queries
- Check MongoDB indexes
- Analyze query patterns
- Optimize aggregation pipelines

#### 2. High Memory Usage
- Monitor container resource usage
- Adjust container memory limits
- Optimize AI model loading

#### 3. API Response Times
- Enable response caching
- Optimize database queries
- Scale horizontally with load balancer

## Scaling

### Horizontal Scaling
```yaml
# Scale with Docker Compose
version: '3.8'
services:
  backend:
    build: ./backend
    deploy:
      replicas: 3
    
  frontend:
    build: ./frontend
    deploy:
      replicas: 2
```

### Load Balancing
```nginx
# Nginx load balancer configuration
upstream backend_servers {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api/ {
        proxy_pass http://backend_servers;
    }
}
```

### Auto Scaling (Kubernetes)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: volunteer-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Maintenance

### Regular Tasks
1. **Daily**: Monitor logs and metrics
2. **Weekly**: Update dependencies, backup data
3. **Monthly**: Security patches, performance review
4. **Quarterly**: Full system backup, disaster recovery test

### Update Procedures
```bash
# Update application
git pull origin main
docker-compose build --no-cache
docker-compose up -d

# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d
```

This deployment guide provides comprehensive instructions for deploying the Intelligent Volunteer Matching System across various environments and platforms. Choose the deployment method that best fits your infrastructure requirements and technical expertise. 