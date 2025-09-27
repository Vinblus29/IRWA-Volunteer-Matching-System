# 🐳 Docker Setup Guide for Volunteer Matching System

## 📋 Prerequisites

### Install Docker Desktop (Windows)

1. **Download Docker Desktop**:
   - Visit: https://www.docker.com/products/docker-desktop
   - Download Docker Desktop for Windows
   - File size: ~500MB

2. **System Requirements**:
   - Windows 10 64-bit: Pro, Enterprise, or Education
   - WSL 2 backend support
   - At least 4GB RAM
   - Virtualization enabled in BIOS

3. **Installation Steps**:
   ```bash
   # 1. Download and run Docker Desktop Installer.exe
   # 2. Follow the installation wizard
   # 3. Restart your computer when prompted
   # 4. Start Docker Desktop from Start Menu
   ```

4. **Verify Installation**:
   ```bash
   docker --version
   docker-compose --version
   ```

## 🚀 Quick Start (Easiest Method)

### Option 1: Full Docker Setup
```bash
# 1. Clone and navigate to project
cd K:\Volunteer-Matching_system

# 2. Set environment variable (replace with your actual OpenAI key)
set OPENAI_API_KEY=sk-proj-your-openai-api-key

# 3. Build and start all services
docker-compose up --build

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Development Mode (Recommended for Testing)
```bash
# Start only backend services (database, cache)
docker-compose up redis -d

# Run backend manually
cd backend
pip install -r requirements.txt
set OPENAI_API_KEY=sk-proj-your-openai-api-key
python -m uvicorn app.main:app --reload

# Run frontend manually (in new terminal)
cd frontend
npm install
npm start
```

## 🛠️ Alternative Setup (No Docker Required)

If Docker installation fails, you can run the system manually:

### Backend Setup
```bash
# 1. Install Python 3.11+
# Download from: https://www.python.org/downloads/

# 2. Navigate to backend
cd backend

# 3. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# 6. Set environment variables
copy env.config .env
# Edit .env file with your credentials

# 7. Start backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# 1. Install Node.js 18+
# Download from: https://nodejs.org/

# 2. Navigate to frontend
cd frontend

# 3. Install dependencies
npm install

# 4. Set environment variables
copy env.config .env
# Edit .env file if needed

# 5. Start frontend
npm start
```

## 🔧 Docker Compose Services

### Services Overview
```yaml
✅ backend:8000     # FastAPI Python backend
✅ frontend:3000    # React TypeScript frontend  
✅ redis:6379       # Redis cache/queue
✅ nginx:80         # Reverse proxy (production)
```

### Development vs Production

**Development Mode:**
```bash
# Start development services
docker-compose up backend frontend redis

# Features:
# - Hot reload enabled
# - Debug mode on
# - Source code mounted as volumes
# - API docs available
```

**Production Mode:**
```bash
# Start production services
docker-compose --profile production up

# Features:
# - Nginx reverse proxy
# - SSL/HTTPS support
# - Optimized builds
# - Health checks enabled
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Docker Not Starting
```bash
# Check Docker Desktop is running
# Look for Docker icon in system tray

# Restart Docker Desktop
# Right-click Docker icon → Restart

# Check WSL 2 (Windows)
wsl --list --verbose
wsl --set-default-version 2
```

#### 2. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill process using port
taskkill /PID <process_id> /F

# Or use different ports
docker-compose -f docker-compose.yml up --build
```

#### 3. Build Failures
```bash
# Clean Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

#### 4. Database Connection Issues
```bash
# Check MongoDB Atlas connection
# Verify IP address is whitelisted
# Check credentials in .env file

# Test connection manually
python -c "
import pymongo
client = pymongo.MongoClient('your-mongodb-url')
print('Connected:', client.admin.command('ping'))
"
```

#### 5. Frontend Not Loading
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check frontend build
docker-compose logs frontend

# Clear browser cache
# Ctrl + F5 (hard refresh)
```

#### 6. Missing Dependencies
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies  
cd frontend
npm install

# System dependencies (Ubuntu/WSL)
sudo apt update
sudo apt install python3-dev build-essential
```

## 📊 Service Health Checks

### Backend Health
```bash
# API health check
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "agents": "running"
}
```

### Frontend Health
```bash
# Frontend health check
curl http://localhost:3000

# Should return React app HTML
```

### Redis Health
```bash
# Redis health check
docker exec -it volunteer-matching-system_redis_1 redis-cli ping

# Expected response: PONG
```

## 🔐 Environment Configuration

### Required Environment Variables

**Backend (.env):**
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
OPENAI_API_KEY=sk-proj-your-openai-api-key
JWT_SECRET_KEY=your-secret-key
ENVIRONMENT=development
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## 🚀 Deployment Options

### Local Development
```bash
docker-compose up --build
```

### Cloud Deployment
```bash
# AWS ECS
# Google Cloud Run  
# Azure Container Instances
# DigitalOcean App Platform
```

### Manual Deployment
```bash
# Build images
docker build -t volunteer-backend ./backend
docker build -t volunteer-frontend ./frontend

# Push to registry
docker push your-registry/volunteer-backend
docker push your-registry/volunteer-frontend
```

## 📝 Logs and Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Recent logs only
docker-compose logs --tail=50 backend
```

### Performance Monitoring
```bash
# Container stats
docker stats

# System usage
docker system df

# Clean up unused resources
docker system prune
```

## 🆘 Emergency Quick Start

If everything fails, use this minimal setup:

```bash
# 1. Start only the database (use MongoDB Atlas)
# 2. Run backend manually:
cd backend
pip install fastapi uvicorn pymongo python-dotenv
set MONGODB_URL=your-atlas-url
set OPENAI_API_KEY=your-key
python -c "
from app.main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8000)
"

# 3. Run frontend manually:
cd frontend  
npx create-react-app temp-app
# Copy src files to temp-app/src
cd temp-app && npm start
```

## 🎯 Success Indicators

✅ **Backend Running**: http://localhost:8000/docs shows API documentation
✅ **Frontend Running**: http://localhost:3000 shows login page  
✅ **Database Connected**: API health check returns "connected"
✅ **AI Working**: Can create volunteer profiles and get matches
✅ **Authentication Working**: Can register and login users

## 📞 Support

If you're still having issues:

1. **Check logs**: `docker-compose logs`
2. **Restart services**: `docker-compose restart`
3. **Clean rebuild**: `docker-compose down && docker-compose up --build`
4. **Manual setup**: Follow the non-Docker instructions above
5. **Check system requirements**: Ensure you have enough RAM and disk space

The system is designed to work even without Docker by running services manually! 