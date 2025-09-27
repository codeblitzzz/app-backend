# 🚀 Quick Setup Guide - Fixed Version

## ✅ **What I Fixed**

1. **Removed Export Feature** - The export functionality was causing crashes
2. **Fixed Gitignore** - Proper environment file handling
3. **Updated Deployment Script** - Better error handling and checks
4. **Created .env.example** - Template for environment variables

---

## 📋 **Step-by-Step Setup**

### **Step 1: Fix Your Local Environment**

```bash
cd /home/ujjwal/Downloads/hilabs-main

# Create proper .env file from template
cp .env.example .env

# Edit .env with your actual database credentials
nano .env
```

**Update these values in .env:**
```bash
DATABASE_HOST=admin.c9sumkiag01s.eu-north-1.rds.amazonaws.com
DATABASE_PORT=3306
DATABASE_USER=bpadmin
DATABASE_PASSWORD=Qwerty1234
DATABASE_NAME=demo
```

### **Step 2: Test Backend Locally**

```bash
# Stop any running containers
docker-compose down

# Rebuild and start (this should work now)
docker-compose up --build

# In another terminal, test the API
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "healthy", "timestamp": "..."}
```

### **Step 3: Prepare for Git Repository**

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Fixed backend - removed export feature"

# Create repository on GitHub, then:
git remote add origin https://github.com/yourusername/hilabs-backend.git
git push -u origin main
```

---

## 🚀 **EC2 Deployment Steps**

### **Step 1: Connect to EC2**

```bash
# On your local machine
chmod 400 your-key-name.pem
ssh -i your-key-name.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### **Step 2: Setup EC2 Environment**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt install git -y

# Logout and login again
exit
```

**Reconnect:**
```bash
ssh -i your-key-name.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### **Step 3: Clone and Deploy**

```bash
# Clone your repository
git clone https://github.com/yourusername/hilabs-backend.git hilabs-main
cd hilabs-main

# Create environment file
cp .env.example .env
nano .env
```

**Update .env with your database credentials:**
```bash
DATABASE_HOST=admin.c9sumkiag01s.eu-north-1.rds.amazonaws.com
DATABASE_PORT=3306
DATABASE_USER=bpadmin
DATABASE_PASSWORD=Qwerty1234
DATABASE_NAME=demo
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

### **Step 4: Deploy**

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

---

## 🔍 **Testing Your Deployment**

### **Local Testing:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/providers
curl http://localhost:8000/docs
```

### **EC2 Testing:**
```bash
# Replace YOUR_EC2_IP with actual IP
curl http://YOUR_EC2_IP/health        # If using port 80
curl http://YOUR_EC2_IP:8000/health   # If using port 8000
```

---

## 🔧 **Available APIs (Working)**

1. **Health Check**: `GET /health`
2. **Providers**: `GET /providers` 
3. **Upload CSV**: `POST /process_csv`
4. **AI Query**: `POST /query`
5. **Analytics**: `GET /analytics/*`
6. **Duplicates**: `GET /duplicates`
7. **API Docs**: `GET /docs`

---

## ❌ **Removed Features**

- **Export CSV**: Removed due to import errors
- **Export endpoints**: `/export/*` no longer available

---

## 🚨 **If You Get Errors**

### **Backend Won't Start:**
```bash
# Check logs
docker-compose logs backend

# Common fixes:
# 1. Check .env file exists and has correct values
# 2. Ensure database credentials are correct
# 3. Try rebuilding: docker-compose up --build
```

### **Import Errors:**
```bash
# The export feature has been completely removed
# If you still see export-related errors:
grep -r "export" backend/app/
# Should return no results
```

### **Deployment Script Fails:**
```bash
# Check if you're in the right directory
pwd  # Should show /home/ubuntu/hilabs-main or similar

# Check if .env exists
ls -la .env

# Check git status
git status
```

---

## ✅ **Success Indicators**

- ✅ `docker-compose ps` shows backend running
- ✅ `curl http://localhost:8000/health` returns JSON
- ✅ No import errors in logs
- ✅ API documentation accessible at `/docs`

---

## 🎯 **Next Steps After Success**

1. **Setup CI/CD** with GitHub Actions
2. **Deploy Frontend** to Vercel
3. **Configure Domain** (optional)
4. **Setup SSL** (optional)

The backend should now work properly without the problematic export feature!
