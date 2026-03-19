import streamlit as st
import re
from collections import Counter
import json

# Optional PDF support
try:
    from PyPDF2 import PdfReader
    PDF_SUPPORTED = True
except ImportError:
    PDF_SUPPORTED = False

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Comprehensive skills list with categories
SKILLS_BY_CATEGORY = {
    'Programming Languages': ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Rust', 'Swift', 'Kotlin'],
    'Web Technologies': ['HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django', 'Flask'],
    'Databases': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Cassandra', 'Firebase'],
    'Data & Analytics': ['Data Analysis', 'Machine Learning', 'Deep Learning', 'Pandas', 'NumPy', 'SciPy', 'Matplotlib', 'TensorFlow', 'PyTorch', 'Scikit-learn'],
    'Big Data': ['Hadoop', 'Spark', 'Hive', 'Kafka'],
    'Cloud & DevOps': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'CI/CD', 'Jenkins'],
    'AI/ML Specific': ['NLP', 'Computer Vision', 'Neural Networks', 'Reinforcement Learning'],
    'Tools & Platforms': ['Git', 'GitHub', 'GitLab', 'Jira', 'Linux', 'Windows', 'Mac'],
    'Soft Skills': ['Agile', 'Scrum', 'Project Management', 'Leadership', 'Communication', 'Problem Solving']
}

FLAT_SKILLS_LIST = [skill for skills in SKILLS_BY_CATEGORY.values() for skill in skills]

# Role definitions
ROLES = {
    'Web Developer': {
        'skills': ['JavaScript', 'HTML', 'CSS', 'React', 'Node.js', 'Python', 'SQL'],
        'description': 'Build and maintain web applications',
        'emoji': '🌐'
    },
    'Data Analyst': {
        'skills': ['SQL', 'Python', 'Data Analysis', 'Pandas', 'NumPy', 'Excel', 'Tableau'],
        'description': 'Analyze data and provide insights',
        'emoji': '📊'
    },
    'AI/ML Engineer': {
        'skills': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'NLP'],
        'description': 'Develop AI/ML models and systems',
        'emoji': '🤖'
    },
    'Backend Engineer': {
        'skills': ['Python', 'Java', 'Node.js', 'SQL', 'Docker', 'AWS', 'Kubernetes'],
        'description': 'Develop server-side applications',
        'emoji': '⚙️'
    },
    'DevOps Engineer': {
        'skills': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Git', 'Jenkins'],
        'description': 'Manage infrastructure and deployments',
        'emoji': '🚀'
    },
    'Data Scientist': {
        'skills': ['Python', 'Machine Learning', 'Statistics', 'Pandas', 'TensorFlow', 'SQL'],
        'description': 'Build and deploy data science models',
        'emoji': '🔬'
    }
}

# ============================================================================
# BACKEND PARSING FUNCTIONS
# ============================================================================

def extract_text_from_file(uploaded_file):
    """Extract text from TXT or PDF file"""
    if uploaded_file.type == 'text/plain':
        return uploaded_file.read().decode('utf-8')
    elif uploaded_file.type == 'application/pdf' and PDF_SUPPORTED:
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'
            return text
        except Exception as e:
            return None
    return None

def extract_name(text):
    """Extract candidate name from resume"""
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        # Skip empty lines and common headers
        if line and not re.match(r'(?i)(resume|cv|curriculum vitae|compiled by|updated|document)', line):
            # Remove common titles
            line = re.sub(r'(?i)\b(mr|ms|mrs|dr|prof|eng|ats|es)\.\s*', '', line)
            # Remove email/phone-like patterns
            if not re.match(r'^(\+?\d|[a-zA-Z0-9._%+-]+@)', line):
                return line.title() if len(line) < 60 else None
    return "Unknown"

def extract_email(text):
    """Extract email address"""
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else None

def extract_phone(text):
    """Extract phone number"""
    match = re.search(r'(?:\+\d{1,3}[-.\s]?)?\(?(?:\d{3})\)?[-.\s]?(?:\d{3})[-.\s]?(?:\d{4})', text)
    return match.group(0) if match else None

