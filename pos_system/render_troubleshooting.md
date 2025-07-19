# 🔧 Render.com Build Failure Troubleshooting

## Common Build Failures & Solutions

### 1. **Python Version Issues**
**Error**: `Python version not found`
**Solution**: 
- Update `runtime.txt` to: `python-3.10.12`
- Or remove `runtime.txt` entirely (Render will auto-detect)

### 2. **Missing Dependencies**
**Error**: `ModuleNotFoundError`
**Solution**: 
- Make sure `requirements.txt` has all dependencies
- Check that all imports in `app.py` are listed in requirements

### 3. **Port Issues**
**Error**: `Port already in use`
**Solution**: 
- The app already uses `os.environ.get('PORT')` - this is correct

### 4. **Database Issues**
**Error**: `Database locked` or `Permission denied`
**Solution**: 
- SQLite works fine on Render
- Database will be created automatically

## 🔍 **How to Check Build Logs**

1. **In Render dashboard**, click on your service
2. **Go to "Logs" tab**
3. **Look for red error messages**
4. **Copy the exact error** and check below

## 🛠️ **Quick Fixes to Try**

### Fix 1: Update requirements.txt
```txt
Flask==2.3.3
Flask-SocketIO==5.3.6
python-socketio==5.8.0
python-engineio==4.7.1
Werkzeug==2.3.7
eventlet==0.33.3
gunicorn==21.2.0
```

### Fix 2: Update Procfile
```
web: python app.py
```

### Fix 3: Remove runtime.txt
Delete the `runtime.txt` file entirely

### Fix 4: Check Build Command
Make sure it's: `pip install -r requirements.txt`

### Fix 5: Check Start Command
Make sure it's: `python app.py`

## 📋 **What to Tell Me**

If build still fails, tell me:
1. **The exact error message** from the logs
2. **Which step failed** (build or deploy)
3. **Any red text** in the logs

## 🚀 **Alternative: Railway.app**

If Render keeps failing:
1. Go to https://railway.app
2. Connect your GitHub repo
3. Railway auto-detects Python apps
4. Usually works without issues

## ✅ **Success Indicators**

When it works, you'll see:
- ✅ Build completed successfully
- ✅ Service is live
- ✅ URL like: `https://your-app.onrender.com` 