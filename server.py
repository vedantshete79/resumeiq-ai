import os
import sys
import json
import re
import math
import zipfile
import xml.etree.ElementTree as ET
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# Common ATS Action Verbs
POWER_ACTION_VERBS = [
    "Accelerated", "Architected", "Automated", "Engineered", "Optimized", "Spearheaded",
    "Developed", "Implemented", "Transformed", "Pioneered", "Orchestrated", "Designed",
    "Maximized", "Streamlined", "Deployed", "Cultivated", "Expanded", "Restructured"
]

TECHNICAL_KEYWORDS_DB = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Express", "FastAPI", "Flask",
    "SQL", "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "CI/CD", "Git", "REST API", "GraphQL", "Microservices", "System Design", "Agile", "Scrum",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Pandas", "NumPy",
    "HTML5", "CSS3", "TailwindCSS", "Webpack", "Vite", "Unit Testing", "Jest", "C++", "Java",
    "Go", "Rust", "Data Analysis", "Project Management", "Product Strategy", "ETL", "Spark"
]

def extract_text_from_docx(file_bytes):
    try:
        from io import BytesIO
        with zipfile.ZipFile(BytesIO(file_bytes)) as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            texts = [elem.text for elem in tree.iter() if elem.tag.endswith('t') and elem.text]
            return " ".join(texts)
    except Exception as e:
        return f"Error extracting DOCX text: {str(e)}"

def extract_text_from_pdf(file_bytes):
    try:
        text = file_bytes.decode('latin-1', errors='ignore')
        tj_matches = re.findall(r'\((.*?)\)\s*Tj', text)
        tj_array_matches = re.findall(r'\[\s*(.*?)\s*\]\s*TJ', text)
        
        extracted = []
        for m in tj_matches:
            if len(m.strip()) > 1:
                extracted.append(m.strip())
        for m in tj_array_matches:
            sub_matches = re.findall(r'\((.*?)\)', m)
            extracted.extend([s.strip() for s in sub_matches if len(s.strip()) > 1])
            
        result = " ".join(extracted)
        if len(result.strip()) > 50:
            return result
        words = re.findall(r'[A-Za-z0-9@.\-\s]{3,}', text)
        clean_words = [w.strip() for w in words if len(w.strip()) > 3 and not w.startswith('/')]
        return " ".join(clean_words[:500])
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"

def tokenize(text):
    text = text.lower()
    words = re.findall(r'[a-z0-9+#.-]{2,}', text)
    stopwords = {"and", "the", "to", "of", "a", "in", "for", "is", "on", "that", "by", "this", "with", "i", "you", "it", "not", "or", "be", "are", "from", "at", "as", "your", "all", "have", "new", "more", "an", "was", "we", "will", "home", "can", "us", "about", "if", "page", "my", "has", "search", "free", "but", "our", "one", "other", "do", "no", "information", "time", "they", "site", "he", "up", "may", "what", "which", "their", "news", "out", "use", "any", "there", "see", "only", "so", "his", "when", "contact", "here", "business", "who", "web", "also", "now", "help", "get", "pm", "view", "online"}
    return [w for w in words if w not in stopwords]

def calculate_tfidf_similarity(text1, text2):
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    
    if not tokens1 or not tokens2:
        return 0.0, [], [], []
    
    vocab = list(set(tokens1 + tokens2))
    
    def get_freq(tokens):
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        return freq
    
    freq1 = get_freq(tokens1)
    freq2 = get_freq(tokens2)
    
    vec1 = []
    vec2 = []
    
    N = 2
    for word in vocab:
        df = (1 if word in freq1 else 0) + (1 if word in freq2 else 0)
        idf = math.log((N + 1) / (df + 1)) + 1
        
        tf1 = freq1.get(word, 0) / len(tokens1)
        tf2 = freq2.get(word, 0) / len(tokens2)
        
        vec1.append(tf1 * idf)
        vec2.append(tf2 * idf)
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    
    similarity = (dot_product / (mag1 * mag2)) if (mag1 > 0 and mag2 > 0) else 0.0
    
    set1 = set(tokens1)
    set2 = set(tokens2)
    
    matched = list(set1.intersection(set2))
    missing = list(set2 - set1)
    
    matched_tech = [m.title() for m in matched if len(m) > 2]
    missing_tech = [m.title() for m in missing if len(m) > 2][:15]
    suggested = [k for k in TECHNICAL_KEYWORDS_DB if k.lower() not in set1 and k.lower() in set2][:10]
    if not suggested:
        suggested = [k for k in TECHNICAL_KEYWORDS_DB if k.lower() not in set1][:8]
        
    return min(round(similarity * 100, 1), 98.5), matched_tech[:20], missing_tech[:15], suggested

