import os
import json
import uuid
import logging
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, g, Response, jsonify
)
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from database.db import get_db_connection, init_db
from services.pdf_parser import extract_text_from_pdf, PDFParsingError
from services.resume_analyzer import analyze_resume_quality
from services.job_matcher import calculate_job_match
from services.career_recommender import recommend_career_roles
from services.skill_gap import analyze_skill_gap
from services.roadmap_generator import generate_learning_roadmap
from services.resume_builder import (
    create_resume_version, duplicate_resume_version, get_user_resume_versions, parse_resume_version_data
)
from services.pdf_exporter import generate_resume_pdf_bytes
from services.ai_rewriter import improve_resume_content
from services.optimizer import optimize_resume_for_job
from services.comparator import compare_resume_versions
from services.interview_prep import generate_interview_prep, evaluate_candidate_answer
from services.gemini_service import (
    is_gemini_available, rewrite_bullet_point_ai, evaluate_interview_answer_ai,
    generate_cover_letter_ai, optimize_resume_for_jd_ai, chat_career_coach_ai
)
from data.job_roles import JOB_ROLES

# Configure Application Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

app = Flask(__name__)
app.config.from_object(Config)

# Register custom Jinja2 type tests
app.jinja_env.tests['list'] = lambda v: isinstance(v, list)
app.jinja_env.tests['dict'] = lambda v: isinstance(v, dict)

@app.context_processor
def inject_gemini_status():
    return dict(gemini_active=is_gemini_available())

# Security Extensions Setup
csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=app.config['RATELIMIT_STORAGE_URI']
)

# Initialize Database Schema on app startup
with app.app_context():
    init_db()

# --- AUTHENTICATION HELPERS ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# --- SYSTEM & HEALTH CHECK ROUTES ---

@app.route('/health')
@limiter.exempt
def health_check():
    """Health check endpoint for monitoring."""
    db_status = "ok"
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1;")
        conn.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "version": "2.0.0"
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html')

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')

        conn = get_db_connection()
        existing_user = conn.execute("SELECT id FROM users WHERE email = ?;", (email,)).fetchone()
        if existing_user:
            conn.close()
            flash("An account with this email address already exists.", "danger")
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?);", (name, email, password_hash))
        user_id = cursor.lastrowid

        # Create blank profile
        cursor.execute("INSERT INTO profiles (user_id) VALUES (?);", (user_id,))
        conn.commit()
        conn.close()

        logging.info(f"New user registered: {email}")
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?;", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            logging.info(f"User logged in: {email}")
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            logging.warning(f"Failed login attempt for: {email}")
            flash("Invalid email or password.", "danger")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?;", (user_id,)).fetchone()
    profile = conn.execute("SELECT * FROM profiles WHERE user_id = ?;", (user_id,)).fetchone()
    history = conn.execute("SELECT * FROM analyses WHERE user_id = ? ORDER BY id DESC;", (user_id,)).fetchall()
    versions = get_user_resume_versions(user_id)
    conn.close()

    latest_analysis = history[0] if history else None

    return render_template('dashboard.html', user=user, profile=profile, latest_analysis=latest_analysis, history=history, versions=versions)

# --- RESUME UPLOAD & ANALYSIS ---

