import os
import re
from config import Config

def improve_resume_content(content_text: str, content_type: str = "Project Description") -> dict:
    """
    AI Resume Content Improver & Bullet Point Rewriter.
    Uses LLM API if Configured (AI_PROVIDER='openai' or 'ollama'),
    otherwise uses a deterministic rule-based STAR transformation engine.
    
    CRITICAL RULE: NEVER fabricates experience, metrics, or achievements.
    """
    if not content_text or not content_text.strip():
        return {
            "original": "",
            "rewrites": [],
            "ai_available": False,
            "message": "Content text cannot be empty."
        }

    original_clean = content_text.strip()

    # 1. Try Configured LLM Provider
    provider = getattr(Config, 'AI_PROVIDER', 'none')
    api_key = getattr(Config, 'AI_API_KEY', '')

    if provider == "openai" and api_key:
        try:
            import urllib.request
            import json
            prompt = f"""You are a senior tech recruiter and resume editor. Rewrite the following resume {content_type} into 2 professional, high-impact bullet points using strong action verbs and STAR method.
DO NOT fabricate any fake metrics, experience, or percentages. If measurable metrics are missing, append '(Add a measurable result if you have a truthful metric)'.

Original Text:
"{original_clean}"

Return a JSON object with format: {{"rewrites": ["bullet 1", "bullet 2"]}}"""

            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = json.dumps({"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}).encode('utf-8')
            req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=data, headers=headers)
            with urllib.request.urlopen(req) as resp:
                res_data = json.loads(resp.read().decode('utf-8'))
                res_content = res_data['choices'][0]['message']['content']
                parsed = json.loads(res_content)
                return {
                    "original": original_clean,
                    "rewrites": parsed.get("rewrites", [res_content]),
                    "ai_available": True,
                    "provider": "OpenAI GPT"
                }
        except Exception as e:
            print(f"Notice: OpenAI API call skipped/failed ({e}). Falling back to rule engine.")

    # 2. Rule-Based STAR Transformation Engine (Fallback)
    action_verb_map = {
        r'\bmade\b': 'engineered',
        r'\bbuilt\b': 'architected and developed',
        r'\bworked on\b': 'spearheaded the development of',
        r'\bhelped with\b': 'collaborated on',
        r'\bused\b': 'leveraged',
        r'\bcreated\b': 'designed and deployed',
        r'\badded\b': 'integrated',
        r'\bfixed\b': 'resolved critical bugs in',
        r'\bchanged\b': 'refactored and optimized'
    }

    rewritten_1 = original_clean
    for weak_word, strong_verb in action_verb_map.items():
        rewritten_1 = re.sub(weak_word, strong_verb, rewritten_1, flags=re.IGNORECASE)

    # Capitalize first letter and format as professional bullet
    rewritten_1 = rewritten_1[0].upper() + rewritten_1[1:] if rewritten_1 else rewritten_1
    if not rewritten_1.endswith('.'):
        rewritten_1 += '.'

    # Check for metrics
    has_metrics = bool(re.search(r'\d+%', original_clean) or re.search(r'\d+\s*(users|clients|ms|requests)', original_clean))

    if not has_metrics:
        metric_note = " [Add a measurable result if you have a truthful metric, e.g., 'improving response speed by 20%']"
        bullet_option1 = f"• {rewritten_1}{metric_note}"
        bullet_option2 = f"• Spearheaded implementation: {rewritten_1}{metric_note}"
    else:
        bullet_option1 = f"• {rewritten_1}"
        bullet_option2 = f"• Key Contribution: {rewritten_1}"

    rewrites = [bullet_option1, bullet_option2]

    return {
        "original": original_clean,
        "rewrites": rewrites,
        "ai_available": False,
        "provider": "Rule-Based STAR Engine",
        "message": "AI API Key not configured. Using deterministic STAR transformation engine."
    }
