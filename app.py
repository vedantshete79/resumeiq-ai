import streamlit as st
import json
import re
import math
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd

# Try importing Plotly for visual analytics
try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION & CYBER DASHBOARD THEME
# ==============================================================================
st.set_page_config(
    page_title="ResumeIQ AI – Premium ATS Resume Analyzer | CEO: Mr. Vedant Shete",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cyber Glassmorphism CSS Injection
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

  /* Base Cyber Dark Theme */
  .stApp {
    background-color: #0B1120;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #FFFFFF;
  }

  /* Hide Default Streamlit Menu & Footer for SaaS look */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}

  /* Glassmorphism Cards */
  div[data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 2.2rem !important;
    color: #FFFFFF !important;
  }

  .glass-card {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }

  .ceo-banner {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(124, 58, 237, 0.2));
    border: 1px solid rgba(124, 58, 237, 0.4);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 24px;
  }

  /* Custom Badges */
  .badge-matched {
    background-color: rgba(34, 197, 94, 0.15);
    color: #4ADE80;
    border: 1px solid rgba(34, 197, 94, 0.4);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin: 4px;
  }

  .badge-missing {
    background-color: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin: 4px;
  }

  .badge-suggested {
    background-color: rgba(59, 130, 246, 0.15);
    color: #60A5FA;
    border: 1px solid rgba(59, 130, 246, 0.4);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin: 4px;
  }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# NLP ENGINE & PARSER LOGIC
# ==============================================================================
POWER_ACTION_VERBS = [
    "Accelerated", "Architected", "Automated", "Engineered", "Optimized", "Spearheaded",
    "Developed", "Implemented", "Transformed", "Pioneered", "Orchestrated", "Designed",
    "Maximized", "Streamlined", "Deployed", "Cultivated", "Expanded", "Restructured"
]

TECHNICAL_KEYWORDS_DB = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Express", "FastAPI", "Flask",
    "SQL", "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "CI/CD", "Git", "REST API", "GraphQL", "Microservices", "System Design", "Agile", "Scrum",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Pandas", "NumPy"
]

def extract_text_from_file(uploaded_file):
    """Extract plain text from uploaded PDF, DOCX, or TXT file."""
    if uploaded_file is None:
        return ""
    try:
        filename = uploaded_file.name.lower()
        content = uploaded_file.read()
        
        if filename.endswith(".docx"):
            from io import BytesIO
            with zipfile.ZipFile(BytesIO(content)) as z:
                xml_content = z.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                texts = [elem.text for elem in tree.iter() if elem.tag.endswith('t') and elem.text]
                return " ".join(texts)
        elif filename.endswith(".pdf"):
            text = content.decode('latin-1', errors='ignore')
            tj_matches = re.findall(r'\((.*?)\)\s*Tj', text)
            if len(tj_matches) > 5:
                return " ".join(tj_matches)
            words = re.findall(r'[A-Za-z0-9@.\-\s]{3,}', text)
            return " ".join([w.strip() for w in words if len(w.strip()) > 3])
        else:
            return content.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"File extraction note: {str(e)}"

def tokenize(text):
    text = text.lower()
    words = re.findall(r'[a-z0-9+#.-]{2,}', text)
    stopwords = {"and", "the", "to", "of", "a", "in", "for", "is", "on", "that", "by", "this", "with", "i", "you", "it", "not", "or", "be", "are", "from", "at", "as", "your", "all", "have", "new", "more", "an", "was", "we", "will", "home", "can", "us", "about", "if", "page", "my", "has", "search", "free", "but", "our", "one", "other", "do", "no", "information", "time", "they", "site", "he", "up", "may", "what", "which", "their", "news", "out", "use", "any", "there", "see", "only", "so", "his", "when", "contact", "here", "business", "who", "web", "also", "now", "help", "get", "pm", "view", "online"}
    return [w for w in words if w not in stopwords]