@app.route('/upload', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def upload():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash("No file was uploaded.", "danger")
            return redirect(request.url)
        
        file = request.files['resume']
        if file.filename == '':
            flash("No file selected.", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)

            try:
                raw_text = extract_text_from_pdf(save_path)
            except PDFParsingError as e:
                logging.error(f"PDF Extraction Error: {str(e)}")
                flash(f"PDF Extraction Error: {str(e)}", "danger")
                return redirect(request.url)

            analysis_result = analyze_resume_quality(raw_text)
            career_data = recommend_career_roles(raw_text)
            top_role = career_data["top_role"]

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analyses (user_id, resume_filename, resume_score, recommended_role, analysis_json)
                VALUES (?, ?, ?, ?, ?);
            """, (
                session['user_id'],
                original_filename,
                analysis_result["overall_score"],
                top_role,
                json.dumps({
                    "raw_text": raw_text,
                    "analysis_result": analysis_result,
                    "career_data": career_data
                })
            ))
            analysis_id = cursor.lastrowid
            conn.commit()
            conn.close()

            flash("Resume analyzed successfully!", "success")
            return redirect(url_for('analysis_detail', analysis_id=analysis_id))
        else:
            flash("Invalid file format. Please upload a PDF file.", "danger")
            return redirect(request.url)

    return render_template('upload.html')

@app.route('/analysis/<int:analysis_id>')
@login_required
def analysis_detail(analysis_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM analyses WHERE id = ?;", (analysis_id,)).fetchone()
    conn.close()

    if not row:
        return render_template('404.html'), 404
    if row['user_id'] != session['user_id']:
        return render_template('403.html'), 403

    parsed_json = json.loads(row['analysis_json'])
    return render_template('analysis.html', analysis=row, analysis_data=parsed_json["analysis_result"])

@app.route('/job-matcher', methods=['GET', 'POST'])
@login_required
@limiter.limit("15 per minute")
def job_matcher():
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Fetch all user resume sources (analyses & builder versions)
    analyses = conn.execute("SELECT * FROM analyses WHERE user_id = ? ORDER BY id DESC;", (user_id,)).fetchall()
    versions = conn.execute("SELECT * FROM resume_versions WHERE user_id = ? ORDER BY id DESC;", (user_id,)).fetchall()
    conn.close()

    # Pre-defined Sample Job Descriptions for instant testing
    sample_jds = {
        "python_backend": {
            "title": "Python Backend Developer Intern",
            "company": "TechCorp Solutions",
            "text": "We are seeking a Python Backend Developer proficient in Python, Flask, REST API, SQL, PostgreSQL, Git, Docker, and AWS. Responsibilities include building scalable REST endpoints, database schema design, and writing unit tests."
        },
        "aiml_engineer": {
            "title": "AI/ML Engineer Intern",
            "company": "AI Innovations Lab",
            "text": "Looking for an AI/ML Engineer skilled in Python, Machine Learning, Deep Learning, PyTorch, TensorFlow, Scikit-Learn, Pandas, NumPy, NLP, and Computer Vision. Candidate will design predictive ML pipelines and train neural network models."
        },
        "software_engineer": {
            "title": "Software Engineer Intern",
            "company": "Global Software Inc.",
            "text": "Looking for a Software Engineer proficient in Data Structures, Algorithms, C++, Java, Python, SQL, DBMS, Operating Systems, Computer Networks, and OOP principles. Ideal candidates have strong problem-solving skills."
        }
    }

    if request.method == 'POST':
        job_title = request.form.get('job_title', '').strip()
        company_name = request.form.get('company_name', '').strip()
        job_description = request.form.get('job_description', '').strip()
        resume_source = request.form.get('resume_source', 'latest')

        if not job_title or not job_description:
            flash("Job title and job description are required.", "danger")
            return render_template('job_matcher.html', analyses=analyses, versions=versions, sample_jds=sample_jds)

        # Determine Resume Text Source
        raw_resume_text = ""
        analysis_id_to_update = None

        if resume_source.startswith("version_"):
            v_id = int(resume_source.replace("version_", ""))
            conn = get_db_connection()
            v_row = conn.execute("SELECT * FROM resume_versions WHERE id = ? AND user_id = ?;", (v_id, user_id)).fetchone()
            conn.close()
            if v_row:
                parsed_v = parse_resume_version_data(v_row)
                raw_resume_text = f"{parsed_v['summary']}\n"
                for cat, sk in parsed_v.get('skills', {}).items():
                    raw_resume_text += f"{cat}: {', '.join(sk) if isinstance(sk, list) else sk}\n"
                for p in parsed_v.get('projects', []):
                    raw_resume_text += f"{p.get('title', '')} {p.get('tech_stack', '')} {p.get('description', '')}\n"
                for e in parsed_v.get('experience', []):
                    raw_resume_text += f"{e.get('title', '')} {e.get('company', '')} {e.get('description', '')}\n"

        if not raw_resume_text and analyses:
            latest_a = analyses[0]
            analysis_id_to_update = latest_a['id']
            parsed_json = json.loads(latest_a['analysis_json'])
            raw_resume_text = parsed_json["raw_text"]

        # Default fallback sample resume if user has neither uploaded PDF nor created version
        if not raw_resume_text:
            raw_resume_text = """
            Sandeep Gaud - Python Developer
            Email: sandeep@example.com | Phone: +91 9876543210
            EDUCATION: B.Tech in Computer Science and Engineering (AI) - 2026
            TECHNICAL SKILLS:
            Programming: Python, Java, C++, SQL
            Web & Frameworks: Flask, REST API, HTML5, CSS3, Jinja2
            Database: SQLite, MySQL, PostgreSQL
            Tools: Git, GitHub, Linux, Postman
            PROJECTS:
            ResumeAI - AI-Powered Resume Analyzer & Job Matcher
            - Built web application using Flask, pypdf, and scikit-learn.
            - Implemented TF-IDF and Cosine Similarity matching algorithms.
            """

        match_result = calculate_job_match(raw_resume_text, job_description, job_title, company_name)

        if analysis_id_to_update:
            conn = get_db_connection()
            try:
                conn.execute("""
                    UPDATE analyses
                    SET job_title = ?, company_name = ?, job_match_score = ?
                    WHERE id = ?;
                """, (job_title, company_name, match_result["overall_match_score"], analysis_id_to_update))
            except Exception:
                conn.execute("""
                    UPDATE analyses
                    SET job_title = ?, job_match_score = ?
                    WHERE id = ?;
                """, (job_title, match_result["overall_match_score"], analysis_id_to_update))
            conn.commit()
            conn.close()

        return render_template('job_result.html', match_result=match_result, analysis_id=analysis_id_to_update or 1)

    return render_template('job_matcher.html', analyses=analyses, versions=versions, sample_jds=sample_jds)

# --- RESUME BUILDER & MULTI-VERSION ROUTES ---

@app.route('/resumes')
@login_required
def builder_list():
    versions = get_user_resume_versions(session['user_id'])
    return render_template('builder_list.html', versions=versions)

@app.route('/resumes/new', methods=['GET', 'POST'])
@login_required
def builder_new():
    roles_list = list(JOB_ROLES.keys())
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?;", (session['user_id'],)).fetchone()
    conn.close()

    if request.method == 'POST':
        version_name = request.form.get('version_name', '').strip()
        target_role = request.form.get('target_role', 'Software Engineer')
        template_name = request.form.get('template_name', 'ats_classic')

        if not version_name:
            flash("Version name is required.", "danger")
            return render_template('builder_form.html', version=None, parsed={}, roles_list=roles_list, user=user)

        certs = []
        c1_name = request.form.get('cert1_name', '').strip()
        c1_date = request.form.get('cert1_date', '').strip()
        if c1_name: certs.append({"name": c1_name, "date": c1_date})
        c2_name = request.form.get('cert2_name', '').strip()
        c2_date = request.form.get('cert2_date', '').strip()
        if c2_name: certs.append({"name": c2_name, "date": c2_date})

        achievements_raw = request.form.get('achievements', '').strip()
        achievements = [a.strip() for a in achievements_raw.split('\n') if a.strip()]

        initial_data = {
            "summary": request.form.get('summary', '').strip(),
            "contact_info": {
                "name": request.form.get('contact_name', '').strip(),
                "email": request.form.get('contact_email', '').strip(),
                "phone": request.form.get('contact_phone', '').strip(),
                "location": request.form.get('contact_location', '').strip(),
                "github": request.form.get('contact_github', '').strip(),
                "linkedin": request.form.get('contact_linkedin', '').strip(),
                "portfolio": request.form.get('contact_portfolio', '').strip(),
            },
            "skills": {
                "Languages": [s.strip() for s in request.form.get('skill_languages', '').split(',') if s.strip()],
                "Frontend Development": [s.strip() for s in request.form.get('skill_frontend', '').split(',') if s.strip()],
                "Backend Frameworks": [s.strip() for s in request.form.get('skill_backend', '').split(',') if s.strip()],
                "Databases & Cloud": [s.strip() for s in request.form.get('skill_database', '').split(',') if s.strip()],
                "Developer Tools": [s.strip() for s in request.form.get('skill_tools', '').split(',') if s.strip()],
                "Core Computer Science": [s.strip() for s in request.form.get('skill_cs', '').split(',') if s.strip()],
            },
            "projects": [
                {
                    "title": request.form.get('proj1_title', '').strip(),
                    "tech_stack": request.form.get('proj1_tech', '').strip(),
                    "description": request.form.get('proj1_desc', '').strip(),
                    "github_url": request.form.get('proj1_github', '').strip(),
                    "live_demo_url": request.form.get('proj1_demo', '').strip()
                },
                {
                    "title": request.form.get('proj2_title', '').strip(),
                    "tech_stack": request.form.get('proj2_tech', '').strip(),
                    "description": request.form.get('proj2_desc', '').strip(),
                    "github_url": request.form.get('proj2_github', '').strip(),
                    "live_demo_url": request.form.get('proj2_demo', '').strip()
                }
            ],
            "experience": [
                {
                    "title": request.form.get('exp1_title', '').strip(),
                    "company": request.form.get('exp1_company', '').strip(),
                    "dates": request.form.get('exp1_dates', '').strip(),
                    "description": request.form.get('exp1_desc', '').strip()
                }
            ],
            "education": [
                {
                    "degree": request.form.get('edu1_degree', request.form.get('edu_degree', '')).strip(),
                    "institution": request.form.get('edu1_inst', request.form.get('edu_inst', '')).strip(),
                    "year": request.form.get('edu1_year', request.form.get('edu_year', '')).strip()
                },
                {
                    "degree": request.form.get('edu2_degree', '').strip(),
                    "institution": request.form.get('edu2_inst', '').strip(),
                    "year": request.form.get('edu2_year', '').strip()
                }
            ],
            "certifications": certs,
            "achievements": achievements,
            "template_name": template_name
        }

        # Save Certifications & Achievements in certifications_json column
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO resume_versions (
                user_id, version_name, target_role, summary,
                contact_info_json, education_json, skills_json,
                experience_json, projects_json, certifications_json, template_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            session['user_id'],
            version_name,
            target_role,
            initial_data["summary"],
            json.dumps(initial_data["contact_info"]),
            json.dumps(initial_data["education"]),
            json.dumps(initial_data["skills"]),
            json.dumps(initial_data["experience"]),
            json.dumps(initial_data["projects"]),
            json.dumps({"certifications": certs, "achievements": achievements}),
            template_name
        ))
        version_id = cursor.lastrowid
        conn.commit()
        conn.close()

        flash("New resume version created successfully!", "success")
        return redirect(url_for('builder_preview', version_id=version_id))

    return render_template('builder_form.html', version=None, parsed={}, roles_list=roles_list, user=user)

@app.route('/resumes/<int:version_id>/edit', methods=['GET', 'POST'])
@login_required
def builder_edit(version_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM resume_versions WHERE id = ? AND user_id = ?;", (version_id, session['user_id'])).fetchone()
    conn.close()

    if not row:
        return render_template('404.html'), 404

    roles_list = list(JOB_ROLES.keys())
    parsed = parse_resume_version_data(row)

    if request.method == 'POST':
        version_name = request.form.get('version_name', '').strip()
        target_role = request.form.get('target_role', 'Software Engineer')
        template_name = request.form.get('template_name', 'ats_classic')

        updated_skills = {
            "Languages": [s.strip() for s in request.form.get('skill_languages', '').split(',') if s.strip()],
            "Frontend Development": [s.strip() for s in request.form.get('skill_frontend', '').split(',') if s.strip()],
            "Backend Frameworks": [s.strip() for s in request.form.get('skill_backend', '').split(',') if s.strip()],
            "Databases & Cloud": [s.strip() for s in request.form.get('skill_database', '').split(',') if s.strip()],
            "Developer Tools": [s.strip() for s in request.form.get('skill_tools', '').split(',') if s.strip()],
            "Core Computer Science": [s.strip() for s in request.form.get('skill_cs', '').split(',') if s.strip()],
        }

        updated_projects = [
            {
                "title": request.form.get('proj1_title', '').strip(),
                "tech_stack": request.form.get('proj1_tech', '').strip(),
                "description": request.form.get('proj1_desc', '').strip(),
                "github_url": request.form.get('proj1_github', '').strip(),
                "live_demo_url": request.form.get('proj1_demo', '').strip()
            },
            {
                "title": request.form.get('proj2_title', '').strip(),
                "tech_stack": request.form.get('proj2_tech', '').strip(),
                "description": request.form.get('proj2_desc', '').strip(),
                "github_url": request.form.get('proj2_github', '').strip(),
                "live_demo_url": request.form.get('proj2_demo', '').strip()
            }
        ]

        updated_experience = [
            {
                "title": request.form.get('exp1_title', '').strip(),
                "company": request.form.get('exp1_company', '').strip(),
                "dates": request.form.get('exp1_dates', '').strip(),
                "description": request.form.get('exp1_desc', '').strip()
            }
        ]

        updated_education = [
            {
                "degree": request.form.get('edu1_degree', request.form.get('edu_degree', '')).strip(),
                "institution": request.form.get('edu1_inst', request.form.get('edu_inst', '')).strip(),
                "year": request.form.get('edu1_year', request.form.get('edu_year', '')).strip()
            },
            {
                "degree": request.form.get('edu2_degree', '').strip(),
                "institution": request.form.get('edu2_inst', '').strip(),
                "year": request.form.get('edu2_year', '').strip()
            }
        ]

        updated_contact = {
            "name": request.form.get('contact_name', '').strip(),
            "email": request.form.get('contact_email', '').strip(),
            "phone": request.form.get('contact_phone', '').strip(),
            "location": request.form.get('contact_location', '').strip(),
            "github": request.form.get('contact_github', '').strip(),
            "linkedin": request.form.get('contact_linkedin', '').strip(),
            "portfolio": request.form.get('contact_portfolio', '').strip(),
        }

        certs = []
        c1_name = request.form.get('cert1_name', '').strip()
        c1_date = request.form.get('cert1_date', '').strip()
        if c1_name: certs.append({"name": c1_name, "date": c1_date})
        c2_name = request.form.get('cert2_name', '').strip()
        c2_date = request.form.get('cert2_date', '').strip()
        if c2_name: certs.append({"name": c2_name, "date": c2_date})

        achievements_raw = request.form.get('achievements', '').strip()
        achievements = [a.strip() for a in achievements_raw.split('\n') if a.strip()]

        conn = get_db_connection()
        conn.execute("""
            UPDATE resume_versions
            SET version_name = ?, target_role = ?, summary = ?,
                contact_info_json = ?, education_json = ?, skills_json = ?,
                experience_json = ?, projects_json = ?, certifications_json = ?, template_name = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?;
        """, (
            version_name, target_role, request.form.get('summary', '').strip(),
            json.dumps(updated_contact), json.dumps(updated_education), json.dumps(updated_skills),
            json.dumps(updated_experience), json.dumps(updated_projects),
            json.dumps({"certifications": certs, "achievements": achievements}),
            template_name, version_id, session['user_id']
        ))
        conn.commit()
        conn.close()
        flash("Resume version updated!", "success")
        return redirect(url_for('builder_preview', version_id=version_id))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?;", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('builder_form.html', version=row, parsed=parsed, roles_list=roles_list, user=user)

@app.route('/resumes/<int:version_id>/preview')
@login_required
def builder_preview(version_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM resume_versions WHERE id = ? AND user_id = ?;", (version_id, session['user_id'])).fetchone()
    conn.close()

    if not row:
        return render_template('404.html'), 404

    parsed = parse_resume_version_data(row)
    user = {"name": session.get("user_name", "Candidate")}
    return render_template('builder_preview.html', version=row, parsed=parsed, user=user)

@app.route('/resumes/<int:version_id>/export-pdf')
@login_required
def builder_export_pdf(version_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM resume_versions WHERE id = ? AND user_id = ?;", (version_id, session['user_id'])).fetchone()
    conn.close()

    if not row:
        return render_template('404.html'), 404

    parsed = parse_resume_version_data(row)
    pdf_bytes = generate_resume_pdf_bytes(parsed)

    filename = f"{secure_filename(row['version_name'])}.pdf"
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )

@app.route('/resumes/<int:version_id>/duplicate', methods=['POST'])
@login_required
def builder_duplicate(version_id):
    try:
        new_name = f"Copy of Version {version_id}"
        new_id = duplicate_resume_version(session['user_id'], version_id, new_name)
        flash("Resume version duplicated successfully!", "success")
        return redirect(url_for('builder_edit', version_id=new_id))
    except Exception as e:
        flash(f"Duplicate Error: {str(e)}", "danger")
        return redirect(url_for('builder_list'))

@app.route('/resumes/<int:version_id>/optimize', methods=['GET', 'POST'])
@login_required
def optimize_view(version_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM resume_versions WHERE id = ? AND user_id = ?;", (version_id, session['user_id'])).fetchone()
    conn.close()

    if not row:
        return render_template('404.html'), 404

    if request.method == 'POST':
        job_title = request.form.get('job_title', '').strip()
        company_name = request.form.get('company_name', '').strip()
        job_description = request.form.get('job_description', '').strip()

        if not job_title or not job_description or not company_name:
            flash("All fields are required for optimization.", "danger")
            return render_template('optimize.html', version=row)

        opt_result = optimize_resume_for_job(session['user_id'], version_id, job_title, company_name, job_description)
        flash(f"Created new optimized version: '{opt_result['new_version_name']}'!", "success")
        return redirect(url_for('builder_preview', version_id=opt_result['new_version_id']))

    return render_template('optimize.html', version=row)

@app.route('/resumes/compare')
@login_required
def compare_view():
    user_id = session['user_id']
    versions = get_user_resume_versions(user_id)
    
    version_a_id = request.args.get('version_a', type=int)
    version_b_id = request.args.get('version_b', type=int)

    compare_result = None
    if version_a_id and version_b_id:
        try:
            compare_result = compare_resume_versions(user_id, version_a_id, version_b_id)
        except Exception as e:
            flash(f"Comparison error: {str(e)}", "danger")

    return render_template('compare.html', versions=versions, version_a_id=version_a_id, version_b_id=version_b_id, compare_result=compare_result)

# --- AI REWRITER & INTERVIEW PREP & GEMINI SERVICES ---

@app.route('/rewriter', methods=['GET', 'POST'])
@login_required
@limiter.limit("15 per minute")
def rewriter():
    rewrite_result = None
    gemini_rewrites = []
    original_text = ""
    content_type = "Project Description"

    if request.method == 'POST':
        content_type = request.form.get('content_type', 'Project Description')
        original_text = request.form.get('content_text', '').strip()

        if not original_text:
            flash("Original text cannot be empty.", "danger")
        else:
            rewrite_result = improve_resume_content(original_text, content_type)
            if is_gemini_available():
                gemini_rewrites = rewrite_bullet_point_ai(original_text, content_type)

    return render_template(
        'rewriter.html',
        rewrite_result=rewrite_result,
        gemini_rewrites=gemini_rewrites,
        original_text=original_text,
        content_type=content_type
    )

@app.route('/interview-prep', methods=['GET', 'POST'])
@login_required
@limiter.limit("20 per minute")
def interview_prep_view():
    target_role = request.args.get('target_role', request.form.get('target_role', 'Python Developer'))
    roles_list = list(JOB_ROLES.keys())

    eval_result = None
    selected_question = request.form.get('question', '')
    user_answer = request.form.get('user_answer', '').strip()

    if request.method == 'POST' and selected_question and user_answer:
        model_ans = request.form.get('model_answer', '')
        key_terms_str = request.form.get('key_terms', '')
        key_terms = [t.strip() for t in key_terms_str.split(',') if t.strip()]

        if is_gemini_available():
            ai_eval = evaluate_interview_answer_ai(selected_question, model_ans, user_answer)
            if ai_eval and 'score' in ai_eval:
                eval_result = {
                    'score': ai_eval.get('score', 85),
                    'strengths': [ai_eval.get('strengths', '')],
                    'missing_keywords': ai_eval.get('missing_terms', []),
                    'model_answer': model_ans,
                    'ai_coaching': ai_eval.get('feedback', ''),
                    'is_gemini': True
                }

        if not eval_result:
            eval_result = evaluate_candidate_answer(selected_question, user_answer, target_role, model_ans, key_terms)
            eval_result['is_gemini'] = False

        flash("AI Evaluation complete! Check your Score & Feedback below.", "success")

    prep_data = generate_interview_prep(target_role)
    return render_template(
        'interview.html',
        target_role=target_role,
        roles_list=roles_list,
        prep_data=prep_data,
        eval_result=eval_result,
        selected_question=selected_question,
        user_answer=user_answer
    )

@app.route('/job-matcher/cover-letter', methods=['POST'])
@login_required
def generate_cover_letter_route():
    resume_text = request.form.get('resume_text', '').strip()
    job_description = request.form.get('job_description', '').strip()
    target_role = request.form.get('target_role', 'Software Engineer')

    if not is_gemini_available():
        return jsonify({'success': False, 'error': 'Gemini API Key is missing in .env file.'})

    conn = get_db_connection()
    user = conn.execute("SELECT name FROM users WHERE id = ?;", (session['user_id'],)).fetchone()
    conn.close()
    user_name = user['name'] if user else 'Candidate'

    letter = generate_cover_letter_ai(resume_text, job_description, candidate_name=user_name, target_role=target_role)
    if letter:
        return jsonify({'success': True, 'cover_letter': letter})
    return jsonify({'success': False, 'error': 'Failed to generate cover letter. Please verify your GEMINI_API_KEY.'})

@app.route('/api/chat', methods=['POST'])
@login_required
@csrf.exempt
def api_chat_route():
    data = request.get_json(silent=True) or {}
    user_msg = data.get('message', '').strip()
    history = data.get('history', [])

    if not user_msg:
        return jsonify({'response': 'Please enter a valid question!'})

    resp_text = chat_career_coach_ai(user_msg, history)
    return jsonify({'response': resp_text, 'gemini_active': is_gemini_available()})

# --- CAREER & ROADMAP ROUTES ---

@app.route('/career-recommendation/<int:analysis_id>')
@login_required
def career_recommendation(analysis_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM analyses WHERE id = ?;", (analysis_id,)).fetchone()
    conn.close()

    if not row:
        return render_template('404.html'), 404
    if row['user_id'] != session['user_id']:
        return render_template('403.html'), 403

    parsed_json = json.loads(row['analysis_json'])
    career_data = parsed_json.get("career_data")
    if not career_data:
        career_data = recommend_career_roles(parsed_json["raw_text"])

    return render_template('career.html', analysis_id=analysis_id, career_data=career_data)

@app.route('/skill-gap/<int:analysis_id>')
@login_required
def skill_gap(analysis_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM analyses WHERE id = ?;", (analysis_id,)).fetchone()
    conn.close()

    if not row:
        return render_template('404.html'), 404
    if row['user_id'] != session['user_id']:
        return render_template('403.html'), 403

    target_role = request.args.get('target_role', row['recommended_role'] or "Python Developer")
    parsed_json = json.loads(row['analysis_json'])
    raw_text = parsed_json["raw_text"]

    gap_data = analyze_skill_gap(raw_text, target_role)
    roles_list = list(JOB_ROLES.keys())

    return render_template('skill_gap.html', analysis_id=analysis_id, gap_data=gap_data, roles_list=roles_list)

@app.route('/roadmap/<int:analysis_id>')
@login_required
def roadmap(analysis_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM analyses WHERE id = ?;", (analysis_id,)).fetchone()
    conn.close()

    if not row:
        return render_template('404.html'), 404
    if row['user_id'] != session['user_id']:
        return render_template('403.html'), 403

    target_role = request.args.get('target_role', row['recommended_role'] or "Python Developer")
    parsed_json = json.loads(row['analysis_json'])
    raw_text = parsed_json["raw_text"]

    roadmap_data = generate_learning_roadmap(raw_text, target_role)
    return render_template('roadmap.html', analysis_id=analysis_id, roadmap=roadmap_data)

@app.route('/history')
@login_required
def history():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM analyses WHERE user_id = ? ORDER BY id DESC;", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('history.html', history=rows)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?;", (user_id,)).fetchone()
    roles_list = list(JOB_ROLES.keys())

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        target_role = request.form.get('target_role', 'Software Engineer').strip()
        college = request.form.get('college', '').strip()
        degree = request.form.get('degree', '').strip()
        branch = request.form.get('branch', '').strip()
        grad_year = request.form.get('graduation_year', '').strip()
        github = request.form.get('github_url', '').strip()
        linkedin = request.form.get('linkedin_url', '').strip()

        # URL normalization
        if github and not (github.startswith("http://") or github.startswith("https://")):
            github = f"https://{github}"
        if linkedin and not (linkedin.startswith("http://") or linkedin.startswith("https://")):
            linkedin = f"https://{linkedin}"

        grad_year_val = int(grad_year) if grad_year.isdigit() else None

        # Update User Name
        if name:
            conn.execute("UPDATE users SET name = ? WHERE id = ?;", (name, user_id))
            session['user_name'] = name

        # Password Change Logic
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_new_password = request.form.get('confirm_new_password', '')

        if current_password:
            if not check_password_hash(user['password_hash'], current_password):
                flash("Current password is incorrect.", "danger")
            elif not new_password or len(new_password) < 6:
                flash("New password must be at least 6 characters long.", "danger")
            elif new_password != confirm_new_password:
                flash("New passwords do not match.", "danger")
            else:
                new_hash = generate_password_hash(new_password)
                conn.execute("UPDATE users SET password_hash = ? WHERE id = ?;", (new_hash, user_id))
                flash("Password updated successfully!", "success")

        # Safe Profile Upsert
        profile_exists = conn.execute("SELECT user_id FROM profiles WHERE user_id = ?;", (user_id,)).fetchone()
        
        # Check if phone and target_role columns exist (or handle fallback gracefully)
        try:
            if profile_exists:
                conn.execute("""
                    UPDATE profiles
                    SET college = ?, degree = ?, branch = ?, graduation_year = ?, github_url = ?, linkedin_url = ?, phone = ?, target_role = ?
                    WHERE user_id = ?;
                """, (college, degree, branch, grad_year_val, github, linkedin, phone, target_role, user_id))
            else:
                conn.execute("""
                    INSERT INTO profiles (user_id, college, degree, branch, graduation_year, github_url, linkedin_url, phone, target_role)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (user_id, college, degree, branch, grad_year_val, github, linkedin, phone, target_role))
        except Exception:
            # Fallback if old SQLite schema without phone/target_role
            if profile_exists:
                conn.execute("""
                    UPDATE profiles
                    SET college = ?, degree = ?, branch = ?, graduation_year = ?, github_url = ?, linkedin_url = ?
                    WHERE user_id = ?;
                """, (college, degree, branch, grad_year_val, github, linkedin, user_id))
            else:
                conn.execute("""
                    INSERT INTO profiles (user_id, college, degree, branch, graduation_year, github_url, linkedin_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (user_id, college, degree, branch, grad_year_val, github, linkedin))

        conn.commit()
        flash("Profile information updated successfully!", "success")

    user = conn.execute("SELECT * FROM users WHERE id = ?;", (user_id,)).fetchone()
    profile_data = conn.execute("SELECT * FROM profiles WHERE user_id = ?;", (user_id,)).fetchone()
    
    # Calculate User Stats
    total_analyses = conn.execute("SELECT COUNT(*) FROM analyses WHERE user_id = ?;", (user_id,)).fetchone()[0]
    total_versions = conn.execute("SELECT COUNT(*) FROM resume_versions WHERE user_id = ?;", (user_id,)).fetchone()[0]
    conn.close()

    stats = {
        "total_analyses": total_analyses,
        "total_versions": total_versions,
        "joined_date": user['created_at'][:10] if user and user['created_at'] else "2026-08-28"
    }

    return render_template('profile.html', user=user, profile=profile_data, stats=stats, roles_list=roles_list)

@app.route('/about')
def about():
    return render_template('about.html')

# --- ERROR HANDLERS ---

@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(413)
def request_entity_too_large(e):
    return render_template('413.html'), 413

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('429.html'), 429

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Internal Server Error: {str(e)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