def extract_urls(text):
    """Extract GitHub, LinkedIn, Portfolio URLs"""
    urls = {
        'github': None,
        'linkedin': None,
        'portfolio': None
    }
    
    github_match = re.search(r'https?://github\.com/[\w\-./]+|github\.com/[\w\-./]+', text, re.IGNORECASE)
    if github_match:
        urls['github'] = github_match.group(0)
    
    linkedin_match = re.search(r'https?://(?:www\.)?linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
    if linkedin_match:
        urls['linkedin'] = linkedin_match.group(0)
    
    # Look for portfolio websites
    portfolio_match = re.search(r'https?://(?:www\.)(?!github|linkedin)[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}', text, re.IGNORECASE)
    if portfolio_match:
        urls['portfolio'] = portfolio_match.group(0)
    
    return urls

def extract_skills(text):
    """Extract skills from resume"""
    text_lower = text.lower()
    found_skills = []
    
    for skill in FLAT_SKILLS_LIST:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicates

def extract_education(text):
    """Extract education level"""
    text_lower = text.lower()
    
    if re.search(r'\b(ph\.d|phd|ph d|doctorate)\b', text_lower):
        return 'PhD'
    elif re.search(r'\b(masters?|master\'?s?|m\.sc|msc|m\.s)\b', text_lower):
        return 'Masters'
    elif re.search(r'\b(bachelors?|bachelor\'?s?|b\.sc|bsc|b\.a|b\.s|b\.e|b\.tech)\b', text_lower):
        return 'Bachelors'
    elif re.search(r'\b(diploma|certificate|bootcamp|associate)\b', text_lower):
        return 'Others'
    else:
        return 'Others'

def extract_experience(text):
    """Extract years of experience with multiple pattern matching"""
    patterns = [
        r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:professional\s*)?experience',
        r'(?:professional\s*)?experience\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\+\s*(?:years?|yrs?)',
        r'(\d+)\s*(?:years?|yrs?)\s*(?:in|at|of)',
        r'since\s*(\d{4})',  # Extract year and calculate exp
    ]
    
    matches = []
    for pattern in patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            for match in found:
                try:
                    if len(match) == 4 and match.isdigit():  # Year format
                        years = 2026 - int(match)
                        if 0 <= years <= 70:
                            matches.append(years)
                    else:
                        matches.append(int(match))
                except:
                    pass
    
    return max(matches) if matches else 0

def extract_certifications(text):
    """Extract certification count and names"""
    patterns = [
        r'\b(AWS|Azure|Google Cloud|Certified|Certificate|Certification)[:\s]+([A-Za-z\s&]+)',
        r'\b(certificat(?:e|ion)s?)\b'
    ]
    
    count = 0
    names = []
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        count += len(matches)
    
    # Also look for common cert patterns
    cert_keywords = ['aws', 'azure', 'gcp', 'cissp', 'comptia', 'certified', 'certification']
    cert_count = sum(1 for keyword in cert_keywords if keyword in text.lower())
    
    return max(count, cert_count)

def extract_location(text):
    """Extract location/city from resume"""
    # Look for common patterns like "City, State" or "City, Country"
    match = re.search(r'\b([A-Z][a-z]+)\s*,\s*([A-Z]{2}|[A-Z][a-z]+)\b', text)
    if match:
        return f"{match.group(1)}, {match.group(2)}"
    return None

def extract_projects(text):
    """Try to count projects mentioned"""
    patterns = [
        r'\b(project|projects)\s*[:\-]?\s*(\d+)',
        r'\b(built|developed|created|deployed).*?(?:project|application|system)',
    ]
    
    match = re.search(patterns[0], text, re.IGNORECASE)
    if match:
        return int(match.group(2))
    
    # Count mentions of "built", "developed", etc.
    project_count = len(re.findall(patterns[1], text, re.IGNORECASE))
    return project_count if project_count > 0 else None

# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def calculate_skills_score(skills):
    """Calculate skills score (0-40)"""
    if not FLAT_SKILLS_LIST:
        return 0
    match_percentage = (len(skills) / len(FLAT_SKILLS_LIST)) * 100
    return min(40, (match_percentage / 100) * 40)

def calculate_education_score(education):
    """Calculate education score (0-30)"""
    scores = {
        'PhD': 30,
        'Masters': 25,
        'Bachelors': 20,
        'Others': 10
    }
    return scores.get(education, 10)

def calculate_experience_score(experience_years):
    """Calculate experience score (0-20)"""
    if experience_years >= 5:
        return 20
    elif experience_years >= 3:
        return 18
    elif experience_years >= 1:
        return 15
    elif experience_years > 0:
        return 10
    else:
        return 5