def analyze_ats(resume_text, job_desc):
    tokens1 = tokenize(resume_text)
    tokens2 = tokenize(job_desc if job_desc else resume_text)
    
    if not tokens1 or not tokens2:
        return 0, 0, 0, 0, [], [], [], {}, [], {}
    
    set1 = set(tokens1)
    set2 = set(tokens2)
    
    matched = [m.title() for m in set1.intersection(set2) if len(m) > 2][:20]
    missing = [m.title() for m in set2 - set1 if len(m) > 2][:15]
    suggested = [k for k in TECHNICAL_KEYWORDS_DB if k.lower() not in set1][:8]
    
    kw_match_pct = min(round((len(matched) / max(len(matched) + len(missing), 1)) * 100, 1), 96.0) if job_desc else 88.0
    
    # Section Diagnostics
    sections = {
        "Contact Information": 98 if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text) else 70,
        "Summary": 95 if any(k in resume_text.lower() for k in ["summary", "profile", "about me"]) else 65,
        "Skills": 92 if any(k in resume_text.lower() for k in ["skills", "technologies"]) else 68,
        "Experience": 94 if any(k in resume_text.lower() for k in ["experience", "employment", "history"]) else 72,
        "Education": 90 if any(k in resume_text.lower() for k in ["education", "degree", "university"]) else 75,
        "Projects": 88 if any(k in resume_text.lower() for k in ["projects", "portfolio"]) else 70,
        "Certifications": 85 if any(k in resume_text.lower() for k in ["certifications", "licenses"]) else 55
    }
    
    sec_avg = sum(sections.values()) / len(sections)
    ats_score = min(max(round(sec_avg * 0.5 + kw_match_pct * 0.5), 48), 98)
    resume_strength = min(max(round(sec_avg * 0.7 + kw_match_pct * 0.3), 50), 98)
    recruiter_readiness = min(max(round(ats_score * 0.6 + sec_avg * 0.4), 52), 97)
    
    risks = []
    if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text):
        risks.append("⚠️ Missing Email Address in header.")
    if len(re.findall(r'\b\d+%\b|\$\d+|\b\d+x\b', resume_text)) < 3:
        risks.append("⚠️ Low Quantifiable Metrics count (add %, $, or 10x numbers).")
    if len(resume_text.split()) < 150:
        risks.append("🔴 Short Resume Length (< 150 words).")
    if not risks:
        risks.append("🟢 Excellent ATS Structural Layout & Metric Density.")
        
    return ats_score, resume_strength, kw_match_pct, recruiter_readiness, matched, missing, suggested, sections, risks

# ==============================================================================
# SAMPLE RESUMES DATASET
# ==============================================================================
SAMPLE_RESUME = """Mr. Vedant Shete
vedant.shete@resumeiq.ai | +1 (555) 019-2834 | San Francisco, CA | linkedin.com/in/vedant-shete

PROFESSIONAL SUMMARY
Visionary Founder & Chief Executive Officer with proven leadership in architecting enterprise AI platforms, optimizing cloud-native microservices, and leading high-performing engineering teams. Expert in Python, React, TypeScript, FastAPI, PostgreSQL, and Docker.

WORK EXPERIENCE
Founder & Chief Executive Officer | ResumeIQ AI (2022 - Present)
• Architected high-throughput Python FastAPI microservices handling over 10M daily requests with 99.99% uptime.
• Spearheaded frontend migration to React & TypeScript, boosting user engagement by 38% and reducing bundle size by 45%.
• Automated CI/CD deployment pipelines using Docker, Kubernetes, and GitHub Actions, cutting release cycles from 3 days to 15 minutes.
• Optimized PostgreSQL query execution plans and Redis caching, reducing API latency by 42%.

SKILLS
Programming: Python, JavaScript, TypeScript, SQL, HTML5, CSS3, C++
Frameworks & Libraries: React, Next.js, Node.js, FastAPI, Flask, Express, TailwindCSS
Databases & Cloud: PostgreSQL, MongoDB, Redis, Docker, AWS (S3, EC2, ECS), Git, CI/CD, Agile

EDUCATION
Bachelor of Science in Computer Science & Artificial Intelligence (2015 - 2019)"""

