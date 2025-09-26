# 🚀 Complete EC2 Deployment Guide for HiLabs Project

## 📋 **What This Project Does**

### **Main APIs Explained:**

1. **`GET /providers`** - Provider Directory
   - Lists all healthcare providers with pagination
   - Shows: Provider ID, NPI, Name, Specialty, License info
   - What you see in your screenshot

2. **`POST /process_csv`** - Upload Provider Data
   - Upload CSV files with provider information
   - Processes and stores data in database

3. **`GET /export/providers/csv`** - Export CSV ✅ **NEW!**
   - Downloads all provider data as CSV file
   - This will make your Export CSV button work!

4. **`POST /query`** - AI-Powered Questions
   - Ask questions like "How many cardiologists are in California?"
   - AI converts to SQL and returns results

5. **`GET /analytics/*`** - Analytics Dashboard
   - Provider distribution by specialty
   - Geographic distribution by state
   - Experience level analytics

6. **`GET /duplicates`** - Find Duplicate Records
   - Identifies potential duplicate provider entries

---

## 🔧 **Export CSV Fix**

I've created the missing export endpoint! After deployment, your Export CSV button will work with:
- **URL**: `GET /export/providers/csv`
- **Downloads**: Complete provider data as CSV file

---

## 🚀 **Step-by-Step EC2 Deployment**

### **STEP 1: Create AWS Account & Launch EC2**