def calculate_certificates_score(cert_count):
    """Calculate certificates score (0-10)"""
    if cert_count >= 5:
        return 10
    elif cert_count >= 3:
        return 8
    elif cert_count >= 2:
        return 7
    elif cert_count >= 1:
        return 5
    else:
        return 2

def calculate_total_score(skills_score, education_score, experience_score, cert_score):
    """Calculate total score"""
    return skills_score + education_score + experience_score + cert_score

def get_fit_category(total_score):
    """Categorize fit based on score"""
    if total_score >= 85:
        return ("🌟 Strong Fit", "#04B86C")
    elif total_score >= 70:
        return ("✅ Moderate Fit", "#FFA500")
    elif total_score >= 50:
        return ("⚠️ Developing", "#FF6B6B")
    else:
        return ("📈 Early Stage", "#808080")

# ============================================================================
# RECOMMENDATION FUNCTIONS
# ============================================================================

def recommend_roles(skills):
    """Recommend top 3 roles based on skills match"""
    role_scores = {}
    
    for role, role_data in ROLES.items():
        required_skills = role_data['skills']
        matched = sum(1 for skill in required_skills if skill in skills)
        score = (matched / len(required_skills)) * 100 if required_skills else 0
        role_scores[role] = score
    
    top_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    recommendations = []
    for role, score in top_roles:
        matched_count = sum(1 for skill in ROLES[role]['skills'] if skill in skills)
        total_count = len(ROLES[role]['skills'])
        reason = f"Matches {matched_count}/{total_count} required skills"
        
        recommendations.append({
            'role': role,
            'emoji': ROLES[role]['emoji'],
            'description': ROLES[role]['description'],
            'score': round(score, 1),
            'reason': reason,
            'matched': matched_count,
            'total': total_count
        })
    
    return recommendations

def get_ai_suggestions(skills, education, experience_years, cert_count, projects):
    """Generate AI-powered suggestions for improvement"""
    suggestions = []
    
    # Skills suggestions
    if len(skills) < 5:
        suggestions.append({
            'type': '📚 Skills Gap',
            'text': 'Learn 5+ more in-demand technologies',
            'priority': 'High' if len(skills) < 3 else 'Medium'
        })
    
    # Experience suggestions
    if experience_years == 0:
        suggestions.append({
            'type': '💼 Build Experience',
            'text': 'Create 3-5 portfolio projects to showcase skills',
            'priority': 'High'
        })
    elif experience_years < 2:
        suggestions.append({
            'type': '🎯 Career Growth',
            'text': 'Continue building real-world project experience',
            'priority': 'Medium'
        })
    
    # Certification suggestions
    if cert_count < 2:
        suggestions.append({
            'type': '🏆 Certifications',
            'text': f'Get industry certifications (AWS, Google Cloud, etc.)',
            'priority': 'Medium'
        })
    
    # Education suggestions
    if education == 'Others':
        suggestions.append({
            'type': '🎓 Education',
            'text': 'Consider formal education or bootcamp',
            'priority': 'Low'
        })
    
    # Project suggestions
    if projects is None or projects < 3:
        suggestions.append({
            'type': '🚀 Projects',
            'text': 'Build and deploy 3+ portfolio projects',
            'priority': 'High' if experience_years == 0 else 'Medium'
        })
    
    if not suggestions:
        suggestions.append({
            'type': '⭐ Excellence',
            'text': 'Consider specialization or advanced technique mastery',
            'priority': 'Low'
        })
    
    return suggestions

def calculate_profile_completeness(name, email, phone, urls, skills, education, experience, certs):
    """Calculate how complete the resume is"""
    completeness_checks = [
        name != "Unknown",
        email is not None,
        phone is not None,
        bool(urls.get('github') or urls.get('linkedin')),
        len(skills) >= 5,
        education != 'Others',
        experience > 0,
        certs > 0
    ]
    
    completeness_score = (sum(completeness_checks) / len(completeness_checks)) * 100
    return round(completeness_score, 1)

# ============================================================================
# STREAMLIT UI
# ============================================================================