def analyze_resume_sections(text):
    sections = {
        "Contact Information": {"score": 70, "found": False, "status": "Needs Phone/LinkedIn check"},
        "Summary": {"score": 60, "found": False, "status": "Missing or brief summary"},
        "Skills": {"score": 65, "found": False, "status": "Few hard skills detected"},
        "Experience": {"score": 75, "found": False, "status": "Check bullet point metrics"},
        "Education": {"score": 80, "found": False, "status": "Degree detected"},
        "Projects": {"score": 70, "found": False, "status": "Add live links/metrics"},
        "Certifications": {"score": 50, "found": False, "status": "No certifications header found"}
    }
    
    lower_text = text.lower()
    
    if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text) or re.search(r'\+?\d[\d\s-]{8,}', text):
        sections["Contact Information"]["found"] = True
        sections["Contact Information"]["score"] = 98
        sections["Contact Information"]["status"] = "Email & Phone valid"
        
    if any(k in lower_text for k in ["summary", "profile", "about me", "objective"]):
        sections["Summary"]["found"] = True
        sections["Summary"]["score"] = 95
        sections["Summary"]["status"] = "Executive overview present"
        
    if any(k in lower_text for k in ["skills", "technologies", "competencies", "expertise"]):
        sections["Skills"]["found"] = True
        sections["Skills"]["score"] = 92
        sections["Skills"]["status"] = "Structured skills section present"
        
    if any(k in lower_text for k in ["experience", "employment", "work history", "history"]):
        sections["Experience"]["found"] = True
        sections["Experience"]["score"] = 94
        sections["Experience"]["status"] = "Detailed work history present"
        
    if any(k in lower_text for k in ["education", "degree", "university", "bachelor", "master", "college"]):
        sections["Education"]["found"] = True
        sections["Education"]["score"] = 90
        sections["Education"]["status"] = "Education credentials identified"
        
    if any(k in lower_text for k in ["projects", "key projects", "portfolio"]):
        sections["Projects"]["found"] = True
        sections["Projects"]["score"] = 88
        sections["Projects"]["status"] = "Projects highlighted"
        
    if any(k in lower_text for k in ["certification", "certifications", "licenses", "aws certified"]):
        sections["Certifications"]["found"] = True
        sections["Certifications"]["score"] = 85
        sections["Certifications"]["status"] = "Industry credentials listed"
        
    return sections

def detect_ats_risks(text):
    risks = []
    if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
        risks.append({"level": "Danger", "title": "Missing Email Address", "detail": "ATS parsers require a valid email format to create user candidate files."})
    if not re.search(r'\+?\d[\d\s-]{8,}', text):
        risks.append({"level": "Warning", "title": "Phone Number Missing or Unformatted", "detail": "Add a standard phone number format (e.g. +1 (555) 019-2834)."})
    digits_matches = re.findall(r'\b\d+%\b|\$\d+|\b\d+x\b|\b\d+\s*(?:users|clients|projects|million|k)\b', text, re.IGNORECASE)
    if len(digits_matches) < 3:
        risks.append({"level": "Warning", "title": "Low Quantifiable Metrics", "detail": "Only found a few quantified achievements. Add numbers, %, $, or scale (e.g., 'Boosted efficiency by 34%')."})
    found_power_verbs = [v for v in POWER_ACTION_VERBS if v.lower() in text.lower()]
    if len(found_power_verbs) < 4:
        risks.append({"level": "Warning", "title": "Low Action Verb Density", "detail": "Incorporate strong impact verbs like 'Spearheaded', 'Architected', 'Automated' to start experience bullet points."})
    if len(text.split()) < 150:
        risks.append({"level": "Danger", "title": "Short Resume Length", "detail": "Resume content is under 150 words. ATS algorithms may classify it as incomplete."})
    if not risks:
        risks.append({"level": "Success", "title": "Excellent ATS Formatting", "detail": "No major ATS structural risks detected. Clear headers, metrics, and email format."})
    return risks

