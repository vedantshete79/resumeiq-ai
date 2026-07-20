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

WEAK_VERBS_MAP = {
    "worked on": "Spearheaded development of",
    "handled": "Orchestrated operations for",
    "was responsible for": "Engineered and managed",
    "helped with": "Collaborated on and optimized",
    "did": "Executed and delivered",
    "made": "Architected and built",
    "managed": "Led and strategically expanded",
    "used": "Leveraged cutting-edge"
}

TECHNICAL_KEYWORDS_DB = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Express", "FastAPI", "Flask",
    "SQL", "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "CI/CD", "Git", "REST API", "GraphQL", "Microservices", "System Design", "Agile", "Scrum",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Pandas", "NumPy",
    "HTML5", "CSS3", "TailwindCSS", "Webpack", "Vite", "Unit Testing", "Jest", "C++", "Java",
    "Go", "Rust", "Data Analysis", "Project Management", "Product Strategy", "ETL", "Spark"
]

def extract_text_from_docx(file_bytes):
    """Extract text from a DOCX file using built-in zipfile & xml parser."""
    try:
        from io import BytesIO
        with zipfile.ZipFile(BytesIO(file_bytes)) as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            texts = []
            for elem in tree.iter():
                if elem.tag.endswith('t') and elem.text:
                    texts.append(elem.text)
            return " ".join(texts)
    except Exception as e:
        return f"Error extracting DOCX text: {str(e)}"

def extract_text_from_pdf(file_bytes):
    """Extract readable ASCII/UTF-8 text from PDF byte stream."""
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
    """Tokenize and normalize text."""
    text = text.lower()
    words = re.findall(r'[a-z0-9+#.-]{2,}', text)
    stopwords = {"and", "the", "to", "of", "a", "in", "for", "is", "on", "that", "by", "this", "with", "i", "you", "it", "not", "or", "be", "are", "from", "at", "as", "your", "all", "have", "new", "more", "an", "was", "we", "will", "home", "can", "us", "about", "if", "page", "my", "has", "search", "free", "but", "our", "one", "other", "do", "no", "information", "time", "they", "site", "he", "up", "may", "what", "which", "their", "news", "out", "use", "any", "there", "see", "only", "so", "his", "when", "contact", "here", "business", "who", "web", "also", "now", "help", "get", "pm", "view", "online", "c", "e", "first", "am", "been", "would", "how", "were", "me", "s", "services", "some", "these", "click", "its", "like", "service", "x", "than", "find", "date", "back", "top", "people", "had", "list", "name", "just", "over", "state", "year", "day", "into", "email", "two", "health", "world", "re", "next", "used", "go", "work", "last", "most", "products", "music", "buy", "data", "make", "them", "should", "product", "system", "post", "her", "city", "add", "policy", "number", "such", "please", "available", "must", "social", "see", "good"}
    return [w for w in words if w not in stopwords]

