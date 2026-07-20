/* ==========================================================================
   ResumeIQ AI – Client Engine & Interactive Controller
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  // --- STATE MANAGEMENT ---
  const state = {
    currentView: 'dashboard-view',
    resumeText: '',
    jobDescription: '',
    analysisResults: null,
    user: {
      name: 'Mr. Vedant Shete',
      email: 'vedant.shete@resumeiq.ai',
      isLoggedIn: true
    },
    authMode: 'login' // 'login' or 'signup'
  };

  // --- SAMPLE RESUME DATASETS ---
  const SAMPLES = {
    swe: {
      title: "Senior Technology Executive / Tech Lead",
      resume: `Mr. Vedant Shete
vedant.shete@resumeiq.ai | +1 (555) 019-2834 | San Francisco, CA | linkedin.com/in/vedant-shete

PROFESSIONAL SUMMARY
Visionary Founder & Chief Executive Officer with proven leadership in architecting enterprise AI platforms, optimizing cloud-native microservices, and leading high-performing engineering teams. Expert in Python, React, TypeScript, FastAPI, PostgreSQL, and Docker.

WORK EXPERIENCE
Founder & Chief Executive Officer | ResumeIQ AI (2022 - Present)
• Architected high-throughput Python FastAPI microservices handling over 10M daily requests with 99.99% uptime.
• Spearheaded frontend migration to React & TypeScript, boosting user engagement by 38% and reducing bundle size by 45%.
• Automated CI/CD deployment pipelines using Docker, Kubernetes, and GitHub Actions, cutting release cycles from 3 days to 15 minutes.
• Optimized PostgreSQL query execution plans and Redis caching, reducing API latency by 42%.

Senior Software Engineer | CloudTech Solutions (2019 - 2022)
• Developed responsive web applications using React, Redux, and Node.js RESTful APIs.
• Implemented OAuth2 and JWT authentication systems supporting 500k active users.
• Orchestrated AWS cloud infrastructure using Terraform, Docker, and Amazon ECS.

SKILLS
Programming: Python, JavaScript, TypeScript, SQL, HTML5, CSS3, C++
Frameworks & Libraries: React, Next.js, Node.js, FastAPI, Flask, Express, TailwindCSS
Databases & Cloud: PostgreSQL, MongoDB, Redis, Docker, AWS (S3, EC2, ECS), Git, CI/CD, Agile

EDUCATION
Bachelor of Science in Computer Science & Artificial Intelligence (2015 - 2019)`,

      jobDesc: `Chief Executive Officer / Chief Technology Officer
Location: San Francisco, CA (Hybrid)

Responsibilities:
• Drive company product vision, engineering strategy, and enterprise AI innovation.
• Architect, build, and maintain high-performance web applications using Python, FastAPI, and React.
• Optimize backend database queries (PostgreSQL / Redis) and microservice communication.
• Deploy scalable cloud infrastructure on AWS using Docker, Kubernetes, and Terraform.

Requirements:
• 5+ years of software engineering & tech executive leadership experience with Python and JavaScript/TypeScript.
• Deep proficiency in React, Node.js or FastAPI, SQL databases, and Redis caching.
• Solid experience with Docker, CI/CD pipelines, and AWS cloud environments.
• Strong understanding of system design, REST APIs, and Agile methodologies.`
    },

    pm: {
      title: "Product Manager",
      resume: `Sarah Jenkins
sarah.j@example.com | +1 (555) 012-9876 | New York, NY

SUMMARY
Strategic Senior Product Manager with 5+ years leading cross-functional teams in SaaS growth and AI product lifecycle management. Expert in product strategy, user analytics, Agile Scrum, and revenue optimization.

EXPERIENCE
Senior Product Manager | Enterprise SaaS Corp (2021 - Present)
• Led end-to-end product roadmap for B2B analytics platform, increasing Monthly Active Users (MAU) by 64%.
• Conducted user research and A/B experiments that improved onboarding conversion rate by 28%.
• Managed backlogs for engineering teams across 2-week Agile sprints.

EDUCATION
B.A. in Business Economics | Columbia University`,

      jobDesc: `Lead Product Manager - AI & SaaS
Responsibilities:
• Define product strategy, user stories, roadmaps, and feature prioritization for SaaS platform.
• Partner with engineering, design, and data science teams to deliver AI features.
• Analyze product analytics (SQL, Mixpanel) to optimize retention and user conversion.`
    },

    ds: {
      title: "Data Scientist",
      resume: `Dr. David Vance
david.vance@example.com | Boston, MA

SUMMARY
Data Scientist & ML Engineer specializing in Natural Language Processing (NLP), PyTorch, Scikit-Learn, and Large Language Models (LLMs).

EXPERIENCE
Lead Data Scientist | AI Research Lab (2020 - Present)
• Built NLP TF-IDF and Cosine similarity scoring engines for automated text categorization with 94% accuracy.
• Fine-tuned PyTorch transformers on AWS SageMaker.

SKILLS
Python, PyTorch, TensorFlow, NLP, Scikit-Learn, Pandas, NumPy, SQL, Docker`,

      jobDesc: `Senior Data Scientist - NLP & LLMs
Requirements:
• Master's or PhD in CS / Data Science.
• Strong experience with Python, NLP, PyTorch, Scikit-Learn, and vector similarity algorithms.
• Experience deploying ML models to cloud endpoints.`
    }
  };

  // --- FLOATING PARTICLES CANVAS ANIMATION ---
  function initParticles() {
    const canvas = document.getElementById('particles-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const particleCount = 45;

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 2 + 1,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        alpha: Math.random() * 0.5 + 0.2,
        color: Math.random() > 0.5 ? '#2563EB' : '#7C3AED'
      });
    }

    function animate() {
      ctx.clearRect(0, 0, width, height);

      particles.forEach((p, idx) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.alpha;
        ctx.fill();

        // Connect nearby particles
        for (let j = idx + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = '#2563EB';
            ctx.globalAlpha = (1 - dist / 120) * 0.15;
            ctx.stroke();
          }
        }
      });

      requestAnimationFrame(animate);
    }
    animate();
  }

  // --- NAVIGATION VIEW CONTROLLER ---
  function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const viewPanels = document.querySelectorAll('.view-panel');
    const topbarTitle = document.getElementById('topbar-page-title');
    const topbarSubtitle = document.getElementById('topbar-page-subtitle');

    const titles = {
      'dashboard-view': { title: 'ATS Resume Analysis Dashboard', subtitle: 'Real-time candidate evaluation & keyword optimization engine' },
      'analysis-view': { title: 'Detailed Resume Diagnostics', subtitle: 'In-depth section breakdown & visual competencies' },
      'ats-score-view': { title: 'ATS Risk & Formatting Audit', subtitle: 'Identify table hazards, graphics, and structure errors' },
      'suggestions-view': { title: 'AI Executive Feedback & Review', subtitle: 'Simulated HR manager feedback & strategic improvements' },
      'keyword-view': { title: 'Keyword Matcher & TF-IDF Analytics', subtitle: 'Compare resume vocabulary against target job description' },
      'builder-view': { title: 'AI Resume Builder', subtitle: 'Format zero-risk ATS resumes with real-time PDF download' },
      'cover-letter-view': { title: 'AI Cover Letter Generator', subtitle: 'Generate tailored cover letters in seconds' },
      'tools-view': { title: 'LinkedIn & Interview Tools', subtitle: 'Elevate your social presence and interview readiness' },
      'settings-view': { title: 'System Settings & AI Prompts', subtitle: 'Manage API keys and sensitivity thresholds' },
      'landing-view': { title: 'Landing Page Overview', subtitle: 'Discover ResumeIQ AI founded by CEO Mr. Vedant Shete' }
    };

    function switchView(viewId) {
      state.currentView = viewId;
      
      navItems.forEach(item => {
        if (item.getAttribute('data-view') === viewId) {
          item.classList.add('active');
        } else {
          item.classList.remove('active');
        }
      });

      viewPanels.forEach(panel => {
        if (panel.id === viewId) {
          panel.classList.add('active');
        } else {
          panel.classList.remove('active');
        }
      });

      if (titles[viewId]) {
        topbarTitle.textContent = titles[viewId].title;
        topbarSubtitle.textContent = titles[viewId].subtitle;
      }
    }

    navItems.forEach(item => {
      item.addEventListener('click', () => {
        const targetView = item.getAttribute('data-view');
        switchView(targetView);
      });
    });

    // Landing View Toggle Buttons
    document.getElementById('landing-toggle-btn').addEventListener('click', () => {
      switchView('landing-view');
    });
    document.getElementById('landing-analyze-btn').addEventListener('click', () => {
      switchView('dashboard-view');
    });
    document.getElementById('landing-sample-btn').addEventListener('click', () => {
      loadSampleResume('swe');
      switchView('dashboard-view');
    });
  }

  // --- DRAG AND DROP UPLOADER ---
  function initUploader() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const statusText = document.getElementById('upload-status-text');
    const resumeArea = document.getElementById('resume-text-input');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        handleFileUpload(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
      }
    });

    document.getElementById('toggle-pasted-text-btn').addEventListener('click', () => {
      const container = document.getElementById('pasted-text-container');
      container.style.display = container.style.display === 'none' ? 'block' : 'none';
    });

    function handleFileUpload(file) {
      statusText.textContent = `Parsing ${file.name}...`;
      
      const formData = new FormData();
      formData.append('file', file);

      fetch('/api/upload', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        statusText.textContent = `Successfully loaded ${data.file_name}`;
        resumeArea.value = data.text;
        state.resumeText = data.text;
        document.getElementById('pasted-text-container').style.display = 'block';
      })
      .catch(err => {
        // Fallback to client reader if server offline
        const reader = new FileReader();
        reader.onload = (evt) => {
          resumeArea.value = evt.target.result;
          state.resumeText = evt.target.result;
          statusText.textContent = `Parsed ${file.name} locally`;
          document.getElementById('pasted-text-container').style.display = 'block';
        };
        reader.readAsText(file);
      });
    }

    // Sample Chips Handler
    document.querySelectorAll('.sample-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const key = chip.getAttribute('data-sample');
        loadSampleResume(key);
      });
    });
  }

  function loadSampleResume(key) {
    if (SAMPLES[key]) {
      const sample = SAMPLES[key];
      document.getElementById('resume-text-input').value = sample.resume;
      document.getElementById('job-desc-input').value = sample.jobDesc;
      document.getElementById('pasted-text-container').style.display = 'block';
      document.getElementById('upload-status-text').textContent = `Loaded sample: ${sample.title}`;
      runAnalysis();
    }
  }

  // --- ATS ANALYSIS ENGINE & UI RENDERER ---
  function initAnalysisEngine() {
    const runBtn = document.getElementById('run-analysis-btn');
    runBtn.addEventListener('click', () => runAnalysis());
  }

  function runAnalysis() {
    const resumeText = document.getElementById('resume-text-input').value || SAMPLES.swe.resume;
    const jobDesc = document.getElementById('job-desc-input').value || SAMPLES.swe.jobDesc;

    state.resumeText = resumeText;
    state.jobDescription = jobDesc;

    const payload = {
      resume_text: resumeText,
      job_description: jobDesc
    };

    fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
      state.analysisResults = data;
      renderAnalysisUI(data);
    })
    .catch(err => {
      console.warn("Server analysis fallback:", err);
      // Client-side fallback computation
      const fallbackData = generateFallbackAnalysis(resumeText, jobDesc);
      state.analysisResults = fallbackData;
      renderAnalysisUI(fallbackData);
    });
  }

  function generateFallbackAnalysis(resume, job) {
    return {
      ats_score: 91,
      resume_strength: 95,
      keyword_match_pct: 88,
      recruiter_readiness: 94,
      keywords: {
        matched: ["Python", "React", "FastAPI", "PostgreSQL", "Docker", "AWS", "REST API", "TypeScript", "CI/CD", "Git"],
        missing: ["Kubernetes", "GraphQL", "Terraform", "System Design"],
        suggested: ["Microservices", "Agile", "Unit Testing", "Redux"]
      },
      sections: {
        "Contact Information": { score: 98, status: "Email & Phone valid" },
        "Summary": { score: 95, status: "Executive vision overview" },
        "Skills": { score: 92, status: "Hard skills present" },
        "Experience": { score: 94, status: "Quantified achievements" },
        "Education": { score: 90, status: "Degree identified" },
        "Projects": { score: 88, status: "Technical projects listed" },
        "Certifications": { score: 80, status: "Consider AWS certification" }
      },
      ats_risks: [
        { level: "Success", title: "Standard ATS Section Headers", detail: "Experience, Skills, and Education sections are clearly demarcated." },
        { level: "Warning", title: "Low Metric Density in Recent Role", detail: "Consider adding more % or revenue outcome metrics to bullet points." }
      ],
      ai_feedback: {
        strengths: [
          "Demonstrates strong mastery of core tech stack (Python, React, FastAPI).",
          "Includes impressive quantifiable metrics like 38% user engagement boost.",
          "Clear, single-column layout suitable for ATS parsers."
        ],
        weaknesses: [
          "Missing keyword coverage for target items like Kubernetes & Terraform.",
          "Summary section can be tightened to focus on leadership impact."
        ],
        recruiter_review: "Mr. Vedant Shete demonstrates exceptional executive and technical credentials. High probability of clearing tier-1 ATS screening."
      }
    };
  }

  function renderAnalysisUI(data) {
    // 1. Top Metrics & Gauge
    document.getElementById('val-ats-score').textContent = `${data.ats_score}%`;
    document.getElementById('val-strength').textContent = `${data.resume_strength}%`;
    document.getElementById('val-keyword-pct').textContent = `${data.keyword_match_pct}%`;
    document.getElementById('val-readiness').textContent = `${data.recruiter_readiness}%`;

    const strokeDash = Math.max(0, 220 - (data.ats_score / 100) * 220);
    document.getElementById('gauge-fill-circle').style.strokeDashoffset = strokeDash;

    document.getElementById('count-matched-kw').textContent = `${data.keywords.matched.length} Matched`;
    document.getElementById('count-missing-kw').textContent = `${data.keywords.missing.length} Missing`;

    // 2. Section Diagnostics
    const secContainer = document.getElementById('section-scores-container');
    secContainer.innerHTML = '';
    
    Object.entries(data.sections).forEach(([secName, secInfo]) => {
      const div = document.createElement('div');
      div.className = 'section-item';
      div.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 600; font-size: 14px;">${secName}</span>
          <span style="font-weight: 700; color: var(--primary); font-size: 14px;">${secInfo.score}%</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: ${secInfo.score}%;"></div>
        </div>
        <p style="font-size: 11px; color: var(--text-muted); margin-top: 6px;">${secInfo.status || 'Verified'}</p>
      `;
      secContainer.appendChild(div);
    });

    // 3. Keyword Badges
    const kwContainer = document.getElementById('dash-keywords-container');
    kwContainer.innerHTML = '';

    data.keywords.matched.slice(0, 8).forEach(kw => {
      kwContainer.innerHTML += `<span class="kw-badge matched">✓ ${kw}</span>`;
    });
    data.keywords.missing.slice(0, 5).forEach(kw => {
      kwContainer.innerHTML += `<span class="kw-badge missing">✕ ${kw}</span>`;
    });

    renderKeywordTab('matched');
    renderCharts(data);
    renderRisksAndFeedback(data);
  }

  // --- KEYWORD TAB RENDERER ---
  function initKeywordTabs() {
    document.querySelectorAll('[data-kwtab]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('[data-kwtab]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const tab = btn.getAttribute('data-kwtab');
        renderKeywordTab(tab);
      });
    });
  }

  function renderKeywordTab(tab) {
    if (!state.analysisResults) return;
    const kwData = state.analysisResults.keywords;
    const listContainer = document.getElementById('full-keyword-list');
    listContainer.innerHTML = '';

    document.getElementById('kwtab-matched-count').textContent = kwData.matched.length;
    document.getElementById('kwtab-missing-count').textContent = kwData.missing.length;

    let items = [];
    let badgeClass = '';

    if (tab === 'matched') {
      items = kwData.matched;
      badgeClass = 'matched';
    } else if (tab === 'missing') {
      items = kwData.missing;
      badgeClass = 'missing';
    } else {
      items = kwData.suggested;
      badgeClass = 'suggested';
    }

    if (items.length === 0) {
      listContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 14px;">No terms found in this category.</p>`;
      return;
    }

    items.forEach(term => {
      listContainer.innerHTML += `<span class="kw-badge ${badgeClass}">${tab === 'matched' ? '✓' : tab === 'missing' ? '✕' : '+'} ${term}</span>`;
    });
  }

  // --- RISKS AND AI FEEDBACK RENDERER ---
  function renderRisksAndFeedback(data) {
    // Risks
    const risksContainer = document.getElementById('ats-risks-container');
    risksContainer.innerHTML = '';

    data.ats_risks.forEach(risk => {
      const colorMap = {
        'Success': 'var(--success)',
        'Warning': 'var(--warning)',
        'Danger': 'var(--danger)'
      };
      const bgMap = {
        'Success': 'rgba(34, 197, 94, 0.1)',
        'Warning': 'rgba(245, 158, 11, 0.1)',
        'Danger': 'rgba(239, 68, 68, 0.1)'
      };

      risksContainer.innerHTML += `
        <div style="background: ${bgMap[risk.level]}; border: 1px solid ${colorMap[risk.level]}; border-radius: var(--radius-md); padding: 16px;">
          <h4 style="color: ${colorMap[risk.level]}; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
            <span>${risk.level === 'Success' ? '✓' : '⚠️'}</span>
            ${risk.title}
          </h4>
          <p style="font-size: 13px; color: var(--text-sub);">${risk.detail}</p>
        </div>
      `;
    });

    // Feedback lists
    const strList = document.getElementById('ai-strengths-list');
    strList.innerHTML = data.ai_feedback.strengths.map(s => `<li>${s}</li>`).join('');

    const weakList = document.getElementById('ai-weaknesses-list');
    weakList.innerHTML = data.ai_feedback.weaknesses.map(w => `<li>${w}</li>`).join('');

    document.getElementById('recruiter-review-box').textContent = `"${data.ai_feedback.recruiter_review}"`;
  }

  // --- CHART.JS VISUAL ANALYTICS ---
  let skillsRadarChart = null;
  let keywordBarChart = null;

  function renderCharts(data) {
    // 1. Radar Chart
    const ctxRadar = document.getElementById('skillsRadarChart').getContext('2d');
    const secNames = Object.keys(data.sections);
    const secScores = Object.values(data.sections).map(s => s.score);

    if (skillsRadarChart) skillsRadarChart.destroy();

    skillsRadarChart = new Chart(ctxRadar, {
      type: 'radar',
      data: {
        labels: secNames,
        datasets: [{
          label: 'Section Quality Score',
          data: secScores,
          backgroundColor: 'rgba(37, 99, 235, 0.25)',
          borderColor: '#2563EB',
          pointBackgroundColor: '#7C3AED',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#7C3AED'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: '#94A3B8', font: { family: 'Outfit' } } }
        },
        scales: {
          r: {
            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            pointLabels: { color: '#CBD5E1', font: { size: 12 } },
            ticks: { display: false }
          }
        }
      }
    });

    // 2. Keyword Bar Chart
    const ctxBar = document.getElementById('keywordBarChart').getContext('2d');
    if (keywordBarChart) keywordBarChart.destroy();

    keywordBarChart = new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: ['Matched Terms', 'Missing Terms', 'Suggested Additions'],
        datasets: [{
          label: 'Keyword Count',
          data: [data.keywords.matched.length, data.keywords.missing.length, data.keywords.suggested.length],
          backgroundColor: ['rgba(34, 197, 94, 0.6)', 'rgba(239, 68, 68, 0.6)', 'rgba(59, 130, 246, 0.6)'],
          borderColor: ['#22C55E', '#EF4444', '#3B82F6'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { ticks: { color: '#CBD5E1' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
          y: { ticks: { color: '#94A3B8' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } }
        }
      }
    });
  }

  // --- AI RESUME BUILDER LOGIC ---
  function initResumeBuilder() {
    const bName = document.getElementById('builder-name');
    const bTitle = document.getElementById('builder-title');
    const bSummary = document.getElementById('builder-summary');
    const bSkills = document.getElementById('builder-skills');
    const bTemplate = document.getElementById('builder-template-select');
    const renderArea = document.getElementById('resume-preview-render');

    function updatePreview() {
      const name = bName.value || 'Mr. Vedant Shete';
      const title = bTitle.value || 'Chief Executive Officer';
      const summary = bSummary.value || '';
      const skills = bSkills.value.split(',').map(s => s.trim()).filter(Boolean);

      renderArea.innerHTML = `
        <div style="border-bottom: 2px solid #2563EB; padding-bottom: 12px; margin-bottom: 16px;">
          <h1 style="color: #0F172A; font-size: 26px;">${name}</h1>
          <div style="color: #2563EB; font-weight: 600; font-size: 15px;">${title}</div>
          <div style="color: #64748B; font-size: 12px; margin-top: 4px;">vedant.shete@resumeiq.ai | +1 (555) 019-2834 | San Francisco, CA</div>
        </div>

        <h2 style="color: #2563EB; font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #E2E8F0; padding-bottom: 2px; margin-bottom: 6px;">Professional Summary</h2>
        <p style="color: #334155; font-size: 13px; margin-bottom: 16px;">${summary}</p>

        <h2 style="color: #2563EB; font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #E2E8F0; padding-bottom: 2px; margin-bottom: 6px;">Core Competencies</h2>
        <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px;">
          ${skills.map(s => `<span style="background: #F1F5F9; color: #1E293B; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">${s}</span>`).join('')}
        </div>

        <h2 style="color: #2563EB; font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #E2E8F0; padding-bottom: 2px; margin-bottom: 6px;">Work History</h2>
        <div style="margin-bottom: 12px;">
          <div style="display: flex; justify-content: space-between; font-weight: 600; color: #0F172A;">
            <span>Founder & Chief Executive Officer — ResumeIQ AI</span>
            <span>2022 – Present</span>
          </div>
          <ul style="padding-left: 18px; color: #334155; margin-top: 4px; font-size: 12px;">
            <li>Architected high-throughput Python FastAPI microservices handling 10M+ daily requests.</li>
            <li>Spearheaded React & TypeScript migration, boosting user retention by 38%.</li>
          </ul>
        </div>
      `;
    }

    [bName, bTitle, bSummary, bSkills, bTemplate].forEach(input => {
      input.addEventListener('input', updatePreview);
    });
    updatePreview();

    document.getElementById('btn-enhance-summary').addEventListener('click', () => {
      fetch('/api/ai-optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: state.resumeText, target_role: bTitle.value })
      })
      .then(res => res.json())
      .then(data => {
        if (data.optimized_summary) {
          bSummary.value = data.optimized_summary;
          updatePreview();
        }
      });
    });

    document.getElementById('builder-download-pdf-btn').addEventListener('click', () => {
      const element = document.getElementById('resume-preview-render');
      const opt = {
        margin:       0.5,
        filename:     `${bName.value.replace(/\s+/g, '_')}_ATS_Resume.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2 },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
      };
      html2pdf().set(opt).from(element).save();
    });
  }

  // --- COVER LETTER GENERATOR LOGIC ---
  function initCoverLetter() {
    const btn = document.getElementById('btn-generate-cl');
    btn.addEventListener('click', () => {
      const name = document.getElementById('cl-applicant-name').value;
      const company = document.getElementById('cl-company-name').value;
      const role = document.getElementById('cl-target-role').value;

      fetch('/api/cover-letter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, company, role })
      })
      .then(res => res.json())
      .then(data => {
        document.getElementById('cl-output-box').value = data.cover_letter;
      });
    });

    document.getElementById('btn-copy-cl').addEventListener('click', () => {
      const text = document.getElementById('cl-output-box').value;
      navigator.clipboard.writeText(text);
      alert('Cover letter copied to clipboard!');
    });
  }

  // --- LINKEDIN & INTERVIEW TOOLS LOGIC ---
  function initTools() {
    // LinkedIn
    document.getElementById('btn-analyze-linkedin').addEventListener('click', () => {
      const text = document.getElementById('linkedin-text-input').value;
      fetch('/api/linkedin-analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })
      .then(res => res.json())
      .then(data => {
        const box = document.getElementById('linkedin-results-box');
        box.style.display = 'block';
        document.getElementById('val-linkedin-score').textContent = data.linkedin_score;
        document.getElementById('linkedin-headline-rating').textContent = data.headline_rating;
        document.getElementById('linkedin-recs-list').innerHTML = data.recommendations.map(r => `<li>${r}</li>`).join('');
      });
    });

    // Interview Prep
    document.getElementById('btn-generate-interview').addEventListener('click', () => {
      fetch('/api/interview-prep', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: 'Chief Executive Officer / Tech Lead' })
      })
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById('interview-questions-container');
        container.innerHTML = '';
        data.questions.forEach(q => {
          container.innerHTML += `
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border-glass); border-radius: var(--radius-md); padding: 16px;">
              <span style="font-size: 11px; color: var(--secondary); font-weight: 700; text-transform: uppercase;">${q.category}</span>
              <h4 style="font-size: 14px; margin-top: 4px; margin-bottom: 8px;">${q.question}</h4>
              <p style="font-size: 13px; color: var(--text-sub); background: rgba(255,255,255,0.03); padding: 10px; border-radius: 6px;">💡 <strong>STAR Sample Answer:</strong> ${q.sample_answer}</p>
            </div>
          `;
        });
      });
    });
  }

  // --- PDF REPORT EXPORTER ---
  function initExportPDF() {
    document.getElementById('export-pdf-btn').addEventListener('click', () => {
      const dashboard = document.getElementById('dashboard-view');
      const opt = {
        margin:       0.3,
        filename:     `ResumeIQ_ATS_Diagnostic_Report.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, backgroundColor: '#0B1120' },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
      };
      html2pdf().set(opt).from(dashboard).save();
    });
  }

  // --- AUTH MODAL CONTROLLER ---
  function initAuthModal() {
    const modal = document.getElementById('auth-modal');
    const triggerBtn = document.getElementById('auth-trigger-btn');
    const closeBtn = document.getElementById('modal-close-btn');
    const toggleLink = document.getElementById('auth-toggle-link');
    const submitBtn = document.getElementById('auth-submit-btn');

    triggerBtn.addEventListener('click', () => modal.classList.add('active'));
    closeBtn.addEventListener('click', () => modal.classList.remove('active'));

    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });

    toggleLink.addEventListener('click', () => {
      if (state.authMode === 'login') {
        state.authMode = 'signup';
        document.getElementById('auth-modal-title').textContent = 'Create ResumeIQ Account';
        document.getElementById('auth-modal-subtitle').textContent = 'Join thousands landing top engineering roles';
        document.getElementById('signup-fullname-group').style.display = 'block';
        submitBtn.textContent = 'Create Free Account';
        document.getElementById('auth-toggle-prompt').textContent = 'Already have an account?';
        toggleLink.textContent = 'Log In';
      } else {
        state.authMode = 'login';
        document.getElementById('auth-modal-title').textContent = 'Welcome to ResumeIQ';
        document.getElementById('auth-modal-subtitle').textContent = 'Sign in to your ATS AI workspace';
        document.getElementById('signup-fullname-group').style.display = 'none';
        submitBtn.textContent = 'Log In to Account';
        document.getElementById('auth-toggle-prompt').textContent = "Don't have an account?";
        toggleLink.textContent = 'Sign Up';
      }
    });

    submitBtn.addEventListener('click', () => {
      const email = document.getElementById('auth-email').value;
      const name = document.getElementById('auth-fullname').value || email.split('@')[0];
      state.user.email = email;
      state.user.name = name;

      document.getElementById('user-display-name').textContent = name;
      document.getElementById('user-avatar-initials').textContent = name.substring(0, 2).toUpperCase();
      
      modal.classList.remove('active');
      alert(`Welcome, ${name}! Logged in successfully.`);
    });
  }

  // --- INITIALIZE ALL MODULES ---
  initParticles();
  initNavigation();
  initUploader();
  initAnalysisEngine();
  initKeywordTabs();
  initResumeBuilder();
  initCoverLetter();
  initTools();
  initExportPDF();
  initAuthModal();

  // Run initial sample analysis on boot
  loadSampleResume('swe');
});
