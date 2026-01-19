// Enhanced Resume Checker Frontend
class ResumeChecker {
    constructor() {
        this.initializeEventListeners();
        this.loadDomains();
    }

    initializeEventListeners() {
        const form = document.getElementById('resumeForm');
        const fileInput = document.getElementById('resumeFile');
        const progressBar = document.getElementById('progressBar');
        const resultsContainer = document.getElementById('results');

        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        // Add drag and drop functionality
        this.initializeDragDrop();
    }

    initializeDragDrop() {
        const dropZone = document.getElementById('dropZone');
        if (!dropZone) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'), false);
        });

        dropZone.addEventListener('drop', (e) => this.handleDrop(e), false);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDrop(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const fileInput = document.getElementById('resumeFile');
            fileInput.files = files;
            this.handleFileSelect({ target: fileInput });
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (!file) return;

        const fileInfo = document.getElementById('fileInfo');
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        const maxSize = 16 * 1024 * 1024; // 16MB

        // Validate file type
        if (!allowedTypes.includes(file.type)) {
            this.showError('Please select a PDF, DOCX, or TXT file.');
            return;
        }

        // Validate file size
        if (file.size > maxSize) {
            this.showError('File size must be less than 16MB.');
            return;
        }

        // Show file info
        if (fileInfo) {
            fileInfo.innerHTML = `
                <div class="alert alert-info">
                    <strong>Selected:</strong> ${file.name} (${this.formatFileSize(file.size)})
                </div>
            `;
        }
    }

    async loadDomains() {
        try {
            const response = await fetch('/api/v1/domains');
            const data = await response.json();
            
            const domainSelect = document.getElementById('domain');
            if (domainSelect && data.domains) {
                domainSelect.innerHTML = '<option value="">Select Target Domain</option>';
                data.domains.forEach(domain => {
                    const option = document.createElement('option');
                    option.value = domain;
                    option.textContent = domain;
                    domainSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Failed to load domains:', error);
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const progressBar = document.getElementById('progressBar');
        const resultsContainer = document.getElementById('results');
        const submitBtn = document.getElementById('submitBtn');

        // Show progress
        this.showProgress(true);
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
        }

        try {
            const response = await fetch('/api/v1/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed');
            }

            this.displayResults(data);
            this.trackAnalytics('analysis_completed', { domain: formData.get('domain') });

        } catch (error) {
            this.showError(error.message);
        } finally {
            this.showProgress(false);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Analyze Resume';
            }
        }
    }

    displayResults(data) {
        const resultsContainer = document.getElementById('results');
        if (!resultsContainer) return;

        const results = data.results;
        
        resultsContainer.innerHTML = `
            <div class="card mt-4">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">Analysis Results for ${data.candidate_name}</h4>
                </div>
                <div class="card-body">
                    ${this.generateScoreCard(results)}
                    ${this.generateSkillsSection(results)}
                    ${this.generateAdvancedMetrics(results)}
                    ${this.generateFeedbackSection(results)}
                    ${this.generateActionButtons(data.analysis_id)}
                </div>
            </div>
        `;

        // Generate and display charts
        this.generateCharts(results);
    }

    generateScoreCard(results) {
        const scoreColor = this.getScoreColor(results.match_score);
        return `
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card text-center border-${scoreColor}">
                        <div class="card-body">
                            <h2 class="text-${scoreColor}">${results.match_score}%</h2>
                            <p class="card-text">Match Score</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h2>${results.word_count}</h2>
                            <p class="card-text">Total Words</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h2>${results.section_completeness}%</h2>
                            <p class="card-text">Completeness</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h2>${results.readability.readability_level}</h2>
                            <p class="card-text">Readability</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    generateSkillsSection(results) {
        const foundSkills = results.skills_found.map(skill => 
            `<span class="badge bg-success me-1 mb-1">${skill}</span>`
        ).join('');

        const missingSkills = results.missing_skills.slice(0, 10).map(skill => 
            `<span class="badge bg-danger me-1 mb-1">${skill}</span>`
        ).join('');

        return `
            <div class="row mb-4">
                <div class="col-md-6">
                    <h5 class="text-success">Skills Found (${results.skills_found.length})</h5>
                    <div class="mb-3">${foundSkills || '<em>No skills detected</em>'}</div>
                </div>
                <div class="col-md-6">
                    <h5 class="text-danger">Missing Skills (${results.missing_skills.length})</h5>
                    <div class="mb-3">${missingSkills || '<em>All skills found</em>'}</div>
                </div>
            </div>
        `;
    }

    generateAdvancedMetrics(results) {
        const sections = results.sections_detected;
        const sectionBadges = Object.entries(sections).map(([section, found]) => 
            `<span class="badge bg-${found ? 'success' : 'secondary'} me-1 mb-1">${section}</span>`
        ).join('');

        return `
            <div class="row mb-4">
                <div class="col-12">
                    <h5>Resume Sections</h5>
                    <div class="mb-3">${sectionBadges}</div>
                </div>
            </div>
            <div class="row mb-4">
                <div class="col-12">
                    <div id="chartsContainer"></div>
                </div>
            </div>
        `;
    }

    generateFeedbackSection(results) {
        const feedbackItems = results.feedback.map(item => 
            `<li class="list-group-item">${item}</li>`
        ).join('');

        return `
            <div class="mb-4">
                <h5>AI Feedback & Recommendations</h5>
                <ul class="list-group">
                    ${feedbackItems}
                </ul>
            </div>
        `;
    }

    generateActionButtons(analysisId) {
        return `
            <div class="d-flex gap-2">
                <button class="btn btn-success" onclick="resumeChecker.downloadReport(${analysisId})">
                    <i class="fas fa-download"></i> Download PDF Report
                </button>
                <button class="btn btn-info" onclick="resumeChecker.shareResults(${analysisId})">
                    <i class="fas fa-share"></i> Share Results
                </button>
                <button class="btn btn-secondary" onclick="resumeChecker.saveAnalysis(${analysisId})">
                    <i class="fas fa-save"></i> Save Analysis
                </button>
            </div>
        `;
    }

    generateCharts(results) {
        // Skills distribution chart
        const ctx = document.createElement('canvas');
        ctx.id = 'skillsChart';
        ctx.width = 400;
        ctx.height = 200;
        
        const chartsContainer = document.getElementById('chartsContainer');
        if (chartsContainer) {
            chartsContainer.innerHTML = '<canvas id="skillsChart" width="400" height="200"></canvas>';
            
            // Use Chart.js if available
            if (typeof Chart !== 'undefined') {
                new Chart(document.getElementById('skillsChart'), {
                    type: 'doughnut',
                    data: {
                        labels: ['Skills Found', 'Missing Skills'],
                        datasets: [{
                            data: [results.skills_found.length, results.missing_skills.length],
                            backgroundColor: ['#28a745', '#dc3545']
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Skills Distribution'
                            }
                        }
                    }
                });
            }
        }
    }

    getScoreColor(score) {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'danger';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showProgress(show) {
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.style.display = show ? 'block' : 'none';
        }
    }

    showError(message) {
        const errorContainer = document.getElementById('errorContainer');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    }

    async downloadReport(analysisId) {
        try {
            const response = await fetch(`/download/${analysisId}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `resume_analysis_${analysisId}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            this.showError('Failed to download report');
        }
    }

    shareResults(analysisId) {
        const shareUrl = `${window.location.origin}/analysis/${analysisId}`;
        if (navigator.share) {
            navigator.share({
                title: 'Resume Analysis Results',
                url: shareUrl
            });
        } else {
            navigator.clipboard.writeText(shareUrl).then(() => {
                alert('Share link copied to clipboard!');
            });
        }
    }

    saveAnalysis(analysisId) {
        localStorage.setItem('savedAnalysis', analysisId);
        alert('Analysis saved locally!');
    }

    trackAnalytics(event, data) {
        // Simple analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', event, data);
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.resumeChecker = new ResumeChecker();
});