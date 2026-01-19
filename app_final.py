from flask import Flask, render_template, request, send_file, jsonify
import docx2txt
import PyPDF2
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from matplotlib import pyplot as plt
from fpdf import FPDF
import re
from datetime import datetime
import tempfile

app = Flask(__name__)

# Use temporary directory for file uploads in production
UPLOAD_FOLDER = tempfile.gettempdir()
CHART_FOLDER = "static/charts"

# Create charts folder if missing
os.makedirs(CHART_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Enhanced domain skills with sparkling features data
DOMAIN_SKILLS = {
    "Data Science": {
        "technical": ["Python", "R", "SQL", "Machine Learning", "Statistics", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch"],
        "tools": ["Jupyter", "Tableau", "Power BI", "Excel", "Git", "Docker", "AWS", "Apache Spark", "Hadoop"],
        "soft": ["Problem Solving", "Communication", "Critical Thinking", "Analytics", "Research"],
        "salary_range": [85000, 120000],
        "growth_rate": 22
    },
    "Web Development": {
        "technical": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Python", "Java", "TypeScript", "Vue.js", "Angular"],
        "tools": ["Git", "Docker", "AWS", "MongoDB", "PostgreSQL", "Redis", "Webpack", "Jenkins"],
        "soft": ["Teamwork", "Problem Solving", "Communication", "Creativity", "Attention to Detail"],
        "salary_range": [65000, 95000],
        "growth_rate": 13
    },
    "Mobile App": {
        "technical": ["Java", "Kotlin", "Swift", "Flutter", "React Native", "Android SDK", "iOS SDK", "Dart", "Objective-C"],
        "tools": ["Xcode", "Android Studio", "Git", "Firebase", "TestFlight", "Gradle", "CocoaPods"],
        "soft": ["User Experience", "Problem Solving", "Attention to Detail", "Innovation", "Adaptability"],
        "salary_range": [75000, 105000],
        "growth_rate": 19
    },
    "AI/ML": {
        "technical": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Keras", "OpenCV"],
        "tools": ["Jupyter", "Git", "Docker", "Kubernetes", "AWS", "Google Cloud", "MLflow", "Weights & Biases"],
        "soft": ["Research", "Problem Solving", "Innovation", "Critical Thinking", "Continuous Learning"],
        "salary_range": [95000, 140000],
        "growth_rate": 31
    }
}

def get_all_domain_skills(domain):
    """Get all skills for a domain (flattened)"""
    domain_data = DOMAIN_SKILLS.get(domain, {})
    all_skills = []
    for category, skills in domain_data.items():
        if isinstance(skills, list) and category in ['technical', 'tools', 'soft']:
            all_skills.extend(skills)
    return all_skills

def extract_text_secure(file_path, filename):
    """Securely extract text from uploaded files"""
    try:
        if filename.lower().endswith('.pdf'):
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                max_pages = min(len(pdf_reader.pages), 50)
                for page_num in range(max_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        elif filename.lower().endswith('.docx'):
            return docx2txt.process(file_path)
        elif filename.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        else:
            return None
    except Exception as e:
        print(f"Text extraction error: {str(e)}")
        return None

def detect_resume_sections(text):
    """Detect common resume sections"""
    sections = {
        'contact': False,
        'summary': False,
        'experience': False,
        'education': False,
        'skills': False,
        'projects': False,
        'certifications': False
    }
    
    text_lower = text.lower()
    
    # Contact information patterns
    if re.search(r'\b\w+@\w+\.\w+\b', text) or re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
        sections['contact'] = True
    
    # Section headers
    section_patterns = {
        'summary': r'\b(summary|profile|objective|about)\b',
        'experience': r'\b(experience|employment|work|career)\b',
        'education': r'\b(education|academic|degree|university|college)\b',
        'skills': r'\b(skills|competencies|technologies|technical)\b',
        'projects': r'\b(projects|portfolio|work samples)\b',
        'certifications': r'\b(certifications|certificates|credentials)\b'
    }
    
    for section, pattern in section_patterns.items():
        if re.search(pattern, text_lower):
            sections[section] = True
    
    return sections

def calculate_section_completeness(sections):
    """Calculate completeness score based on detected sections"""
    required_sections = ['contact', 'experience', 'education', 'skills']
    optional_sections = ['summary', 'projects', 'certifications']
    
    required_score = sum(sections[s] for s in required_sections) / len(required_sections)
    optional_score = sum(sections[s] for s in optional_sections) / len(optional_sections)
    
    total_score = (required_score * 0.7) + (optional_score * 0.3)
    return round(total_score * 100, 2)

def calculate_ats_score(text, domain_skills):
    """Calculate ATS compatibility score"""
    try:
        # Simple ATS scoring based on keywords and structure
        score = 50  # Base score
        
        # Check for contact info
        if re.search(r'\b\w+@\w+\.\w+\b', text):
            score += 15
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            score += 15
        
        # Check for section headers
        if re.search(r'\b(experience|education|skills)\b', text.lower()):
            score += 20
        
        return min(100, score)
    except:
        return 50

def analyze_resume_enhanced(text, domain_skills):
    """Enhanced resume analysis with sparkling features"""
    words = text.split()
    word_count = len(words)
    
    # Advanced skill matching - only check string skills
    text_lower = text.lower()
    found_skills = []
    for skill in domain_skills:
        if isinstance(skill, str) and skill.lower() in text_lower:
            found_skills.append(skill)
    
    missing_skills = [skill for skill in domain_skills if isinstance(skill, str) and skill not in found_skills]
    match_score = round((len(found_skills) / len(domain_skills)) * 100, 2) if domain_skills else 0
    
    # Section detection
    sections = detect_resume_sections(text)
    section_completeness = calculate_section_completeness(sections)
    
    # Simple readability score
    readability_score = min(100, max(0, 100 - (word_count - 300) / 10)) if word_count > 0 else 0
    
    # 🌟 SPARKLING FEATURES 🌟
    ats_score = calculate_ats_score(text, domain_skills)
    
    # ATS Analysis structure for template
    ats_analysis = {
        'score': ats_score,
        'recommendations': [
            'Use clear section headers (Experience, Education, Skills)',
            'Include contact information at the top',
            'Use standard fonts and formatting',
            'Avoid images and complex layouts',
            'Include relevant keywords from job descriptions'
        ]
    }
    
    # Industry benchmark
    industry_benchmark = {
        'your_score': match_score,
        'industry_average': 65,
        'top_10_percent': 85,
        'ranking': 'Above Average' if match_score > 65 else 'Average' if match_score > 45 else 'Below Average'
    }
    
    # Resume strength (matching template expectations)
    resume_strength = {
        'score': round((match_score * 0.4) + (ats_score * 0.3) + (section_completeness * 0.3), 1),
        'level': 'Excellent' if match_score > 80 else 'Good' if match_score > 60 else 'Average',
        'color': 'success' if match_score > 80 else 'info' if match_score > 60 else 'warning'
    }
    
    # Job recommendations
    job_recommendations = [
        {
            'title': f'Senior {domain_skills[0] if domain_skills else "Technical"} Specialist',
            'match_percentage': min(95, match_score + 10),
            'companies': ['Google', 'Microsoft', 'Amazon', 'Meta', 'Apple']
        },
        {
            'title': f'{domain_skills[1] if len(domain_skills) > 1 else "Software"} Engineer',
            'match_percentage': min(90, match_score + 5),
            'companies': ['Netflix', 'Uber', 'Airbnb', 'Spotify', 'Tesla']
        }
    ] if domain_skills else []
    
    # Learning path recommendations
    learning_path = []
    if missing_skills:
        for i, skill in enumerate(missing_skills[:6]):
            learning_path.append({
                'skill': skill,
                'platform': ['Coursera', 'Udemy', 'edX', 'Pluralsight'][i % 4],
                'duration': ['4-6 weeks', '2-3 months', '6-8 weeks', '1-2 months'][i % 4],
                'level': ['Beginner', 'Intermediate', 'Advanced'][i % 3],
                'priority': 'High' if i < 3 else 'Medium'
            })
    
    return {
        'word_count': word_count,
        'skills_found': found_skills,
        'missing_skills': missing_skills,
        'match_score': match_score,
        'sections_detected': sections,
        'section_completeness': section_completeness,
        'readability_score': readability_score,
        'ats_score': ats_score,
        'ats_analysis': ats_analysis,  # For template compatibility
        'industry_benchmark': industry_benchmark,
        'resume_strength': resume_strength,  # Renamed from overall_strength
        'job_recommendations': job_recommendations,
        'learning_path': learning_path
    }

def generate_enhanced_feedback(result, domain):
    """Generate intelligent feedback"""
    feedback = []
    
    score = result['match_score']
    if score >= 80:
        feedback.append("Excellent! Your resume shows strong alignment with the target domain.")
    elif score >= 60:
        feedback.append("Good match! Consider adding a few more relevant skills.")
    elif score >= 40:
        feedback.append("Moderate alignment. Focus on highlighting more domain-specific skills.")
    else:
        feedback.append("Low alignment detected. Consider restructuring your resume.")
    
    # ATS feedback
    ats_score = result.get('ats_score', 50)
    if ats_score < 60:
        feedback.append("Improve ATS compatibility by adding clear section headers and contact info.")
    elif ats_score > 80:
        feedback.append("Great ATS optimization! Your resume should pass most screening systems.")
    
    # Section feedback
    completeness = result['section_completeness']
    if completeness < 70:
        feedback.append("Consider adding missing resume sections like summary or projects.")
    
    # Skills feedback
    if result['missing_skills']:
        top_missing = result['missing_skills'][:3]
        feedback.append(f"Priority skills to develop: {', '.join(top_missing)}")
    
    return feedback

def create_enhanced_skill_chart(found, missing):
    """Create enhanced visualization"""
    try:
        if not found and not missing:
            return None
            
        labels = ['Skills Found', 'Missing Skills']
        sizes = [len(found), len(missing)]
        colors = ['#28a745', '#dc3545']
        
        plt.figure(figsize=(10, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        plt.title('Skills Distribution Analysis', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        os.makedirs(CHART_FOLDER, exist_ok=True)
        chart_path = os.path.join(CHART_FOLDER, "skill_chart.png")
        plt.savefig(chart_path, bbox_inches='tight', dpi=150, facecolor='white')
        plt.close()
        
        return chart_path
    except Exception as e:
        print(f"Chart creation error: {str(e)}")
        try:
            plt.close('all')
        except:
            pass
        return None

def clean_text_for_pdf(text):
    """Remove emojis and non-latin characters for PDF compatibility"""
    import re
    # Remove emojis and other unicode symbols
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def generate_enhanced_pdf_report(candidate, domain, result, timestamp):
    """Generate comprehensive PDF report"""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_fill_color(70, 130, 180)
        pdf.rect(0, 0, 210, 25, 'F')
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 15, "Enhanced AI Resume Analysis Report", ln=True, align="C")
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, f"Generated on {timestamp}", ln=True, align="C")
        
        # Reset colors
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)
        
        # Summary
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Executive Summary", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Candidate: {clean_text_for_pdf(candidate)}", ln=True)
        pdf.cell(0, 8, f"Domain: {clean_text_for_pdf(domain)}", ln=True)
        pdf.cell(0, 8, f"Overall Score: {result['resume_strength']['score']}% ({result['resume_strength']['level']})", ln=True)
        pdf.cell(0, 8, f"Skills Match: {result['match_score']}%", ln=True)
        pdf.cell(0, 8, f"ATS Score: {result['ats_score']}%", ln=True)
        pdf.ln(10)
        
        # Skills Analysis
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"Skills Found ({len(result['skills_found'])}):", ln=True)
        pdf.set_font("Arial", '', 11)
        
        skills_text = ", ".join(result['skills_found']) if result['skills_found'] else "No relevant skills detected"
        pdf.multi_cell(0, 6, clean_text_for_pdf(skills_text))
        pdf.ln(5)
        
        # Recommendations
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "AI Recommendations:", ln=True)
        pdf.set_font("Arial", '', 11)
        
        feedback = generate_enhanced_feedback(result, domain)
        for i, item in enumerate(feedback, 1):
            clean_item = clean_text_for_pdf(item)
            pdf.multi_cell(0, 6, f"{i}. {clean_item}")
            pdf.ln(2)
        
        # Save PDF
        pdf_path = os.path.join(UPLOAD_FOLDER, f"enhanced_resume_report_{int(datetime.now().timestamp())}.pdf")
        pdf.output(pdf_path)
        return pdf_path
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return None

