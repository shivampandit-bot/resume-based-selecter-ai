import streamlit as st
import re
import base64
from collections import Counter
import time

# Optional PDF support
try:
    from PyPDF2 import PdfReader
    PDF_SUPPORTED = True
except ImportError:
    PDF_SUPPORTED = False

# Page configuration
st.set_page_config(
    page_title="Graphura Resume AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern SaaS design
def load_css():
    st.markdown("""
    <style>
    /* Global Styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        overflow-x: hidden;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 4px;
    }

    /* Glassmorphism effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
        border-color: rgba(255, 255, 255, 0.2);
    }

    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 80px 20px;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 30px;
        margin: 20px 0;
        position: relative;
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
        animation: float 6s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
    }

    .hero-subtitle {
        font-size: 1.5rem;
        color: #b8c5d6;
        margin-bottom: 40px;
        font-weight: 300;
    }

    .hero-tagline {
        font-size: 1.2rem;
        color: #8892a0;
        margin-bottom: 50px;
        font-style: italic;
    }

    /* Buttons */
    .btn-primary {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border: none;
        color: white;
        padding: 15px 40px;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 50px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        text-decoration: none;
        display: inline-block;
        margin: 10px;
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        background: linear-gradient(45deg, #764ba2, #667eea);
    }

    .btn-secondary {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        padding: 15px 40px;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 50px;
        cursor: pointer;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        text-decoration: none;
        display: inline-block;
        margin: 10px;
    }

    .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.4);
        transform: translateY(-2px);
    }

    /* Upload Section */
    .upload-section {
        text-align: center;
        padding: 40px;
        margin: 30px 0;
    }

    .upload-box {
        border: 2px dashed rgba(102, 126, 234, 0.5);
        border-radius: 20px;
        padding: 60px 40px;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        cursor: pointer;
        margin: 20px auto;
        max-width: 600px;
    }

    .upload-box:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.1);
        transform: scale(1.02);
    }

    .upload-icon {
        font-size: 3rem;
        color: #667eea;
        margin-bottom: 20px;
    }

    /* Dashboard Cards */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 25px;
        margin: 30px 0;
    }

    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
    }

    .card-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }

    .card-title::before {
        content: '';
        width: 4px;
        height: 20px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 2px;
        margin-right: 12px;
    }

    /* Progress Bars */
    .progress-bar {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        overflow: hidden;
        margin: 10px 0;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 4px;
        transition: width 1s ease;
    }

    /* Circular Progress */
    .circular-progress {
        width: 120px;
        height: 120px;
        margin: 0 auto;
        position: relative;
    }

    .circular-progress svg {
        width: 100%;
        height: 100%;
        transform: rotate(-90deg);
    }

    .circular-progress circle {
        fill: none;
        stroke-width: 8;
        stroke-linecap: round;
    }

    .circular-progress .bg {
        stroke: rgba(255, 255, 255, 0.1);
    }

    .circular-progress .fg {
        stroke: url(#gradient);
        stroke-dasharray: 283;
        stroke-dashoffset: 283;
        transition: stroke-dashoffset 1s ease;
    }

    /* Skills Tags */
    .skill-tag {
        display: inline-block;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }

    /* Role Cards */
    .role-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }

    .role-card:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateX(5px);
    }

    .role-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .role-match {
        color: #667eea;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .role-reason {
        color: #b8c5d6;
        font-size: 0.9rem;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .badge-fresher {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
    }

    .badge-experienced {
        background: linear-gradient(45deg, #4ecdc4, #44a08d);
        color: white;
    }

    .badge-strong {
        background: linear-gradient(45deg, #4ecdc4, #44a08d);
        color: white;
    }

    .badge-moderate {
        background: linear-gradient(45deg, #f9ca24, #f0932b);
        color: white;
    }

    .badge-low {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
    }

    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }

        .dashboard-grid {
            grid-template-columns: 1fr;
        }

        .upload-box {
            padding: 40px 20px;
        }
    }

    /* Loading Animation */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: #667eea;
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Navbar */
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: rgba(15, 15, 35, 0.9);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px 30px;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .navbar-brand {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .navbar-links {
        display: flex;
        gap: 20px;
    }

    .navbar-link {
        color: #b8c5d6;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
    }

    .navbar-link:hover {
        color: #667eea;
    }

    /* Theme Toggle */
    .theme-toggle {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .theme-toggle:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    </style>

    <!-- SVG Gradient Definition -->
    <svg width="0" height="0">
        <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
            </linearGradient>
        </defs>
    </svg>
    """, unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Define skills list
SKILLS_LIST = [
    'Python', 'Java', 'JavaScript', 'HTML', 'CSS', 'C++', 'C#', 'Ruby', 'PHP', 'Go',
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'React', 'Angular', 'Vue.js', 'Node.js',
    'Machine Learning', 'Deep Learning', 'Data Analysis', 'Pandas', 'NumPy', 'TensorFlow',
    'Keras', 'Scikit-learn', 'NLP', 'Computer Vision', 'AWS', 'Azure', 'Docker', 'Kubernetes',
    'Git', 'Linux', 'Windows', 'Agile', 'Scrum', 'Project Management'
]

# Define roles and their required skills
ROLES = {
    'Web Developer': ['Python', 'JavaScript', 'HTML', 'CSS', 'React', 'Node.js'],
    'Data Analyst': ['Python', 'SQL', 'Data Analysis', 'Pandas', 'NumPy', 'Machine Learning'],
    'AI/ML Engineer': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'Scikit-learn', 'NLP'],
    'Graphic Designer': ['Adobe Photoshop', 'Illustrator', 'Figma', 'UI/UX'],
    'Digital Marketing': ['SEO', 'Google Analytics', 'Social Media', 'Content Marketing'],
    'HR Intern': ['Communication', 'Recruitment', 'HR Management']
}

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == 'text/plain':
        return uploaded_file.read().decode('utf-8')
    elif uploaded_file.type == 'application/pdf' and PDF_SUPPORTED:
        pdf_reader = PdfReader(uploaded_file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    else:
        return None

def extract_name(text):
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line and not re.match(r'(?i)(resume|cv|curriculum vitae)', line):
            # Remove common titles
            line = re.sub(r'(?i)\b(mr|ms|mrs|dr|prof)\.?\s*', '', line)
            return line.title()
    return "Unknown"

def extract_skills(text):
    text_lower = text.lower()
    found_skills = [skill for skill in SKILLS_LIST if skill.lower() in text_lower]
    return list(set(found_skills))  # Remove duplicates

def extract_education(text):
    text_lower = text.lower()
    if 'phd' in text_lower or 'doctorate' in text_lower:
        return 'PhD'
    elif 'masters' in text_lower or 'master\'s' in text_lower or 'msc' in text_lower or 'ms' in text_lower:
        return 'Masters'
    elif 'bachelors' in text_lower or 'bachelor\'s' in text_lower or 'bsc' in text_lower or 'bs' in text_lower:
        return 'Bachelors'
    else:
        return 'Others'

def extract_experience(text):
    # Look for patterns like "X years", "X yrs", "X+ years"
    patterns = [
        r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
        r'experience\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\+\s*years?',
        r'(\d+)\s*years?\s*work'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            years = max(int(match) for match in matches)
            return years
    return 0

def extract_certifications(text):
    count = len(re.findall(r'\b(certificat(?:e|ion)s?)\b', text, re.IGNORECASE))
    return count

def calculate_skills_score(skills):
    if not SKILLS_LIST:
        return 0
    match_percentage = len(skills) / len(SKILLS_LIST) * 100
    return min(40, (match_percentage / 100) * 40)

def calculate_education_score(education):
    scores = {
        'PhD': 30,
        'Masters': 25,
        'Bachelors': 20,
        'Others': 10
    }
    return scores.get(education, 10)

def calculate_experience_score(experience_years):
    if experience_years >= 3:
        return 20
    elif experience_years >= 1:
        return 15
    elif experience_years > 0:
        return 10
    else:
        return 5

def calculate_certificates_score(cert_count):
    if cert_count >= 5:
        return 10
    elif cert_count >= 2:
        return 7
    elif cert_count >= 1:
        return 5
    else:
        return 2

def calculate_total_score(skills_score, education_score, experience_score, cert_score):
    return skills_score + education_score + experience_score + cert_score

def get_fit_category(total_score):
    if total_score >= 80:
        return "Strong Fit"
    elif total_score >= 60:
        return "Moderate Fit"
    else:
        return "Low Fit"

def recommend_roles(skills):
    role_scores = {}
    for role, required_skills in ROLES.items():
        matched = sum(1 for skill in required_skills if skill in skills)
        score = (matched / len(required_skills)) * 100 if required_skills else 0
        role_scores[role] = score
    
    # Sort by score descending and take top 3
    top_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    recommendations = []
    for role, score in top_roles:
        reason = f"Matches {sum(1 for skill in ROLES[role] if skill in skills)} out of {len(ROLES[role])} required skills."
        recommendations.append({
            'role': role,
            'score': round(score, 1),
            'reason': reason
        })
    return recommendations

def get_ai_suggestions(skills, education, experience_years, cert_count):
    suggestions = []
    if len(skills) < 5:
        suggestions.append("Improve skills: Learn more technologies relevant to your field.")
    if experience_years == 0:
        suggestions.append("Add projects: Build personal projects to gain experience.")
    if cert_count < 2:
        suggestions.append("Get certifications: Obtain industry-recognized certifications.")
    if not suggestions:
        suggestions.append("Keep up the good work! Consider advanced courses or specializations.")
    return suggestions

def main():
    st.title("Graphura Resume AI")
    st.markdown("Smart Resume Analyzer")
    
    uploaded_file = st.file_uploader("Upload your resume (TXT or PDF)", type=['txt', 'pdf'])
    
    if uploaded_file is not None:
        text = extract_text_from_file(uploaded_file)
        if text is None:
            st.error("Unsupported file type or PDF support not available.")
            return
        
        st.subheader("Resume Content")
        st.text_area("Extracted Text", text, height=200)
        
        # Extract information
        name = extract_name(text)
        skills = extract_skills(text)
        education = extract_education(text)
        experience_years = extract_experience(text)
        cert_count = extract_certifications(text)
        
        is_fresher = experience_years == 0
        
        # Calculate scores
        skills_score = calculate_skills_score(skills)
        education_score = calculate_education_score(education)
        experience_score = calculate_experience_score(experience_years)
        cert_score = calculate_certificates_score(cert_count)
        total_score = calculate_total_score(skills_score, education_score, experience_score, cert_score)
        
        fit_category = get_fit_category(total_score)
        
        # Display results
        st.subheader(f"Candidate: {name}")
        st.write(f"**Status:** {'Fresher' if is_fresher else 'Experienced'}")
        
        st.subheader("Total Score")
        st.progress(total_score / 100)
        st.write(f"**{total_score:.1f}/100** - {fit_category}")
        
        st.subheader("Score Breakdown")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Skills", f"{skills_score:.1f}/40")
        with col2:
            st.metric("Education", f"{education_score}/30")
        with col3:
            st.metric("Experience", f"{experience_score}/20")
        with col4:
            st.metric("Certificates", f"{cert_score}/10")
        
        st.subheader("Extracted Skills")
        if skills:
            st.write(", ".join(skills))
        else:
            st.write("No skills detected.")
        
        st.subheader("Top 3 Recommended Roles")
        recommendations = recommend_roles(skills)
        for rec in recommendations:
            st.write(f"**{rec['role']}** - Score: {rec['score']}%")
            st.write(f"Reason: {rec['reason']}")
            st.write("---")
        
        st.subheader("AI Suggestions")
        suggestions = get_ai_suggestions(skills, education, experience_years, cert_count)
        for suggestion in suggestions:
            st.write(f"- {suggestion}")

if __name__ == "__main__":
    main()