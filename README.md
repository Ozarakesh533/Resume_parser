# 🤖 AI Resume Parser Pro

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


**Developed by: Rakesh Oza**  
*AI & Machine Learning Engineer*

A powerful, intelligent resume parsing application that uses advanced AI to extract and analyze resume data with neural network precision.

## 🚀 Live Demo

**🌐 Try it now:** [https://resumeparserbyrakesh.netlify.app/](https://resumeparserbyrakesh.netlify.app/)

## 🎥 Video
https://github.com/user-attachments/assets/6f94402b-ca27-467f-a24a-77a2de35ab88

## 🏗️ Architecture

This is a full-stack application with:

- **Frontend**: Modern AI-themed web interface deployed on Netlify
- **Backend**: FastAPI-powered REST API deployed on Railway
- **AI Engine**: Advanced resume parsing with machine learning

## 🌟 Features

### 🎨 Frontend Features
- **AI-Themed UI**: Futuristic design with neural network animations
- **Drag & Drop Upload**: Intuitive file upload interface
- **Real-time Processing**: Live progress tracking with AI status indicators
- **Multi-file Support**: Process multiple resumes simultaneously
- **Interactive Results**: Detailed analysis with modal views
- **Export Functionality**: Download parsed data as JSON
- **Responsive Design**: Works on all devices
- **Quantum Processing Effects**: Beautiful loading animations

### 🔧 Backend Features
- **FastAPI Framework**: High-performance async API
- **Multiple File Formats**: PDF, DOCX, TXT, RTF support
- **AI Processing**: Advanced text extraction and analysis
- **RESTful API**: Clean, documented endpoints
- **CORS Enabled**: Cross-origin request support
- **Health Monitoring**: Built-in health check endpoints

## 🛠️ Tech Stack

### Frontend
- **HTML5/CSS3/JavaScript**: Modern vanilla web technologies
- **Font Awesome**: Icon library
- **Google Fonts**: Orbitron & Rajdhani fonts
- **CSS Animations**: Hardware-accelerated transitions
- **Netlify**: Static site hosting

### Backend
- **Python**: Core programming language
- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Railway**: Cloud deployment platform
- **AI Libraries**: Resume processing engine

## 🚀 Deployment

### Live URLs
- **Frontend (Netlify)**: https://resumeparserbyrakesh.netlify.app/
- **Backend (Railway)**: https://web-production-33afa.up.railway.app/

### Deployment Configuration

#### Frontend (Netlify)
```toml
# netlify.toml
[build]
  publish = "."
  
[build.environment]
  NODE_VERSION = "18"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

#### Backend (Railway)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python backend_api.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## 📋 API Endpoints

### Base URL: `https://web-production-33afa.up.railway.app`

- **GET** `/` - API status and health check
- **POST** `/parse-resume` - Upload and parse resume files
- **GET** `/health` - Health check endpoint

## 🎯 Usage

1. **Visit**: [https://resumeparserbyrakesh.netlify.app/](https://resumeparserbyrakesh.netlify.app/)
2. **Upload**: Drag and drop resume files or click to browse
3. **Process**: Click "Initialize AI Processing" to start analysis
4. **Results**: View detailed parsing results with AI insights
5. **Export**: Download results as JSON for further use

## 📁 Project Structure

```
Resume_parser/
├── frontend/                 # Netlify deployment
│   ├── index.html           # Main web interface
│   ├── script.js            # AI processing logic
│   ├── styles.css           # Futuristic styling
│   ├── netlify.toml         # Netlify configuration
│   └── README.md            # Frontend documentation
├── backend_api.py           # Railway FastAPI server
├── resume_final.py          # AI processing engine
├── railway.json             # Railway configuration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── README.md               # This file
```

## 🔧 Local Development

### Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python backend_api.py
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Serve locally (optional)
python -m http.server 3000
```

## 📊 Response Format

```json
{
  "personalInfo": {
    "name": "John Doe",
    "email": "john.doe@email.com",
    "phone": "+1-234-567-8900",
    "location": "New York, NY",
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe"
  },
  "skills": ["Python", "JavaScript", "React", "FastAPI"],
  "total_experience": "5 years and 3 months",
  "summary": "Experienced software developer...",
  "experience": "Senior Developer at Tech Corp...",
  "education": "BS Computer Science, MIT",
  "metadata": {
    "filename": "resume.pdf",
    "file_size": 245760,
    "processing_status": "success"
  }
}
```
## 🌐 CORS Configuration

The backend is configured to accept requests from:
- `https://resumeparserbyrakesh.netlify.app` (Production)
- `http://localhost:3000` (Local development)
- `http://127.0.0.1:8080` (Local backend testing)

## 🔒 Security Features

- **File Validation**: Type and size restrictions
- **CORS Protection**: Configured allowed origins
- **Input Sanitization**: Safe file processing
- **Error Handling**: Comprehensive error management
- **Security Headers**: Netlify security configuration

## 📊 Performance

- **Fast Processing**: Optimized AI algorithms
- **Scalable Architecture**: Cloud-native deployment
- **Responsive UI**: Hardware-accelerated animations
- **Efficient API**: Async FastAPI framework

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Developer

**Rakesh Oza**  
*AI & Machine Learning Engineer*

- 🌐 **Live App**: [Resume_parser](https://resumeparserbyrakesh.netlify.app/)
- 📧 **Contact**: ozarakesh533@gmail.com
- 💼 **LinkedIn**:[Linkedin](https://www.linkedin.com/in/rakeshoza/)
- 🐙 **GitHub**: [Github](https://github.com/Ozarakesh533)

## 🆘 Support

For support and questions:
1. Check the troubleshooting section in `/frontend/README.md`
2. Test the API endpoints directly
3. Open an issue in the repository
4. Contact the development team

---

**© 2024 AI Resume Parser Pro - Rakesh Oza. All rights reserved.**

*Powered by Advanced AI Neural Networks* 🧠✨