@app.route('/', methods=['GET', 'POST'])
def home():
    """Enhanced home route with sparkling features"""
    if request.method == 'GET':
        return render_template("index.html")
    
    try:
        candidate = request.form.get('name', '').strip()
        domain = request.form.get('domain', '').strip()
        
        if not candidate or not domain:
            return render_template("index.html", result={'error': 'Name and domain are required'})
        
        if 'resume' not in request.files:
            return render_template("index.html", result={'error': 'No resume file provided'})
        
        file = request.files['resume']
        if file.filename == '':
            return render_template("index.html", result={'error': 'No file selected'})
        
        # Save file
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text
        text = extract_text_secure(file_path, filename)
        if not text:
            return render_template("index.html", result={'error': 'Could not extract text from file'})
        
        # Get domain skills
        domain_skills = get_all_domain_skills(domain)
        
        # Perform enhanced analysis
        result = analyze_resume_enhanced(text, domain_skills)
        
        # Generate feedback
        result['feedback'] = generate_enhanced_feedback(result, domain)
        
        # Add salary estimation with enhanced structure
        domain_data = DOMAIN_SKILLS.get(domain, {})
        salary_range = domain_data.get('salary_range', [50000, 80000])
        result['salary_estimate'] = {
            'min_salary': salary_range[0],
            'max_salary': salary_range[1],
            'currency': 'USD',
            'growth_rate': domain_data.get('growth_rate', 10),
            'market_demand': 'High' if domain_data.get('growth_rate', 10) > 20 else 'Medium'
        }
        
        # Create chart
        chart_url = create_enhanced_skill_chart(result['skills_found'], result['missing_skills'])
        
        # Generate PDF report
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        pdf_url = generate_enhanced_pdf_report(candidate, domain, result, timestamp)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        return render_template("index.html", 
                             result=result, 
                             chart_url=chart_url, 
                             pdf_url=pdf_url,
                             candidate=candidate,
                             domain=domain)
        
    except Exception as e:
        return render_template("index.html", result={'error': f'An error occurred: {str(e)}'})

@app.route('/api/v1/domains', methods=['GET'])
def get_domains():
    """API endpoint to get available domains"""
    return jsonify({
        'domains': list(DOMAIN_SKILLS.keys()),
        'domain_details': DOMAIN_SKILLS
    })

@app.route('/download')
def download_pdf():
    """Download the latest PDF report"""
    try:
        pdf_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith('enhanced_resume_report_') and f.endswith('.pdf')]
        if pdf_files:
            latest_pdf = max(pdf_files, key=lambda x: os.path.getctime(os.path.join(UPLOAD_FOLDER, x)))
            pdf_path = os.path.join(UPLOAD_FOLDER, latest_pdf)
            return send_file(pdf_path, as_attachment=True, download_name="enhanced_resume_analysis.pdf")
        return "Report not found", 404
    except Exception as e:
        return f"Error downloading report: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🌟 Starting Enhanced AI Resume Checker...")
    print("🎯 Features: ATS Analysis, Salary Estimation, Industry Benchmarking")
    print(f"🌐 Visit: http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)