SAMPLE_JOB_DESC = """Chief Executive Officer / Chief Technology Officer
Responsibilities:
• Drive company product vision, engineering strategy, and enterprise AI innovation.
• Architect, build, and maintain high-performance web applications using Python, FastAPI, and React.
• Optimize backend database queries (PostgreSQL / Redis) and microservice communication.
• Deploy scalable cloud infrastructure on AWS using Docker, Kubernetes, and Terraform.

Requirements:
• 5+ years of software engineering & tech executive leadership experience with Python and JavaScript/TypeScript.
• Deep proficiency in React, Node.js or FastAPI, SQL databases, and Redis caching.
• Solid experience with Docker, CI/CD pipelines, and AWS cloud environments."""

# ==============================================================================
# SIDEBAR NAVIGATION & EXECUTIVE BRANDING
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚡ ResumeIQ AI")
    st.markdown("#### CEO: Mr. Vedant Shete")
    st.caption("Enterprise ATS Optimization Suite 4.0")
    st.divider()

    navigation = st.radio(
        "Navigate Workspace",
        ["🎯 ATS Dashboard", "📊 Visual Analytics", "⚠️ ATS Risk Diagnostics", "📝 AI Resume Builder", "✉️ Cover Letter Generator", "💼 Interview Prep"]
    )
    
    st.divider()
    st.markdown("**Executive Profile**")
    st.info("👤 **Mr. Vedant Shete**\n\nFounder & Chief Executive Officer")

# ==============================================================================
# MAIN VIEW PANEL ROUTING
# ==============================================================================