def main():
    # Page configuration
    st.set_page_config(
        page_title="Graphura Resume AI",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
            /* Main styling */
            :root {
                --primary-color: #6366F1;
                --secondary-color: #EC4899;
                --success-color: #10B981;
                --warning-color: #F59E0B;
                --danger-color: #EF4444;
            }
            
            .main {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                opacity: 0.99;
            }
            
            /* Header styling */
            .header-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 15px;
                color: white;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            
            /* Score card styling */
            .score-card {
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                margin: 0.5rem 0;
                border-left: 5px solid #667eea;
            }
            
            /* Metric styling */
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            /* Role recommendation card */
            .role-card {
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 5px solid #667eea;
                margin: 1rem 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            /* Skills container */
            .skills-container {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
            }
            
            .skill-tag {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 500;
            }
            
            /* Section headers */
            .section-header {
                color: white;
                font-size: 1.8rem;
                font-weight: bold;
                margin-top: 1rem;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 3px solid white;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="header-container">
            <h1>🚀 Graphura Resume AI</h1>
            <p style="font-size: 1.1rem; margin: 0;">Intelligent Resume Analysis & Career Guidance</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📋 About This Tool")
        st.info("""
        **Graphura Resume AI** analyzes your resume and provides:
        - 📊 Scoring based on skills, education, experience
        - 💼 Personalized job role recommendations
        - 📈 Career improvement suggestions
        - ✅ Profile completeness analysis
        """)
    
    # File upload
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "📄 Upload Your Resume",
            type=['txt', 'pdf'],
            key='resume_uploader'
        )
    
    if uploaded_file is not None:
        text = extract_text_from_file(uploaded_file)
        
        if text is None:
            st.error("❌ Could not read file. Please ensure it's a valid TXT or PDF file.")
            return
        
        # Extract all information
        with st.spinner('🔍 Analyzing resume...'):
            name = extract_name(text)
            email = extract_email(text)
            phone = extract_phone(text)
            urls = extract_urls(text)
            skills = extract_skills(text)
            education = extract_education(text)
            experience_years = extract_experience(text)
            cert_count = extract_certifications(text)
            location = extract_location(text)
            projects = extract_projects(text)
            
            is_fresher = experience_years == 0
            
            # Calculate scores
            skills_score = calculate_skills_score(skills)
            education_score = calculate_education_score(education)
            experience_score = calculate_experience_score(experience_years)
            cert_score = calculate_certificates_score(cert_count)
            total_score = calculate_total_score(skills_score, education_score, experience_score, cert_score)
            
            fit_category, fit_color = get_fit_category(total_score)
            profile_completeness = calculate_profile_completeness(
                name, email, phone, urls, skills, education, experience_years, cert_count
            )
        
        # Tabs for organized display
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Score & Analysis",
            "🎯 Recommendations",
            "💡 Suggestions",
            "👤 Profile Details"
        ])
        
        # =================================================================
        # TAB 1: Score & Analysis
        # =================================================================
        with tab1:
            st.markdown("""---""")
            
            # Candidate info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"### 👤 {name}")
                if location:
                    st.caption(f"📍 {location}")
            with col2:
                status_badge = "🆕 **Fresher**" if is_fresher else f"✨ **{experience_years} Years Experienced**"
                st.markdown(f"### {status_badge}")
            with col3:
                st.markdown(f"### {fit_category}")
            
            st.markdown("""---""")
            
            # Overall score
            st.markdown("## 📈 Overall Score")
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.progress(total_score / 100, text=f"{total_score:.1f} / 100")
            with col2:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Completeness", f"{profile_completeness}%")
                with col_b:
                    st.metric("Grade", "B+" if total_score >= 70 else "B" if total_score >= 60 else "C+")
            
            st.markdown("""---""")
            
            # Score breakdown
            st.markdown("## 📋 Score Breakdown")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                    <div class="score-card">
                        <div style="text-align: center;">
                            <h3>📚 Skills</h3>
                            <p style="font-size: 2rem; font-weight: bold; color: #667eea;">{skills_score:.1f}</p>
                            <p style="font-size: 0.9rem; color: gray;">/ 40</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="score-card">
                        <div style="text-align: center;">
                            <h3>🎓 Education</h3>
                            <p style="font-size: 2rem; font-weight: bold; color: #764ba2;">{education_score}</p>
                            <p style="font-size: 0.9rem; color: gray;">/ 30</p>
                            <p style="font-size: 0.8rem; color: #667eea;">{education}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="score-card">
                        <div style="text-align: center;">
                            <h3>💼 Experience</h3>
                            <p style="font-size: 2rem; font-weight: bold; color: #EC4899;">{experience_score}</p>
                            <p style="font-size: 0.9rem; color: gray;">/ 20</p>
                            <p style="font-size: 0.8rem; color: #667eea;">{experience_years} yrs</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <div class="score-card">
                        <div style="text-align: center;">
                            <h3>🏆 Certificates</h3>
                            <p style="font-size: 2rem; font-weight: bold; color: #10B981;">{cert_score}</p>
                            <p style="font-size: 0.9rem; color: gray;">/ 10</p>
                            <p style="font-size: 0.8rem; color: #667eea;">{cert_count} found</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""---""")
            
            # Skills visualization
            st.markdown("## 🔧 Detected Skills")
            if skills:
                st.markdown(f"**Found {len(skills)} skills:**")
                cols = st.columns(3)
                for idx, skill in enumerate(sorted(skills)):
                    with cols[idx % 3]:
                        st.markdown(f"✅ {skill}", help=f"Skill: {skill}")
            else:
                st.warning("⚠️ No skills detected. Make sure to include skills in your resume.")
        
        # =================================================================
        # TAB 2: Recommendations
        # =================================================================
        with tab2:
            st.markdown("""---""")
            st.markdown("## 🎯 Top 3 Career Recommendations")
            st.markdown(f"Based on your {len(skills)} detected skills and {education} education")
            st.markdown("""---""")
            
            recommendations = recommend_roles(skills)
            
            for idx, rec in enumerate(recommendations, 1):
                match_percentage = (rec['matched'] / rec['total']) * 100
                
                st.markdown(f"""
                    <div class="role-card">
                        <h3>{idx}. {rec['emoji']} {rec['role']}</h3>
                        <p style="color: #666; margin: 0.5rem 0;">{rec['description']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.progress(match_percentage / 100, text=f"{match_percentage:.0f}% Match")
                
                with col2:
                    st.metric("Score", f"{rec['score']:.1f}%")
                
                with col3:
                    st.caption(f"{rec['matched']}/{rec['total']} skills match")
                
                st.markdown(f"**Why?** {rec['reason']}")
                st.markdown("---")
        
        # =================================================================
        # TAB 3: Suggestions
        # =================================================================
        with tab3:
            st.markdown("""---""")
            st.markdown("## 💡 AI-Powered Improvement Suggestions")
            st.markdown("""---""")
            
            suggestions = get_ai_suggestions(skills, education, experience_years, cert_count, projects)
            
            for suggestion in suggestions:
                priority_color = {
                    'High': '🔴',
                    'Medium': '🟡',
                    'Low': '🟢'
                }
                
                st.markdown(f"""
                    <div style="
                        background: white;
                        padding: 1.5rem;
                        border-radius: 12px;
                        border-left: 5px solid #667eea;
                        margin: 1rem 0;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    ">
                        <h4>{suggestion['type']}</h4>
                        <p style="margin: 0.5rem 0; font-size: 1.05rem;">{suggestion['text']}</p>
                        <p style="margin: 0; color: gray; font-size: 0.9rem;">
                            Priority: {priority_color[suggestion['priority']]} {suggestion['priority']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        
        # =================================================================
        # TAB 4: Profile Details
        # =================================================================
        with tab4:
            st.markdown("""---""")
            st.markdown("## 👤 Profile Information")
            st.markdown("""---""")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Personal Information")
                st.write(f"**Name:** {name}")
                if email:
                    st.write(f"**Email:** {email}")
                else:
                    st.warning("⚠️ No email found in resume")
                
                if phone:
                    st.write(f"**Phone:** {phone}")
                else:
                    st.info("ℹ️ No phone number found")
                
                if location:
                    st.write(f"**Location:** {location}")
            
            with col2:
                st.markdown("### Online Presence")
                if urls['github']:
                    st.write(f"🐙 **GitHub:** [Profile]({urls['github']})")
                else:
                    st.warning("⚠️ No GitHub profile found")
                
                if urls['linkedin']:
                    st.write(f"💼 **LinkedIn:** [Profile]({urls['linkedin']})")
                else:
                    st.info("ℹ️ No LinkedIn profile found")
                
                if urls['portfolio']:
                    st.write(f"🌐 **Portfolio:** [Website]({urls['portfolio']})")
            
            st.markdown("""---""")
            
            # Resume content
            with st.expander("📄 View Full Resume Text"):
                st.text_area("Resume Content", text, height=300, disabled=True)
        
        st.markdown("""---""")
        st.success("✅ Analysis complete! Download your results or share with recruiters.")

if __name__ == "__main__":
    main()