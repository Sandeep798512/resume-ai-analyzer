import os
import json
import logging
import urllib.request
import urllib.error
from config import Config

logger = logging.getLogger(__name__)

def get_gemini_api_key() -> str:
    """Returns configured GEMINI_API_KEY from environment or Config."""
    key = os.environ.get('GEMINI_API_KEY', '').strip() or getattr(Config, 'GEMINI_API_KEY', '').strip()
    return key.strip("'\"")

def is_gemini_available() -> bool:
    """Checks if GEMINI_API_KEY is configured with a valid key."""
    key = get_gemini_api_key()
    return bool(key and len(key) > 15 and not key.startswith('YOUR_'))

def call_gemini_api(prompt: str, system_instruction: str = "", model_name: str = "gemini-flash-latest") -> str:
    """
    Calls Google Gemini REST API directly using standard library urllib.
    Prioritizes gemini-flash-latest and newer endpoints for instant 200 OK responses.
    """
    api_key = get_gemini_api_key()
    if not api_key or api_key.startswith('YOUR_'):
        logger.info("Gemini API Key not set or default placeholder used.")
        return ""

    models_to_try = [
        "gemini-flash-latest",
        "gemini-2.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-pro-latest",
        "gemini-1.5-flash"
    ]

    contents_parts = []
    if system_instruction:
        contents_parts.append({"text": f"System Instruction: {system_instruction}\n\nUser Request: {prompt}"})
    else:
        contents_parts.append({"text": prompt})

    payload = {
        "contents": [
            {
                "parts": contents_parts
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }
    data_bytes = json.dumps(payload).encode('utf-8')

    for m_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={api_key}"
        try:
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                
                candidates = res_json.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        text = parts[0].get('text', '').strip()
                        if text:
                            return text
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            logger.warning(f"Gemini API ({m_name}) HTTPError {e.code}: {err_body[:150]}")
        except Exception as e:
            logger.warning(f"Gemini API ({m_name}) Request failed: {e}")

    return ""

def rewrite_bullet_point_ai(bullet_text: str, target_role: str = "Software Engineer") -> list:
    """
    Generates 3 ATS-optimized resume bullet variations using Gemini AI.
    """
    if not is_gemini_available():
        return []

    prompt = f"""You are an elite Tech Resume Coach and ATS Specialist.
Target Role: {target_role}
Original Bullet Point: "{bullet_text}"

Generate 3 high-impact, ATS-optimized resume bullet variations:
1. Quantifiable Impact Version (includes realistic performance metrics/percentages)
2. Action-Verb & Leadership Version (starts with strong active tech verb)
3. Technical Depth Version (emphasizes architectural skills, tools, and best practices)

Return ONLY a JSON array of 3 string items."""

    res_text = call_gemini_api(prompt)
    if not res_text:
        return []

    try:
        clean_text = res_text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_text)
        if isinstance(data, list) and len(data) > 0:
            return data
    except Exception:
        lines = [line.strip().lstrip('123456789.-*• ') for line in res_text.split('\n') if line.strip() and len(line.strip()) > 15]
        if lines:
            return lines[:3]

    return []

def evaluate_interview_answer_ai(question: str, model_answer: str, user_answer: str) -> dict:
    """
    Evaluates a candidate's interview answer using Gemini AI.
    """
    if not is_gemini_available():
        return {}

    prompt = f"""You are a Senior Technical Interviewer evaluating a candidate's response.

Question: "{question}"
Ideal Model Answer: "{model_answer}"
Candidate Answer: "{user_answer}"

Evaluate the candidate's answer and return a JSON object with EXACTLY these keys:
{{
  "score": integer between 0 and 100,
  "strengths": "1-2 sentence description of what the candidate did well",
  "missing_terms": ["list", "of", "important", "keywords", "candidate", "missed"],
  "feedback": "2-3 sentences of constructive coaching on how to improve this answer"
}}

Return ONLY valid JSON."""

    res_text = call_gemini_api(prompt)
    if not res_text:
        return {}

    try:
        clean_text = res_text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_text)
        if isinstance(data, dict) and "score" in data:
            return data
    except Exception:
        pass

    return {}

