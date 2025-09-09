// Advanced AI Resume Parser - Neural Network Intelligence
class AIResumeParser {
    constructor() {
        this.files = [];
        this.results = [];
        this.apiUrl = 'https://web-production-33afa.up.railway.app'; // FastAPI backend URL
        this.processingSteps = [
            'Initializing Neural Networks...',
            'Analyzing Document Structure...',
            'Extracting Text Content...',
            'Processing Skills & Experience...',
            'Generating AI Insights...',
            'Finalizing Analysis...'
        ];
        this.currentStep = 0;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeAIEffects();
    }

    initializeElements() {
        // DOM elements
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.browseBtn = document.getElementById('browseBtn');
        this.fileList = document.getElementById('fileList');
        this.parseBtn = document.getElementById('parseBtn');
        this.loadingSection = document.getElementById('loadingSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsGrid = document.getElementById('resultsGrid');
        this.resultModal = document.getElementById('resultModal');
        this.closeModal = document.getElementById('closeModal');
        this.modalTitle = document.getElementById('modalTitle');
        this.modalBody = document.getElementById('modalBody');
        this.notifications = document.getElementById('notifications');
        this.progressFill = document.getElementById('progressFill');
        this.processingStatus = document.getElementById('processingStatus');
        this.aiConfidence = document.getElementById('aiConfidence');
        this.successCount = document.getElementById('successCount');
        this.errorCount = document.getElementById('errorCount');
        this.exportBtn = document.getElementById('exportBtn');
    }

    bindEvents() {
        // File upload events
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        this.uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        this.uploadArea.addEventListener('dragenter', this.handleDragEnter.bind(this));
        this.uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        this.browseBtn.addEventListener('click', () => this.fileInput.click());
        this.parseBtn.addEventListener('click', this.parseResumes.bind(this));
        this.closeModal.addEventListener('click', this.closeResultModal.bind(this));
        this.exportBtn.addEventListener('click', this.exportResults.bind(this));
        
        // Close modal when clicking outside
        this.resultModal.addEventListener('click', (e) => {
            if (e.target === this.resultModal) {
                this.closeResultModal();
            }
        });
    }

    initializeAIEffects() {
        // Initialize particle effects
        this.createParticles();
        this.createNeuralGrid();
        
        // Add AI typing effect to title
        this.typeWriterEffect();
        
        // Initialize status indicators
        this.animateStatusIndicators();
    }

    createParticles() {
        const particlesContainer = document.getElementById('aiParticles');
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 3 + 1}px;
                height: ${Math.random() * 3 + 1}px;
                background: ${['#00ffff', '#ff00ff', '#ffff00', '#00ff00'][Math.floor(Math.random() * 4)]};
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                opacity: ${Math.random() * 0.5 + 0.1};
                animation: float ${Math.random() * 10 + 10}s linear infinite;
                pointer-events: none;
            `;
            particlesContainer.appendChild(particle);
        }
    }

    createNeuralGrid() {
        const gridContainer = document.getElementById('neuralGrid');
        // Neural grid is created with CSS, but we can add dynamic connections
        for (let i = 0; i < 20; i++) {
            const connection = document.createElement('div');
            connection.style.cssText = `
                position: absolute;
                width: 1px;
                height: 1px;
                background: #00ffff;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                opacity: 0.3;
                animation: connection-pulse ${Math.random() * 3 + 2}s ease-in-out infinite;
                pointer-events: none;
            `;
            gridContainer.appendChild(connection);
        }
    }

    typeWriterEffect() {
        const title = document.querySelector('.ai-title');
        const text = title.textContent;
        title.textContent = '';
        
        let i = 0;
        const typeInterval = setInterval(() => {
            if (i < text.length) {
                title.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(typeInterval);
                // Add final glow effect
                title.style.animation = 'final-glow 2s ease-in-out infinite';
            }
        }, 100);
    }

    animateStatusIndicators() {
        const statusDots = document.querySelectorAll('.status-dot');
        statusDots.forEach((dot, index) => {
            setTimeout(() => {
                dot.style.animation = 'status-pulse 2s ease-in-out infinite';
            }, index * 500);
        });
    }

    handleDragEnter(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
        this.showNotification('Drop files to begin AI analysis', 'success');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDragOver(e) {
        e.preventDefault();
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        this.addFiles(files);
    }

    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        this.addFiles(files);
    }

    addFiles(files) {
        const validFiles = files.filter(file => {
            const validTypes = ['.pdf', '.docx', '.txt', '.rtf'];
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            return validTypes.includes(fileExtension) && file.size <= 10 * 1024 * 1024; // 10MB limit
        });

        if (validFiles.length === 0) {
            this.showNotification('Please select valid files (PDF, DOCX, TXT, RTF) under 10MB', 'error');
            return;
        }

        this.files = [...this.files, ...validFiles];
        this.updateFileList();
        this.updateParseButton();
        this.showNotification(`${validFiles.length} file(s) added for AI analysis`, 'success');
    }

    updateFileList() {
        this.fileList.innerHTML = '';
        
        this.files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'ai-file-item';
            
            const fileIcon = this.getFileIcon(file.name);
            const fileSize = this.formatFileSize(file.size);
            
            fileItem.innerHTML = `
                <div class="file-info">
                    <div class="file-icon">
                        <i class="${fileIcon}"></i>
                    </div>
                    <div class="file-details">
                        <h4>${file.name}</h4>
                        <p>${fileSize} • ${file.type || 'Unknown type'}</p>
                    </div>
                </div>
                <button class="remove-btn" onclick="aiParser.removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            this.fileList.appendChild(fileItem);
        });
    }

    removeFile(index) {
        this.files.splice(index, 1);
        this.updateFileList();
        this.updateParseButton();
        this.showNotification('File removed from analysis queue', 'success');
    }

    updateParseButton() {
        this.parseBtn.disabled = this.files.length === 0;
        if (this.files.length > 0) {
            this.parseBtn.querySelector('span').textContent = `Initialize AI Processing (${this.files.length} files)`;
        } else {
            this.parseBtn.querySelector('span').textContent = 'Initialize AI Processing';
        }
    }

    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        switch (ext) {
            case 'pdf': return 'fas fa-file-pdf';
            case 'docx': return 'fas fa-file-word';
            case 'txt': return 'fas fa-file-alt';
            case 'rtf': return 'fas fa-file-text';
            default: return 'fas fa-file';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async parseResumes() {
        if (this.files.length === 0) return;

        this.showLoadingSection();
        this.results = [];
        this.currentStep = 0;

        try {
            const formData = new FormData();
            this.files.forEach(file => {
                formData.append('files', file);
            });

            // Simulate AI processing steps
            this.simulateAIProcessing();

            const response = await fetch(`${this.apiUrl}/parse-multiple`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.results = data.results || [];
            this.showResults();
            this.showNotification('AI analysis completed successfully!', 'success');

        } catch (error) {
            console.error('Error parsing resumes:', error);
            this.showNotification('AI analysis failed. Please try again.', 'error');
            this.hideLoadingSection();
        }
    }

    simulateAIProcessing() {
        const totalSteps = this.processingSteps.length;
        let currentStep = 0;

        const processStep = () => {
            if (currentStep < totalSteps) {
                this.processingStatus.textContent = this.processingSteps[currentStep];
                this.progressFill.style.width = `${((currentStep + 1) / totalSteps) * 100}%`;
                this.aiConfidence.textContent = `${Math.round(((currentStep + 1) / totalSteps) * 100)}%`;
                currentStep++;
                
                setTimeout(processStep, 1000);
            } else {
                // Processing complete
                setTimeout(() => {
                    this.hideLoadingSection();
                }, 500);
            }
        };

        processStep();
    }

    showLoadingSection() {
        this.loadingSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        
        // Add AI processing animation
        this.loadingSection.querySelector('.ai-brain').style.animation = 'brain-process 2s ease-in-out infinite';
    }

    hideLoadingSection() {
        this.loadingSection.style.display = 'none';
        this.loadingSection.querySelector('.ai-brain').style.animation = '';
    }

    showResults() {
        this.resultsSection.style.display = 'block';
        this.updateResultsGrid();
        this.updateStats();
    }

    updateResultsGrid() {
        this.resultsGrid.innerHTML = '';
        
        this.results.forEach((result, index) => {
            const resultCard = document.createElement('div');
            resultCard.className = `ai-result-card ${result.success ? 'success' : 'error'}`;
            
            const statusClass = result.success ? 'success' : 'error';
            const statusText = result.success ? 'AI Analysis Complete' : 'Analysis Failed';
            
            // Create enhanced result card with metrics
            let cardContent = `
                <h3>${result.filename || 'Unknown File'}</h3>
                <div class="status ${statusClass}">${statusText}</div>
                <div class="details">
                    ${result.success ? 
                        `AI extracted ${result.data?.skills?.length || 0} skills and analyzed experience patterns` :
                        `Error: ${result.error || 'Unknown error occurred'}`
                    }
                </div>
            `;
            
            // Add advanced metrics for successful results
            if (result.success && result.data) {
                const data = result.data;
                const skillsCount = data.skills ? data.skills.length : 0;
                const experienceCount = data.experience ? 1 : 0;
                const educationCount = data.education ? 1 : 0;
                const contactInfo = (data.name || data.email || data.phone) ? 1 : 0;
                
                cardContent += `
                    <div class="result-details">
                        <div class="result-metrics">
                            <div class="metric-item">
                                <span class="metric-value">${skillsCount}</span>
                                <span class="metric-label">Skills</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-value">${experienceCount}</span>
                                <span class="metric-label">Experience</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-value">${educationCount}</span>
                                <span class="metric-label">Education</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-value">${contactInfo}</span>
                                <span class="metric-label">Contact</span>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            resultCard.innerHTML = cardContent;
            resultCard.addEventListener('click', () => this.showResultDetails(result, index));
            this.resultsGrid.appendChild(resultCard);
        });
    }

    updateStats() {
        const successCount = this.results.filter(r => r.success).length;
        const errorCount = this.results.filter(r => !r.success).length;
        
        this.successCount.textContent = successCount;
        this.errorCount.textContent = errorCount;
    }

    showResultDetails(result, index) {
        this.modalTitle.textContent = `AI Analysis Details - ${result.filename || 'Unknown File'}`;
        
        let modalContent = '';
        if (result.success && result.data) {
            const data = result.data;
            
            // Personal Information Section
            modalContent += `
                <div class="modal-section">
                    <h5><i class="fas fa-user"></i> Personal Information</h5>
                    <p><strong>Name:</strong> ${data.name || 'Not detected'}</p>
                    <p><strong>Email:</strong> ${data.email || 'Not detected'}</p>
                    <p><strong>Phone:</strong> ${data.phone || 'Not detected'}</p>
                    <p><strong>Location:</strong> ${data.location || 'Not detected'}</p>
                </div>
            `;
            
            // Professional Summary Section
            if (data.summary) {
                modalContent += `
                    <div class="modal-section">
                        <h5><i class="fas fa-file-alt"></i> Professional Summary</h5>
                        <p>${data.summary}</p>
                    </div>
                `;
            }
            
            // Skills Section with Grid
            if (data.skills && data.skills.length > 0) {
                const skillsHtml = data.skills.map(skill => 
                    `<div class="skill-tag">${skill}</div>`
                ).join('');
                
                modalContent += `
                    <div class="modal-section">
                        <h5><i class="fas fa-tools"></i> Skills Detected (${data.skills.length})</h5>
                        <div class="skills-grid">
                            ${skillsHtml}
                        </div>
                    </div>
                `;
            }
            
            // Experience Section
            if (data.experience) {
                modalContent += `
                    <div class="modal-section">
                        <h5><i class="fas fa-briefcase"></i> Professional Experience</h5>
                        <div class="experience-item">
                            <div class="experience-title">${data.experience.title || 'Position'}</div>
                            <div class="experience-company">${data.experience.company || 'Company'}</div>
                            <div class="experience-duration">${data.experience.duration || 'Duration'}</div>
                            <p>${data.experience.description || 'No description available'}</p>
                        </div>
                    </div>
                `;
            }
            
            // Education Section
            if (data.education) {
                modalContent += `
                    <div class="modal-section">
                        <h5><i class="fas fa-graduation-cap"></i> Education</h5>
                        <div class="experience-item">
                            <div class="experience-title">${data.education.degree || 'Degree'}</div>
                            <div class="experience-company">${data.education.institution || 'Institution'}</div>
                            <div class="experience-duration">${data.education.year || 'Year'}</div>
                        </div>
                    </div>
                `;
            }
            
            // AI Analysis Metrics
            const skillsCount = data.skills ? data.skills.length : 0;
            const hasContact = (data.name || data.email || data.phone) ? 'Yes' : 'No';
            const hasExperience = data.experience ? 'Yes' : 'No';
            const hasEducation = data.education ? 'Yes' : 'No';
            
            modalContent += `
                <div class="modal-section">
                    <h5><i class="fas fa-chart-bar"></i> AI Analysis Metrics</h5>
                    <div class="result-metrics">
                        <div class="metric-item">
                            <span class="metric-value">${skillsCount}</span>
                            <span class="metric-label">Skills Found</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-value">${hasContact}</span>
                            <span class="metric-label">Contact Info</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-value">${hasExperience}</span>
                            <span class="metric-label">Experience</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-value">${hasEducation}</span>
                            <span class="metric-label">Education</span>
                        </div>
                    </div>
                </div>
            `;
            
        } else {
            modalContent = `
                <div class="modal-section">
                    <h5><i class="fas fa-exclamation-triangle"></i> Analysis Error</h5>
                    <p><strong>Error:</strong> ${result.error || 'Unknown error occurred'}</p>
                    <p>Please try uploading the file again or contact support if the issue persists.</p>
                </div>
            `;
        }
        
        this.modalBody.innerHTML = modalContent;
        this.resultModal.style.display = 'block';
        
        // Add AI modal animation
        this.resultModal.querySelector('.modal-hologram').style.animation = 'modal-appear 0.5s ease';
    }

    closeResultModal() {
        this.resultModal.style.display = 'none';
    }

    exportResults() {
        if (this.results.length === 0) {
            this.showNotification('No results to export', 'error');
            return;
        }

        const exportData = {
            timestamp: new Date().toISOString(),
            totalFiles: this.files.length,
            successfulParses: this.results.filter(r => r.success).length,
            failedParses: this.results.filter(r => !r.success).length,
            results: this.results,
            aiVersion: "Neural Network v2.0",
            processingEngine: "Advanced AI Resume Parser Pro"
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai-resume-analysis-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('AI analysis results exported successfully!', 'success');
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `ai-notification ${type}`;
        
        const icon = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle';
        
        notification.innerHTML = `
            <i class="${icon}"></i>
            <span>${message}</span>
        `;
        
        this.notifications.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'notification-slide-out 0.5s ease forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 500);
        }, 5000);
    }
}

// Initialize AI Resume Parser when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.aiParser = new AIResumeParser();
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float {
            0% { transform: translateY(0px) rotate(0deg); }
            100% { transform: translateY(-100vh) rotate(360deg); }
        }
        
        @keyframes connection-pulse {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
        }
        
        @keyframes final-glow {
            0%, 100% { text-shadow: 0 0 30px rgba(0, 255, 255, 0.5); }
            50% { text-shadow: 0 0 50px rgba(0, 255, 255, 0.8), 0 0 70px rgba(0, 255, 255, 0.6); }
        }
        
        @keyframes brain-process {
            0%, 100% { transform: scale(1) rotate(0deg); }
            50% { transform: scale(1.1) rotate(5deg); }
        }
        
        @keyframes modal-appear {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        
        @keyframes notification-slide-out {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
});
