# Quick Start Guide

## ✅ Frontend Setup Complete!

Frontend dependencies have been installed successfully.

## 🚀 Start the Application

### Option 1: Start Frontend Only (Recommended for UI Development)

```bash
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:3000**

### Option 2: Start Both Frontend and Backend

```bash
./start.sh
```

This will start:
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:3000

## 📋 Backend Setup (Required for Full Functionality)

The backend requires additional setup:

### 1. Install Python Dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

**Note:** Some packages may require additional setup:
- `pyspark` - Requires Java/JDK
- `databricks-sdk` - Requires `~/.databrickscfg` configuration

### 2. Configure Databricks

Ensure `~/.databrickscfg` is configured:
```bash
databricks configure --token
```

### 3. Setup Unity Catalog (One-time)

```bash
cd backend
python3 scripts/setup_unity_catalog.py
```

### 4. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

Backend API will be at: **http://localhost:8000**
API Docs: **http://localhost:8000/api/docs**

## 🧪 Testing

### Frontend Only (UI Testing)
- Frontend will run but API calls will fail without backend
- Good for UI/UX development and testing

### Full Stack Testing
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: http://localhost:3000
4. Test API integration

## 📝 Current Status

✅ **Frontend**: Ready to run (`npm run dev`)
⏳ **Backend**: Requires dependency installation
⏳ **Databricks**: Requires `~/.databrickscfg` configuration
⏳ **Unity Catalog**: Requires one-time setup

## 🐛 Troubleshooting

### Frontend Issues
- Port 3000 already in use? Change port in `vite.config.ts`
- Module not found? Run `npm install` again

### Backend Issues
- Import errors? Install dependencies: `pip3 install -r requirements.txt`
- Databricks connection errors? Check `~/.databrickscfg`
- Database errors? Run Unity Catalog setup script

## 📚 Documentation

- Frontend README: `frontend/README.md`
- Backend Testing: `docs/TESTING.md`
- Deployment: `docs/DEPLOYMENT.md`
- Databricks Apps: `docs/DATABRICKS_APPS.md`