#### 1.1 **AWS Account Setup**
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create AWS Account"
3. Follow signup process (requires credit card, but we'll use free tier)

#### 1.2 **Launch EC2 Instance**
1. **Login to AWS Console**
2. **Search "EC2"** and click on EC2 service
3. **Click "Launch Instance"**

#### 1.3 **Configure Instance**
```
Name: hilabs-backend-server
OS: Ubuntu Server 22.04 LTS (Free tier eligible)
Instance Type: t2.micro (Free tier - 1GB RAM, 1 vCPU)
```

#### 1.4 **Create Key Pair**
1. **Key pair name**: `hilabs-key`
2. **Type**: RSA
3. **Format**: .pem
4. **Click "Create key pair"**
5. **⚠️ IMPORTANT**: Download and save the .pem file securely!

#### 1.5 **Security Group Settings**
```
Security Group Name: hilabs-security-group

Inbound Rules:
- SSH (22)      → My IP (for your access only)
- HTTP (80)     → Anywhere (0.0.0.0/0)
- HTTPS (443)   → Anywhere (0.0.0.0/0)  
- Custom (8000) → Anywhere (0.0.0.0/0) [Backend API]
- Custom (3000) → Anywhere (0.0.0.0/0) [Frontend if needed]
```

#### 1.6 **Storage & Launch**
- **Storage**: 8 GB (Free tier)
- **Click "Launch Instance"**

---

### **STEP 2: Connect to Your Server**

#### 2.1 **Get Your Server IP**
1. Go to **EC2 Dashboard → Instances**
2. Select your instance
3. **Copy the "Public IPv4 address"** (e.g., 3.15.123.45)

#### 2.2 **Connect via SSH**

**Windows (PowerShell):**
```powershell
# Navigate to your key file location
cd C:\Users\YourName\Downloads

# Set file permissions
icacls hilabs-key.pem /inheritance:r /grant:r "%username%:R"

# Connect to server (replace with your IP)
ssh -i hilabs-key.pem ubuntu@3.15.123.45
```

**Mac/Linux (Terminal):**
```bash
# Navigate to key file location
cd ~/Downloads

# Set file permissions
chmod 400 hilabs-key.pem

# Connect to server (replace with your IP)
ssh -i hilabs-key.pem ubuntu@3.15.123.45
```

**✅ Success**: You should see a Ubuntu welcome message!

---

### **STEP 3: Setup Server Environment**

Once connected to your EC2 instance, run these commands:

#### 3.1 **Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

#### 3.2 **Install Docker**
```bash
# Install Docker
sudo apt install docker.io -y

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker ubuntu
```

#### 3.3 **Install Docker Compose**
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose
```

#### 3.4 **Install Git**
```bash
sudo apt install git -y
```

#### 3.5 **Logout and Login Again**
```bash
exit
```

**Then reconnect:**
```bash
ssh -i hilabs-key.pem ubuntu@YOUR_EC2_IP
```

---

### **STEP 4: Upload Your Project**

#### Option A: Using Git (If your code is on GitHub)
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

#### Option B: Upload Files Manually
**On your local machine:**
```bash
# Upload entire project to EC2
scp -i hilabs-key.pem -r /home/ujjwal/Downloads/hilabs-main ubuntu@YOUR_EC2_IP:~/
```

**Then on EC2:**
```bash
cd hilabs-main
```

---

### **STEP 5: Configure Environment**

#### 5.1 **Create Environment File**
```bash
# Copy example file
cp .env.example .env

# Edit environment file
nano .env
```

#### 5.2 **Configure Database Settings**
**In the nano editor, update these values:**
```bash
# Database Configuration (UPDATE THESE!)
DATABASE_HOST=your_database_host_here
DATABASE_PORT=3306
DATABASE_USER=your_username_here
DATABASE_PASSWORD=your_password_here
DATABASE_NAME=demo

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# AI Model Configuration (keep as is)
SQL_MODEL_URL=http://model-runner.docker.internal:12434
SQL_MODEL_NAME=hf.co/unsloth/gemma-3-270m-it-GGUF
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

---

### **STEP 6: Deploy Application**

#### 6.1 **Build and Start**
```bash
# Build and start all services
docker-compose up --build -d

# Check if containers are running
docker-compose ps
```

**Expected output:**
```
NAME                COMMAND             SERVICE    STATUS
fastapi_backend     "python -m app.m…"  backend    running
```

#### 6.2 **Check Logs**
```bash
# View application logs
docker-compose logs -f backend

# If you see errors, check this:
docker-compose logs backend
```

#### 6.3 **Test Your API**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test providers endpoint
curl http://localhost:8000/providers

# Test from outside (replace with your EC2 IP)
curl http://YOUR_EC2_IP:8000/health
```

---

### **STEP 7: Access Your Application**

#### 7.1 **API Endpoints**
- **Backend API**: `http://YOUR_EC2_IP:8000`
- **API Documentation**: `http://YOUR_EC2_IP:8000/docs`
- **Health Check**: `http://YOUR_EC2_IP:8000/health`

#### 7.2 **Test Export CSV**
- **Export All**: `http://YOUR_EC2_IP:8000/export/providers/csv`
- **Export Filtered**: `http://YOUR_EC2_IP:8000/export/providers/csv/filtered?specialty=Cardiology&state=CA`

---

### **STEP 8: Setup Domain (Optional)**

#### 8.1 **Buy Domain**
1. Purchase domain from GoDaddy, Namecheap, etc.
2. In DNS settings, add A record:
   - **Name**: `@` (root domain)
   - **Value**: `YOUR_EC2_IP`
   - **Name**: `api`
   - **Value**: `YOUR_EC2_IP`

#### 8.2 **Install Nginx**
```bash
sudo apt install nginx -y
```

#### 8.3 **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/hilabs
```

**Add this configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 8.4 **Enable Site**
```bash
sudo ln -s /etc/nginx/sites-available/hilabs /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 8.5 **Setup SSL (Free)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

---

### **STEP 9: Deploy Frontend (Separate Server)**

#### 9.1 **Install Node.js**
```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 9.2 **Setup Frontend**
```bash
# Navigate to your frontend code
cd ~/your-frontend-folder

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://YOUR_EC2_IP:8000" > .env.local

# Build application
npm run build

# Start application
npm start
```

---

### **STEP 10: Monitoring & Maintenance**

#### 10.1 **Monitor Application**
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f backend

# Check system resources
htop
df -h
```

#### 10.2 **Restart Services**
```bash
# Restart backend
docker-compose restart backend

# Rebuild and restart
docker-compose up --build -d
```

#### 10.3 **Auto-start on Reboot**
```bash
# Add to startup
crontab -e

# Add this line:
@reboot cd /home/ubuntu/hilabs-main && docker-compose up -d
```

---

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. "Connection Refused"**
```bash
# Check if service is running
docker-compose ps

# Check logs
docker-compose logs backend

# Restart service
docker-compose restart backend
```

#### **2. "Database Connection Failed"**
```bash
# Check environment variables
cat .env

# Test database connection
docker-compose exec backend python -c "from app.config.database import test_db_connection; print(test_db_connection())"
```

#### **3. "Port Already in Use"**
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 PID_NUMBER
```

#### **4. "Permission Denied"**
```bash
# Fix docker permissions
sudo usermod -aG docker ubuntu
# Logout and login again
```

---

## 📊 **Cost Estimation**

### **AWS Free Tier (First 12 months):**
- **EC2 t2.micro**: Free (750 hours/month)
- **Storage**: 30 GB free
- **Data Transfer**: 15 GB free

### **After Free Tier:**
- **EC2 t2.micro**: ~$8-10/month
- **Storage**: ~$3/month (30 GB)
- **Data Transfer**: ~$1-5/month

### **Domain (Optional):**
- **Domain**: $10-15/year
- **SSL**: Free (Let's Encrypt)

---

## ✅ **Success Checklist**

- [ ] EC2 instance launched and accessible
- [ ] Docker and Docker Compose installed
- [ ] Project uploaded to server
- [ ] Environment variables configured
- [ ] Application running on port 8000
- [ ] API accessible from internet
- [ ] Export CSV endpoint working
- [ ] (Optional) Domain configured
- [ ] (Optional) SSL certificate installed
- [ ] (Optional) Frontend deployed

---

## 🎯 **Final Testing**

Once deployed, test these URLs (replace with your IP/domain):

1. **Health Check**: `http://YOUR_EC2_IP:8000/health`
2. **API Docs**: `http://YOUR_EC2_IP:8000/docs`
3. **Providers**: `http://YOUR_EC2_IP:8000/providers`
4. **Export CSV**: `http://YOUR_EC2_IP:8000/export/providers/csv`
5. **Analytics**: `http://YOUR_EC2_IP:8000/analytics/specialty-experience`

**🎉 Congratulations! Your HiLabs project is now live on AWS EC2!**

---

## 📞 **Need Help?**

If you encounter issues:
1. Check the logs: `docker-compose logs backend`
2. Verify environment variables: `cat .env`
3. Test database connection
4. Check security group settings in AWS
5. Ensure all ports are open (22, 80, 443, 8000)

The deployment is now complete and your application should be accessible from anywhere on the internet!