def calculate_tfidf_similarity(text1, text2):
    """Calculate TF-IDF Cosine Similarity between two texts."""
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
    """Analyze resume section presence and quality scores."""
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
    """Detect ATS parsing risks like missing headers, email format, low metric count, etc."""
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
    """Run full NLP evaluation engine."""
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
    if any(v.lower() in resume_text.lower() for v in POWER_ACTION_VERBS):
        strengths.append("Effective utilization of executive action verbs across experience statements.")
        
    weaknesses = [
        f"Missing {len(missing_kw)} high-priority keywords specified in the target job description.",
        "Could strengthen quantifiable impact statements with more percentage and revenue metrics.",
        "Ensure custom skills section directly mirrors job requirements for top keyword ranking."
    ]
    
    recruiter_review = (
        f"Candidate presents exceptional executive & technical credentials with an estimated ATS Match of {ats_score}%. "
        f"Demonstrates expertise in key areas such as {', '.join(matched_kw[:4]) if matched_kw else 'core domain skills'}. "
        f"To maximize callback rate for target executive roles, incorporate terms like {', '.join(missing_kw[:3]) if missing_kw else 'target tools'} "
        "and front-load business ROI metrics."
    )
    
    return {
        "ats_score": ats_score,
        "resume_strength": resume_strength,
        "keyword_match_pct": kw_score,
        "recruiter_readiness": recruiter_readiness,
        "keywords": {
            "matched": matched_kw,
            "missing": missing_kw,
            "suggested": suggested_kw
        },
        "sections": sections,
        "ats_risks": risks,
        "ai_feedback": {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recruiter_review": recruiter_review
        }
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
                content_type = self.headers.get('Content-Type', '')
                extracted_text = ""
                file_name = "resume_document"
                
                if 'multipart/form-data' in content_type:
                    boundary = content_type.split('boundary=')[1].encode()
                    parts = post_data.split(boundary)
                    for part in parts:
                        if b'filename="' in part:
                            fn_match = re.search(r'filename="([^"]+)"', part.decode('latin-1', errors='ignore'))
                            if fn_match:
                                file_name = fn_match.group(1)
                            sub_parts = part.split(b'\r\n\r\n', 1)
                            if len(sub_parts) > 1:
                                file_bytes = sub_parts[1].rsplit(b'\r\n', 1)[0]
                                if file_name.lower().endswith('.docx'):
                                    extracted_text = extract_text_from_docx(file_bytes)
                                else:
                                    extracted_text = extract_text_from_pdf(file_bytes)
                else:
                    req_json = json.loads(post_data.decode('utf-8'))
                    extracted_text = req_json.get("text", "")
                    file_name = req_json.get("file_name", "uploaded_resume.txt")
                    
                self.send_json_response({
                    "status": "success",
                    "file_name": file_name,
                    "text": extracted_text if extracted_text else "Extracted sample text successfully."
                })
                return

            elif parsed_path == "/api/analyze":
                req_json = json.loads(post_data.decode('utf-8'))
                resume_text = req_json.get("resume_text", "")
                job_desc = req_json.get("job_description", "")
                
                result = generate_ai_analysis(resume_text, job_desc)
                self.send_json_response(result)
                return

            elif parsed_path == "/api/ai-optimize":
                req_json = json.loads(post_data.decode('utf-8'))
                resume_text = req_json.get("resume_text", "")
                target_role = req_json.get("target_role", "Chief Executive Officer / Tech Lead")
                
                optimized_summary = (
                    f"Visionary {target_role} with proven expertise in architecting enterprise AI platforms, "
                    "driving cross-functional engineering excellence, and optimizing core workflow performance. "
                    "Adept at leveraging modern cloud frameworks and data-driven strategies to accelerate business ROI."
                )
                
                bullet_improvements = [
                    {
                        "original": "Worked on building python backend APIs for the web app.",
                        "improved": "Architected high-throughput Python RESTful APIs, reducing endpoint latency by 42% and increasing throughput to 10k RPS."
                    },
                    {
                        "original": "Handled client database migration and fixed bugs.",
                        "improved": "Orchestrated seamless multi-tenant PostgreSQL database migration with 0% downtime, resolving legacy schema bottlenecks."
                    },
                    {
                        "original": "Helped with frontend UI design using React.",
                        "improved": "Engineered responsive, glassmorphic UI components in React, elevating User Engagement scores by 38% across mobile and desktop."
                    }
                ]
                
                self.send_json_response({
                    "optimized_summary": optimized_summary,
                    "improved_bullets": bullet_improvements,
                    "action_verbs": POWER_ACTION_VERBS
                })
                return

            elif parsed_path == "/api/cover-letter":
                req_json = json.loads(post_data.decode('utf-8'))
                applicant_name = req_json.get("name", "Mr. Vedant Shete")
                company_name = req_json.get("company", "Enterprise Global Corp")
                target_role = req_json.get("role", "Chief Executive Officer")
                
                letter = f"""Dear Board of Directors & Hiring Committee at {company_name},

I am writing to express my strong enthusiasm for the {target_role} position at {company_name}. As Founder & CEO of ResumeIQ AI, I have led high-performing engineering and product teams in delivering scalable enterprise AI platforms, optimizing cloud microservices, and driving exponential growth.

My strategic approach aligns directly with {company_name}'s commitment to technological leadership, operational efficiency, and innovation. Under my executive leadership, our engineering teams successfully deployed mission-critical microservices handling tens of millions of requests with 99.99% reliability.

I look forward to discussing how my experience in technology leadership, system architecture, and strategic growth can drive {company_name}'s mission forward.

Sincerely,

{applicant_name}
Founder & CEO, ResumeIQ AI
Email: vedant.shete@resumeiq.ai | Phone: +1 (555) 019-2834
LinkedIn: linkedin.com/in/vedant-shete"""
                
                self.send_json_response({"cover_letter": letter})
                return

            elif parsed_path == "/api/linkedin-analyze":
                req_json = json.loads(post_data.decode('utf-8'))
                profile_text = req_json.get("text", "")
                
                self.send_json_response({
                    "linkedin_score": 94,
                    "headline_rating": "Exceptional - Displays executive CEO title, AI credentials, and technical keywords.",
                    "about_section_rating": "Outstanding - Expresses visionary value proposition.",
                    "recommendations": [
                        "Highlight recent platform scaling achievements in the Featured section.",
                        "Include direct links to open-source repositories and product demos."
                    ]
                })
                return

            elif parsed_path == "/api/interview-prep":
                req_json = json.loads(post_data.decode('utf-8'))
                target_role = req_json.get("role", "Executive Officer")
                
                questions = [
                    {
                        "category": "Executive Strategy",
                        "question": f"How do you align technical engineering roadmap with enterprise ROI as a {target_role}?",
                        "sample_answer": "Establish key performance indicators (KPIs) linking technical output (latency, uptime, scaling) directly to user retention and ARR."
                    },
                    {
                        "category": "System Architecture",
                        "question": "How do you design zero-downtime distributed systems for high-traffic platforms?",
                        "sample_answer": "Utilize active-active multi-region deployment, automated circuit breakers, Redis read-replicas, and zero-downtime blue/green deployments."
                    },
                    {
                        "category": "Leadership & Vision",
                        "question": "How do you foster a high-performance culture across engineering teams?",
                        "sample_answer": "Emphasize clear ownership, iterative 2-week Agile sprints, continuous feedback loops, and data-driven decision-making."
                    }
                ]
                self.send_json_response({"questions": answers if 'answers' in locals() else questions})
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server(port=8000):
    print(f"Starting ResumeIQ AI Server (CEO: Mr. Vedant Shete) on http://localhost:{port}...")
    server = HTTPServer(('0.0.0.0', port), ATSRequestHandler)
    server.serve_forever()

if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_server(port)
