# Deployment Guide for AI Resume Parser

## 🚀 Quick Deployment Options

### Option 1: Railway (Recommended)

1. **Sign up at [Railway](https://railway.app)**
2. **Connect your GitHub repository**
3. **Deploy with one click** - Railway will automatically detect the configuration
4. **Set environment variables** (if needed):
   ```
   PORT=8080
   PYTHONPATH=/app
   ```

### Option 2: Render

1. **Sign up at [Render](https://render.com)**
2. **Create a new Web Service**
3. **Connect your GitHub repository**
4. **Configure build settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python backend_api.py`
   - Environment: `Python 3`

### Option 3: Heroku

1. **Install Heroku CLI**
2. **Login and create app**:
   ```bash
   heroku login
   heroku create your-resume-parser
   ```
3. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Option 4: Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t resume-parser .
   ```
2. **Run the container**:
   ```bash
   docker run -p 8080:8080 resume-parser
   ```

## 📁 Files Created for Deployment

- `railway.json` - Railway configuration
- `Dockerfile` - Container configuration
- `Procfile` - Process configuration for Heroku
- `runtime.txt` - Python version specification
- `.dockerignore` - Docker ignore patterns
- Updated `requirements.txt` - Added gunicorn for production

## 🔧 Environment Variables

Set these if needed:
- `PORT` - Application port (default: 8080)
- `PYTHONPATH` - Python path (set to `/app` for containers)

## 📱 Frontend Deployment

Your frontend is static HTML/CSS/JS and can be deployed to:
- **Netlify** (recommended for static sites)
- **Vercel**
- **GitHub Pages**
- Or served directly by your backend

## 🔗 Post-Deployment

1. **Update CORS origins** in `backend_api.py` to include your deployed domain
2. **Test the health endpoint**: `https://your-app.com/health`
3. **Update frontend API URLs** to point to your deployed backend

## 🛠️ Troubleshooting

- **Build fails**: Check Python version compatibility
- **Memory issues**: Consider upgrading to a paid tier
- **NLTK data**: May need to download in production (handled automatically)
- **File uploads**: Ensure proper file size limits are set

## 📊 Monitoring

Most platforms provide:
- Application logs
- Performance metrics
- Error tracking
- Uptime monitoring

Choose the platform that best fits your needs and budget!
