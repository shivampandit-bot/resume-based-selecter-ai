# resume-based-selecter-ai
# 🚀 Graphura Resume AI  Graphura Resume AI is an intelligent resume analysis system that automatically extracts key information from resumes, calculates a weighted score, and recommends the most suitable job roles.  This project is designed to automate and improve the resume screening process using rule-based logic and AI-driven insights.
# 🚀 Graphura Resume AI

Graphura Resume AI is a smart resume analysis and role-matching system that helps automate the hiring process by evaluating candidate resumes and recommending the most suitable roles.

---

## 🎯 Features

- 📄 Resume Upload (PDF/TXT)
- 👤 Automatic Name Extraction
- 🧠 Smart Experience Detection (Fresher / Experienced)
- 🛠 Skill Extraction from Resume
- 🎓 Education Detection
- 📜 Certification Count

---

## 💯 Weighted Scoring System

The system evaluates candidates based on:

- Skills → 40 marks  
- Education → 30 marks  
- Experience → 20 marks  
- Certifications → 10 marks  

Final Score: **0–100**

### Categories:
- ✅ Strong Fit (>80)
- ⚠️ Moderate Fit (60–80)
- ❌ Low Fit (<60)

---

## 🎯 Role Recommendation

Based on extracted skills, the system recommends the **Top 3 job roles**:

- Web Developer  
- Data Analyst  
- AI/ML Engineer  
- Graphic Designer  
- Digital Marketing  
- HR Intern  

---

## 🧠 Intelligent Features

- Detects candidate name from resume automatically  
- Identifies freshers if no experience is found  
- Handles incomplete resumes gracefully  
- Provides AI-based improvement suggestions  

---

## 🛠 Tech Stack

- Python 🐍  
- Streamlit 🎨  
- Regex & Basic NLP 🧠  
- PyMuPDF (PDF Parsing) 📄  

---

## 🚀 How to Run

```bash
pip install streamlit pymupdf
streamlit run app.py