# Executive Header Banner
st.markdown("""
<div class="ceo-banner">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin: 0; color: #FFFFFF;">ResumeIQ AI Platform</h2>
            <p style="margin: 4px 0 0 0; color: #93C5FD; font-size: 14px;">Founded by CEO Mr. Vedant Shete | Real-Time Recruiter & ATS Analysis Engine</p>
        </div>
        <div style="background: rgba(37, 99, 235, 0.3); padding: 8px 16px; border-radius: 20px; border: 1px solid #2563EB; font-weight: 700; color: #93C5FD;">
            CEO: Mr. Vedant Shete
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if navigation == "🎯 ATS Dashboard":
    st.subheader("ATS Resume Analysis Engine")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            resume_input = extract_text_from_file(uploaded_file)
            st.success(f"Loaded {uploaded_file.name}")
        else:
            resume_input = st.text_area("Resume Content", value=SAMPLE_RESUME, height=220)
            
    with col2:
        job_desc_input = st.text_area("Target Job Description", value=SAMPLE_JOB_DESC, height=310)

    if st.button("🚀 Run AI ATS Analysis Engine", type="primary", use_container_width=True):
        ats_score, strength, kw_match, readiness, matched, missing, suggested, sections, risks = analyze_ats(resume_input, job_desc_input)
        
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ATS Match Score", f"{ats_score}%", "+Optimal")
        m2.metric("Resume Strength", f"{strength}%", "Executive Grade")
        m3.metric("Keyword Match", f"{kw_match}%", f"{len(matched)} Matched")
        m4.metric("Recruiter Readiness", f"{readiness}%", "Shortlist Ready")
        
        st.divider()
        c_kw1, c_kw2 = st.columns(2)
        with c_kw1:
            st.markdown("### 🟢 Matched Keywords")
            st.write(" ".join([f'<span class="badge-matched">✓ {k}</span>' for k in matched]), unsafe_allow_html=True)
        with c_kw2:
            st.markdown("### 🔴 Missing Target Keywords")
            st.write(" ".join([f'<span class="badge-missing">✕ {k}</span>' for k in missing]), unsafe_allow_html=True)
            
        st.markdown("### 🔵 AI Suggested Badges")
        st.write(" ".join([f'<span class="badge-suggested">+ {k}</span>' for k in suggested]), unsafe_allow_html=True)

elif navigation == "📊 Visual Analytics":
    st.subheader("Visual Competencies & Keyword Frequencies")
    ats_score, strength, kw_match, readiness, matched, missing, suggested, sections, risks = analyze_ats(SAMPLE_RESUME, SAMPLE_JOB_DESC)
    
    v1, v2 = st.columns(2)
    with v1:
        st.markdown("#### Section Quality Breakdown")
        df_sec = pd.DataFrame(list(sections.items()), columns=["Section", "Score"])
        if HAS_PLOTLY:
            fig_radar = px.line_polar(df_sec, r='Score', theta='Section', line_close=True)
            fig_radar.update_traces(fill='toself', line_color='#2563EB')
            fig_radar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF')
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.bar_chart(df_sec.set_index("Section"))
            
    with v2:
        st.markdown("#### Keyword Distribution")
        df_kw = pd.DataFrame({
            "Category": ["Matched", "Missing", "Suggested"],
            "Count": [len(matched), len(missing), len(suggested)]
        })
        if HAS_PLOTLY:
            fig_bar = px.bar(df_kw, x='Category', y='Count', color='Category', color_discrete_map={'Matched': '#22C55E', 'Missing': '#EF4444', 'Suggested': '#3B82F6'})
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.bar_chart(df_kw.set_index("Category"))

elif navigation == "⚠️ ATS Risk Diagnostics":
    st.subheader("ATS Formatting Risk Audit")
    _, _, _, _, _, _, _, _, risks = analyze_ats(SAMPLE_RESUME, SAMPLE_JOB_DESC)
    
    for r in risks:
        if "⚠️" in r or "🔴" in r:
            st.warning(r)
        else:
            st.success(r)

elif navigation == "📝 AI Resume Builder":
    st.subheader("AI Resume Builder & Real-Time Preview")
    b_name = st.text_input("Full Name", value="Mr. Vedant Shete")
    b_title = st.text_input("Target Job Title", value="Chief Executive Officer / Tech Lead")
    b_summary = st.text_area("Professional Summary", value="Visionary Technology Executive and Founder with proven leadership in designing enterprise AI suites, architecting cloud-native microservices, and leading high-performance engineering teams.")
    b_skills = st.text_input("Skills (comma separated)", value="Python, React, FastAPI, PostgreSQL, Docker, AWS, System Architecture")
    
    st.markdown("### Live Formatted Resume Preview")
    st.markdown(f"""
    <div style="background: #FFFFFF; color: #1E293B; padding: 30px; border-radius: 12px; font-family: sans-serif;">
        <h1 style="color: #0F172A; margin-bottom: 2px;">{b_name}</h1>
        <div style="color: #2563EB; font-weight: 700; margin-bottom: 12px;">{b_title}</div>
        <hr style="border-top: 2px solid #2563EB;">
        <h3 style="color: #0F172A;">Summary</h3>
        <p>{b_summary}</p>
        <h3 style="color: #0F172A;">Skills</h3>
        <p><strong>{b_skills}</strong></p>
    </div>
    """, unsafe_allow_html=True)

elif navigation == "✉️ Cover Letter Generator":
    st.subheader("AI Cover Letter Generator")
    c_name = st.text_input("Applicant Name", value="Mr. Vedant Shete")
    c_company = st.text_input("Target Company", value="Enterprise Global Corp")
    c_role = st.text_input("Target Role", value="Chief Executive Officer")
    
    if st.button("Generate Cover Letter", type="primary"):
        letter = f"""Dear Board of Directors & Hiring Committee at {c_company},

I am writing to express my strong enthusiasm for the {c_role} position at {c_company}. As Founder & CEO of ResumeIQ AI, I have led high-performing engineering and product teams in delivering scalable enterprise AI platforms, optimizing cloud microservices, and driving exponential growth.

My strategic approach aligns directly with {c_company}'s commitment to technological leadership and innovation. Under my executive leadership, our engineering teams successfully deployed mission-critical microservices handling tens of millions of requests with 99.99% reliability.

Sincerely,

{c_name}
Founder & CEO, ResumeIQ AI
vedant.shete@resumeiq.ai | +1 (555) 019-2834"""
        st.text_area("Generated Output", value=letter, height=280)

elif navigation == "💼 Interview Prep":
    st.subheader("Interview Preparation Generator")
    st.info("💡 **Question 1 (Executive Strategy):** How do you align engineering roadmap with enterprise ROI?")
    st.caption("STAR Answer: Establish key performance indicators (KPIs) linking technical output (latency, uptime, scaling) directly to user retention and ARR.")
    st.divider()
    st.info("💡 **Question 2 (System Architecture):** How do you design zero-downtime distributed systems?")
    st.caption("STAR Answer: Utilize active-active multi-region deployment, automated circuit breakers, Redis read-replicas, and zero-downtime blue/green deployments.")