def generate_ai_analysis(resume_text, job_desc):
    similarity_score, matched_kw, missing_kw, suggested_kw = calculate_tfidf_similarity(resume_text, job_desc if job_desc else resume_text)
    sections = analyze_resume_sections(resume_text)
    risks = detect_ats_risks(resume_text)
    
    sec_avg = sum(s["score"] for s in sections.values()) / len(sections)
    kw_score = min(round((len(matched_kw) / max(len(matched_kw) + len(missing_kw), 1)) * 100, 1), 95.0) if job_desc else 88.0
    
    ats_score = min(max(round(similarity_score * 0.45 + sec_avg * 0.35 + kw_score * 0.20), 45), 98)
    resume_strength = min(max(round(sec_avg * 0.7 + kw_score * 0.3), 48), 98)
    recruiter_readiness = min(max(round(ats_score * 0.6 + sec_avg * 0.4), 52), 97)
    
    strengths = [
        f"Strong technical alignment with {len(matched_kw)} key terms identified.",
        "Clear section layout enabling accurate ATS text extraction.",
        "Demonstrated executive and hands-on domain leadership in recent roles."
    ]
    weaknesses = [
        f"Missing {len(missing_kw)} high-priority keywords specified in the target job description.",
        "Could strengthen quantifiable impact statements with more percentage and revenue metrics."
    ]
    recruiter_review = f"Candidate presents exceptional executive credentials with an estimated ATS Match of {ats_score}%."
    
    return {
        "ats_score": ats_score,
        "resume_strength": resume_strength,
        "keyword_match_pct": kw_score,
        "recruiter_readiness": recruiter_readiness,
        "keywords": {"matched": matched_kw, "missing": missing_kw, "suggested": suggested_kw},
        "sections": sections,
        "ats_risks": risks,
        "ai_feedback": {"strengths": strengths, "weaknesses": weaknesses, "recruiter_review": recruiter_review}
    }

class ATSRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path).path
        if parsed_path == "/api/health":
            self.send_json_response({"status": "ok", "message": "ResumeIQ AI Server Operational", "ceo": "Mr. Vedant Shete"})
            return
        return super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path).path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            if parsed_path == "/api/upload":
                req_json = json.loads(post_data.decode('utf-8')) if post_data else {}
                self.send_json_response({"status": "success", "text": req_json.get("text", "")})
                return
            elif parsed_path == "/api/analyze":
                req_json = json.loads(post_data.decode('utf-8'))
                result = generate_ai_analysis(req_json.get("resume_text", ""), req_json.get("job_description", ""))
                self.send_json_response(result)
                return
            elif parsed_path == "/api/cover-letter":
                req_json = json.loads(post_data.decode('utf-8'))
                letter = f"Dear Hiring Committee,\n\nI am writing to express my enthusiasm for the role at {req_json.get('company', 'Enterprise Global Corp')}.\n\nSincerely,\n{req_json.get('name', 'Mr. Vedant Shete')}"
                self.send_json_response({"cover_letter": letter})
                return
            else:
                self.send_json_response({"error": "Endpoint not found"}, status=404)
                return
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def send_json_response(self, data, status=200):
        response_bytes = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_bytes)

def run_server():
    port = int(os.environ.get("PORT", 8000))
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
        
    try:
        print(f"Starting ResumeIQ AI Server (CEO: Mr. Vedant Shete) on http://0.0.0.0:{port}...")
        server = HTTPServer(('0.0.0.0', port), ATSRequestHandler)
        server.serve_forever()
    except OSError as err:
        print(f"Socket bind notice ({err}). On Streamlit Cloud, run 'streamlit run app.py' instead.")

if __name__ == '__main__':
    run_server()
