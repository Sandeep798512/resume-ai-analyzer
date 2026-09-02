import json
import re
from config import Config
from data.interview_bank import ROLE_INTERVIEW_BANK, DEFAULT_INTERVIEW_BANK
from services.text_processor import normalize_text

def generate_interview_prep(target_role: str, missing_skills: list = None, resume_projects: list = None) -> dict:
    """
    Generates structured interview questions WITH detailed model answers & key terms.
    """
    role_bank = ROLE_INTERVIEW_BANK.get(target_role, DEFAULT_INTERVIEW_BANK)

    # 1. Try LLM if configured
    provider = getattr(Config, 'AI_PROVIDER', 'none')
    api_key = getattr(Config, 'AI_API_KEY', '')

    if provider == "openai" and api_key:
        try:
            import urllib.request
            prompt = f"""Generate a structured technical interview prep kit for candidate targeting '{target_role}'.
Missing Skills: {', '.join(missing_skills[:5]) if missing_skills else 'None'}.
Return JSON format:
{{
  "technical": [
    {{"question": "q1", "model_answer": "answer1", "key_terms": ["term1", "term2"]}},
    {{"question": "q2", "model_answer": "answer2", "key_terms": ["term1", "term2"]}}
  ],
  "resume": [
    {{"question": "q1", "model_answer": "answer1", "key_terms": ["term1"]}}
  ],
  "behavioral": [
    {{"question": "q1", "model_answer": "answer1", "key_terms": ["term1"]}}
  ],
  "dsa": ["topic1", "topic2"],
  "cs_fundamentals": ["topic1", "topic2"]
}}"""
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = json.dumps({"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}).encode('utf-8')
            req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=data, headers=headers)
            with urllib.request.urlopen(req) as resp:
                res_data = json.loads(resp.read().decode('utf-8'))
                parsed = json.loads(res_data['choices'][0]['message']['content'])
                return {
                    "target_role": target_role,
                    "questions": parsed,
                    "provider": "OpenAI GPT-3.5 Turbo"
                }
        except Exception as e:
            print(f"Notice: LLM API call for interview prep failed/skipped ({e}). Using structured curated bank.")

    # 2. Rule-Based Curated Bank with Model Answers (Fallback)
    tech_q = list(role_bank["technical"])
    if missing_skills:
        for ms in missing_skills[:2]:
            tech_q.insert(0, {
                "question": f"How would you approach learning and implementing {ms} in a production codebase?",
                "model_answer": f"To master {ms}: 1. Understand core principles and syntax. 2. Build a hands-on project integrating {ms} with Flask/SQL. 3. Implement error handling, unit testing, and benchmarking.",
                "key_terms": [ms.lower(), "principles", "hands-on", "testing", "benchmarking"]
            })

    resume_q = list(role_bank["resume"])
    if resume_projects and len(resume_projects) > 0:
        p_name = resume_projects[0].get("title", "capstone project")
        resume_q.insert(0, {
            "question": f"Walk me through the design and technical challenges of your project '{p_name}'.",
            "model_answer": f"Use STAR method: Explain problem solved by '{p_name}', architecture layers built, technical roadblock overcome, and final quantifiable results achieved.",
            "key_terms": [p_name.lower(), "star method", "architecture", "quantifiable"]
        })

    return {
        "target_role": target_role,
        "questions": {
            "technical": tech_q,
            "resume": resume_q,
            "behavioral": role_bank["behavioral"],
            "dsa": role_bank["dsa"],
            "cs_fundamentals": role_bank["cs_fundamentals"]
        },
        "provider": "Curated Technical Question & Answer Bank"
    }

def evaluate_candidate_answer(question: str, user_answer: str, target_role: str = "Software Engineer", model_answer: str = "", key_terms: list = None) -> dict:
    """
    Evaluates candidate's typed answer to an interview question.
    Generates Score %, Strengths, Missing Terms, and AI Feedback.
    """
    if not user_answer or not user_answer.strip():
        return {
            "question": question,
            "score": 0,
            "feedback": "Answer text cannot be empty.",
            "strengths": [],
            "missing_terms": key_terms or [],
            "model_answer": model_answer
        }

    norm_answer = normalize_text(user_answer)
    words = norm_answer.split()

    # 1. Try LLM Evaluation if configured
    provider = Config.AI_PROVIDER
    api_key = Config.AI_API_KEY

    if provider == "openai" and api_key:
        try:
            import urllib.request
            prompt = f"""You are a technical interviewer for '{target_role}'. Evaluate candidate's answer to this question:
Question: "{question}"
Candidate's Answer: "{user_answer}"
Model Answer: "{model_answer}"

Return JSON format:
{{
  "score": 85,
  "feedback": "Concise 2-sentence summary of answer quality",
  "strengths": ["strength 1", "strength 2"],
  "missing_terms": ["concept 1", "concept 2"]
}}"""
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = json.dumps({"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}).encode('utf-8')
            req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=data, headers=headers)
            with urllib.request.urlopen(req) as resp:
                res_data = json.loads(resp.read().decode('utf-8'))
                parsed = json.loads(res_data['choices'][0]['message']['content'])
                parsed["question"] = question
                parsed["model_answer"] = model_answer
                return parsed
        except Exception as e:
            print(f"LLM Answer evaluation skipped/failed ({e}). Using concept match evaluator.")

    # 2. Concept Match Evaluator (Fallback)
    expected_terms = [t.lower() for t in (key_terms or [])]
    found_terms = []
    missing_terms = []

    for term in expected_terms:
        if term in norm_answer:
            found_terms.append(term.title())
        else:
            missing_terms.append(term.title())

    term_score = (len(found_terms) / len(expected_terms) * 60) if expected_terms else 40
    length_score = 40 if len(words) >= 30 else (20 if len(words) >= 15 else 10)
    
    total_score = round(min(100, term_score + length_score))

    strengths = []
    if len(words) >= 25:
        strengths.append("Detailed explanation length with sufficient context.")
    if found_terms:
        strengths.append(f"Successfully included core key technical terms: {', '.join(found_terms)}.")

    if total_score >= 80:
        feedback = "Excellent answer! You demonstrated strong technical clarity and used appropriate industry terminology."
    elif total_score >= 60:
        feedback = "Good response! Incorporating the missing key concepts below will make your answer even more compelling to recruiters."
    else:
        feedback = "Basic response. Expand on technical details, structure your answer using STAR method, and mention key concepts below."

    return {
        "question": question,
        "score": total_score,
        "feedback": feedback,
        "strengths": strengths,
        "missing_terms": missing_terms,
        "model_answer": model_answer or "Review the ideal model answer structure above."
    }
