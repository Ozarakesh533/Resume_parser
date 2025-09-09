# 🤖 AI Resume Parser Pro

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


An advanced AI-powered resume parsing system that extracts structured information from PDF, DOCX, TXT, and RTF resume files. Built with FastAPI backend and modern web frontend, featuring intelligent text extraction, contact information parsing, and skills analysis.

## 🎥 Video
https://github.com/user-attachments/assets/6f94402b-ca27-467f-a24a-77a2de35ab88

## 🌟 Features

### 🔍 **Intelligent Resume Parsing**
- **Multi-format Support**: PDF, DOCX, TXT, RTF files
- **Advanced Text Extraction**: Dual-engine approach using PyMuPDF and pdfplumber
- **Smart Name Detection**: Enhanced algorithms for accurate name extraction
- **Contact Information**: Email, phone, LinkedIn, GitHub, location extraction
- **Skills Analysis**: Comprehensive technical and soft skills identification
- **Experience Calculation**: Automatic work experience duration calculation

### 🚀 **Modern Web Interface**
- **AI-themed UI**: Futuristic design with neural network animations
- **Drag & Drop**: Intuitive file upload interface
- **Real-time Processing**: Live progress tracking with AI confidence metrics
- **Batch Processing**: Multiple resume analysis in one go
- **Export Functionality**: Download results as JSON

### 🔧 **Robust API**
- **RESTful Endpoints**: Clean and documented API
- **Health Monitoring**: Built-in health checks
- **CORS Support**: Cross-origin resource sharing enabled
- **Error Handling**: Comprehensive error management
- **File Validation**: Secure file type and size validation

## 🏗️ Project Structure

```
ai-resume-parser/
├── 📁 frontend/                 # Modern web interface
│   ├── index.html              # Main HTML file
│   ├── styles.css              # AI-themed styling
│   └── script.js               # Interactive JavaScript
├── 📁 Resumes/                 # Sample resume files
├── 📄 backend_api.py           # FastAPI application
├── 📄 resume_final.py          # Core parsing engine
├── 📄 serve_frontend.py        # Frontend server
├── 📄 requirements.txt         # Python dependencies
├── 📄 Dockerfile              # Container configuration
├── 📄 railway.json             # Railway deployment config
├── 📄 Procfile                 # Heroku deployment config
└── 📄 DEPLOYMENT.md            # Deployment guide
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/Ozarakesh533/ai-resume-parser.git
cd ai-resume-parser
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
# Start backend API
python backend_api.py

# In another terminal, start frontend (optional)
python serve_frontend.py
```

### 4. Access the Application
- **API**: http://127.0.0.1:8080
- **Frontend**: http://127.0.0.1:3000
- **API Docs**: http://127.0.0.1:8080/docs

## 📡 API Endpoints

### Health Check
```http
GET /health
```
Returns API status and health information.

### Single Resume Parsing
```http
POST /parse-resume
Content-Type: multipart/form-data

{
  "file": "resume.pdf"
}
```

### Batch Resume Parsing
```http
POST /parse-multiple
Content-Type: multipart/form-data

{
  "files": ["resume1.pdf", "resume2.pdf"]
}
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

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker build -t ai-resume-parser .

# Run container
docker run -p 8080:8080 ai-resume-parser
```

## ☁️ Cloud Deployment

### Railway (Recommended)
1. Fork this repository
2. Connect to [Railway](https://railway.app)
3. Deploy automatically with `railway.json` config

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

### Render
1. Connect repository to [Render](https://render.com)
2. Use `Dockerfile` for deployment

## 🧪 Testing

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8080/health

# Test resume parsing
curl -F "file=@sample_resume.pdf" http://localhost:8080/parse-resume
```

### Load Testing
```bash
# Multiple file upload
curl -F "files=@resume1.pdf" -F "files=@resume2.pdf" http://localhost:8080/parse-multiple
```

## 🔧 Configuration

### Environment Variables
```bash
PORT=8080                    # Application port
PYTHONPATH=/app             # Python path for containers
MAX_FILE_SIZE=10485760      # Max file size (10MB)
```

### Supported File Types
- **PDF**: Advanced text extraction with PyMuPDF and pdfplumber
- **DOCX**: Microsoft Word documents
- **TXT**: Plain text files
- **RTF**: Rich Text Format files

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyMuPDF** and **pdfplumber** for PDF text extraction
- **FastAPI** for the robust web framework
- **NLTK** for natural language processing
- **Railway** for seamless deployment

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Ozarakesh533/ai-resume-parser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Ozarakesh533/ai-resume-parser/discussions)

---

<div align="center">
  <strong>Built with ❤️ for the developer community by Rakesh Oza</strong>
</div>