def generate_cover_letter_ai(resume_text: str, job_description: str, candidate_name: str = "Candidate", target_role: str = "Software Engineer") -> str:
    """
    Generates a professional 3-paragraph tailored cover letter using Gemini AI.
    """
    if not is_gemini_available():
        return ""

    prompt = f"""You are an expert Executive Career Coach and Recruiter.

Candidate Name: {candidate_name}
Target Role: {target_role}

Candidate Resume Summary:
{resume_text[:2000]}

Job Description:
{job_description[:2000]}

Write a highly compelling, professional 3-paragraph Cover Letter tailored specifically to this Job Description."""

    return call_gemini_api(prompt)

def optimize_resume_for_jd_ai(resume_text: str, job_description: str) -> list:
    """
    Generates 3-5 specific actionable bullet suggestions to tailor a resume to a JD.
    """
    if not is_gemini_available():
        return []

    prompt = f"""You are an ATS Optimization Expert.

Resume Content:
{resume_text[:2000]}

Job Description:
{job_description[:2000]}

Provide 4 concrete, highly specific recommendations for how the candidate can modify their resume bullet points and skill section to maximize ATS match score for this job.

Return ONLY a JSON array of strings:
[
  "Recommendation 1...",
  "Recommendation 2...",
  "Recommendation 3...",
  "Recommendation 4..."
]"""

    res_text = call_gemini_api(prompt)
    if not res_text:
        return []

    try:
        clean_text = res_text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_text)
        if isinstance(data, list):
            return data
    except Exception:
        pass

    return []

def chat_career_coach_ai(user_message: str, history: list = None) -> str:
    """
    Powers the floating AI Career Coach Chatbot assistant with Gemini AI + Smart Local Fallback.
    """
    msg_lower = user_message.lower().strip()

    # Try live Gemini API call first if available
    if is_gemini_available():
        history_context = ""
        if history and isinstance(history, list):
            formatted_h = [f"{m.get('role','user').capitalize()}: {m.get('content','')}" for m in history[-4:]]
            history_context = "\n".join(formatted_h) + "\n"

        prompt = f"""You are ResumeAI Coach, an encouraging, sharp, expert AI career mentor helping tech candidates (software developers, AI/ML engineers, CSE students) succeed in tech hiring, resume building, ATS optimization, and technical interviews.

Conversation History:
{history_context}

Candidate Message: "{user_message}"

Provide a concise, helpful, actionable response (under 150 words) with clear bullet points where appropriate."""

        res_text = call_gemini_api(prompt)
        if res_text:
            return res_text

    # --- SMART LOCAL FALLBACK ASSISTANT (Guarantees Chatbot Always Answers) ---
    if any(w in msg_lower for w in ['hi', 'hello', 'hey', 'greetings', 'namaste', 'hola']):
        return "Hello! I'm your ResumeAI Career Coach. How can I help you today with your resume building, ATS score optimization, or interview preparation?"

    if any(w in msg_lower for w in ['resume', 'ats', 'score', 'format', 'template']):
        return "Here are 3 key tips for ATS-friendly resumes:\n1. Use clean, single-column standard section headers (OBJECTIVE, TECHNICAL SKILLS, EXPERIENCE, PROJECTS, EDUCATION).\n2. Include quantifiable impact in bullet points (e.g. 'reduced latency by 30%').\n3. Add direct GitHub & Live Demo deployment links for your top technical projects."

    if any(w in msg_lower for w in ['interview', 'question', 'prep', 'dsa', 'behavioral']):
        return "For technical interview prep:\n1. Use the STAR method (Situation, Task, Action, Result) for behavioral & project questions.\n2. Review core computer science fundamentals: Data Structures, DBMS, OOPs, and Operating Systems.\n3. Practice explaining your project architecture step-by-step!"

    if any(w in msg_lower for w in ['job', 'match', 'description', 'apply', 'role']):
        return "To improve job match compatibility:\n1. Compare your resume against target JDs using our Job Matcher.\n2. Include key tech stack terms mentioned in the job posting.\n3. Generate a tailored cover letter highlighting relevant project achievements!"

    return f"Thanks for asking about '{user_message}'! As your Career Coach, I recommend focusing on strong technical project bullet points, quantifying your accomplishments, and practicing core CS interview questions."
