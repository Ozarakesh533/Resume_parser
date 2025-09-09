# Resume Parser Pro - Frontend

A beautiful, modern, and responsive web frontend for the Resume Parser API built with vanilla HTML, CSS, and JavaScript.

## ✨ Features

- **Modern UI/UX**: Beautiful gradient design with glassmorphism effects
- **Drag & Drop**: Intuitive file upload with drag and drop support
- **Multiple File Support**: Upload and parse multiple resume files simultaneously
- **Real-time Progress**: Visual progress indication during parsing
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Interactive Results**: Click on result cards to view detailed information
- **Export Functionality**: Download all results as JSON file
- **Notifications**: Toast notifications for user feedback
- **File Validation**: Automatic file type and size validation
- **Error Handling**: Comprehensive error handling and user feedback

## 🚀 Getting Started

### Prerequisites

- A running instance of the Resume Parser FastAPI backend (default: http://127.0.0.1:8080)
- Modern web browser with ES6+ support
- No additional dependencies required!

### Installation

1. **Clone or download** the frontend files to your local machine
2. **Ensure your FastAPI backend is running** on the specified port (default: 8080)
3. **Open `index.html`** in your web browser

### Quick Start

1. Start your FastAPI backend:
   ```bash
   cd /path/to/your/backend
   python main.py
   ```

2. Open the frontend:
   - Navigate to the `frontend` folder
   - Double-click `index.html` or open it in your browser
   - Or serve it using a local server:
     ```bash
     # Using Python
     python -m http.server 3000
     
     # Using Node.js
     npx serve .
     
     # Using PHP
     php -S localhost:3000
     ```

3. Start parsing resumes!

## 🎯 Usage

### Uploading Files

1. **Drag & Drop**: Simply drag resume files onto the upload area
2. **Browse Files**: Click the "Browse Files" button to select files manually
3. **Supported Formats**: PDF, DOCX, TXT, RTF
4. **File Size Limit**: Maximum 10MB per file

### Parsing Process

1. **Select Files**: Choose one or multiple resume files
2. **Click Parse**: Click the "Parse Resumes" button to start processing
3. **Monitor Progress**: Watch the progress bar and loading animation
4. **View Results**: See parsing results with success/error indicators

### Viewing Results

- **Success Cards**: Green-bordered cards for successfully parsed resumes
- **Error Cards**: Red-bordered cards for failed parsing attempts
- **Click for Details**: Click any result card to view detailed information
- **Export Results**: Download all results as a JSON file

## 🔧 Configuration

### Backend URL

To change the backend API URL, edit the `apiUrl` property in `script.js`:

```javascript
this.apiUrl = 'http://your-backend-url:port';
```

### File Size Limits

Modify the file size validation in `script.js`:

```javascript
if (file.size > 10 * 1024 * 1024) { // 10MB limit
    // Change this value as needed
}
```

### Supported File Types

Update the allowed extensions in `script.js`:

```javascript
const allowedExtensions = ['.pdf', '.docx', '.txt', '.rtf'];
// Add or remove extensions as needed
```

## 🎨 Customization

### Colors and Themes

The frontend uses CSS custom properties and gradients. Modify `styles.css` to change:

- **Primary Colors**: Update the gradient values in `.logo`, `.browse-btn`, etc.
- **Background**: Change the body background gradient
- **Accent Colors**: Modify success/error state colors

### Layout and Spacing

- **Container Width**: Adjust `.container` max-width
- **Card Spacing**: Modify padding and margin values
- **Grid Layout**: Change `.results-grid` column settings

### Animations

- **Transition Speeds**: Adjust transition durations in CSS
- **Hover Effects**: Modify transform and shadow values
- **Loading Animation**: Customize the spinner and progress bar

## 📱 Responsive Design

The frontend is fully responsive with breakpoints at:

- **Desktop**: 1200px and above
- **Tablet**: 768px to 1199px
- **Mobile**: 480px to 767px
- **Small Mobile**: Below 480px

## 🚨 Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure your FastAPI backend is running
   - Check the `apiUrl` in `script.js`
   - Verify CORS settings in your backend

2. **File Upload Issues**
   - Check file size limits
   - Verify file format support
   - Ensure browser supports File API

3. **Styling Issues**
   - Clear browser cache
   - Check CSS file path
   - Verify Font Awesome CDN connection

### Browser Compatibility

- **Chrome**: 60+ ✅
- **Firefox**: 55+ ✅
- **Safari**: 12+ ✅
- **Edge**: 79+ ✅
- **Internet Explorer**: Not supported ❌

## 🔒 Security Considerations

- **File Validation**: Client-side validation for file types and sizes
- **API Security**: Ensure your backend implements proper security measures
- **CORS**: Configure CORS properly in your FastAPI backend
- **File Handling**: Backend should sanitize and validate uploaded files

## 📈 Performance

- **Lazy Loading**: Results are loaded only when needed
- **Efficient DOM**: Minimal DOM manipulation and reflows
- **Optimized Animations**: Hardware-accelerated CSS transitions
- **Memory Management**: Proper cleanup of event listeners and intervals

## 🤝 Contributing

To contribute to the frontend:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This frontend is part of the Resume Parser Pro project. Please refer to the main project license.

## 🆘 Support

For support and questions:

1. Check the troubleshooting section above
2. Review the backend documentation
3. Open an issue in the project repository
4. Contact the development team

---

**Happy Resume Parsing! 🎉**
