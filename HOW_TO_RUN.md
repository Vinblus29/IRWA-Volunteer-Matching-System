# 🚀 How to Run Backend & Frontend

## 🎯 **EASIEST METHOD - One Click Start**

### **Just double-click this file:**
```
START_SYSTEM.bat
```
**Done!** The system will start automatically and open in your browser.

---

## 🔧 **Manual Method (Step by Step)**

### **Prerequisites:**
- **Python 3.8+** - Download from https://python.org/downloads/
- **Node.js 16+** - Download from https://nodejs.org/

### **Step 1: Start Backend (Terminal 1)**

```bash
# 1. Open Command Prompt or PowerShell
# 2. Navigate to project directory
cd K:\Volunteer-Matching_system\backend

# 3. Create virtual environment (first time only)
python -m venv venv

# 4. Activate virtual environment
venv\Scripts\activate

# 5. Install dependencies (first time only)
pip install -r requirements.txt

# 6. Set environment variables
set MONGODB_URL=mongodb+srv://aivolunteer:aRZH1TmJP65LfXCe@cluster0.mqjdi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
set OPENAI_API_KEY=sk-proj-KzfYmFuHvV2-wQxVtGt0wKLdyMf9Bf_5WPYb8U3OW-5TG6kN8vLJ2WUQFdT5hSTdPM2KqWtT3BlbkFJlOEWvNYcRr1sOPfhJKx9JZiPe3rKvM1cFGk7_YWQJ1OdFbMq6rBvS8hKy
set JWT_SECRET_KEY=volunteer-matching-super-secret-jwt-key-2024
set ENVIRONMENT=development

# 7. Start backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Backend will start at: http://localhost:8000**

### **Step 2: Start Frontend (Terminal 2)**

```bash
# 1. Open NEW Command Prompt or PowerShell
# 2. Navigate to frontend directory
cd K:\Volunteer-Matching_system\frontend

# 3. Install dependencies (first time only)
npm install

# 4. Set environment variable
set REACT_APP_API_URL=http://localhost:8000

# 5. Start frontend server
npm start
```

**✅ Frontend will start at: http://localhost:3000**

---

## 🌐 **Access Your Application**

Once both servers are running:

- **🖥️ Main Application**: http://localhost:3000
- **🔗 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **⚡ Health Check**: http://localhost:8000/health

---

## 🐳 **Docker Method (if Docker is installed)**

```bash
# From project root
cd K:\Volunteer-Matching_system

# Set environment variable
set OPENAI_API_KEY=sk-proj-your-openai-key

# Start everything
docker-compose up --build
```

---

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **1. Python not found**
```bash
# Install Python from https://python.org/downloads/
# Make sure to check "Add Python to PATH" during installation
```

#### **2. Node.js not found**
```bash
# Install Node.js from https://nodejs.org/
# Download the LTS version
```

#### **3. Port already in use**
```bash
# Kill process using the port
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Or use different port
python -m uvicorn app.main:app --reload --port 8001
```

#### **4. Dependencies installation fails**
```bash
# Backend: Upgrade pip first
python -m pip install --upgrade pip
pip install -r requirements.txt

# Frontend: Clear cache
npm cache clean --force
npm install
```

#### **5. Database connection error**
```bash
# Check if MongoDB Atlas URL is correct
# Verify internet connection
# Check if IP address is whitelisted in MongoDB Atlas
```

---

## 📋 **Quick Commands Reference**

### **Backend Commands:**
```bash
cd backend
venv\Scripts\activate                           # Activate environment
python -m uvicorn app.main:app --reload         # Start server
pip install -r requirements.txt                 # Install dependencies
python -c "import app.main; print('OK')"        # Test import
```

### **Frontend Commands:**
```bash
cd frontend
npm install                                      # Install dependencies
npm start                                        # Start server
npm run build                                    # Build for production
npm test                                         # Run tests
```

### **Docker Commands:**
```bash
docker-compose up --build                       # Build and start
docker-compose down                              # Stop services
docker-compose logs backend                     # View backend logs
docker-compose logs frontend                    # View frontend logs
```

---

## ⚡ **Super Quick Start**

**For the fastest setup:**

1. **Double-click `START_SYSTEM.bat`**
2. **Choose option 2 (Manual mode)**
3. **Wait 2-3 minutes**
4. **Browser opens automatically**

That's it! The system handles everything automatically.

---

## 🎯 **Success Indicators**

**Backend is ready when you see:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Frontend is ready when you see:**
```
webpack compiled successfully
Local:            http://localhost:3000
On Your Network:  http://192.168.x.x:3000
```

**Both ready when browser opens to the login page!**

---

## 📞 **Need Help?**

If you run into any issues:

1. **Use the automatic script**: `START_SYSTEM.bat`
2. **Check the logs** in the terminal windows
3. **Verify prerequisites** are installed
4. **Check ports** aren't being used by other applications
5. **Restart your computer** if needed

**The system is designed to work out of the box! 🚀** 