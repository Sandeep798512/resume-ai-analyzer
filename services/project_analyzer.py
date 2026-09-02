import re
from services.text_processor import normalize_text

def analyze_projects_content(text: str) -> dict:
    """
    Analyzes project mentions in resume text for details such as:
    - Tech stack mentioned in projects
    - Action verbs
    - Quantifiable metrics / measurable outcomes (%, numbers, Xx improvement)
    """
    normalized = normalize_text(text)
    
    # Check for quantifiable indicators (numbers followed by %, 'x', 'ms', 'users', 'accuracy')
    metric_pattern = r'\b(\d+(\.\d+)?%|\d+\s*(users|clients|ms|seconds|fps|requests|accuracy|speedup|reduction|increase|fold))\b'
    has_metrics = bool(re.search(metric_pattern, normalized))
    
    # Check for technical project indicators
    project_keywords = ["built", "developed", "designed", "created", "implemented", "deployed", "integrated", "architecture", "system"]
    detected_verbs = [kw for kw in project_keywords if kw in normalized]
    
    word_count = len(normalized.split())
    
    score = 0
    feedback = []
    suggestions = []

    if len(detected_verbs) >= 3:
        score += 40
        feedback.append("Strong technical action verbs detected (e.g., built, developed, implemented).")
    elif len(detected_verbs) > 0:
        score += 20
        feedback.append("Some technical action verbs detected.")
    else:
        suggestions.append("Use strong action verbs like 'Developed', 'Architected', 'Implemented', or 'Deployed'.")

    if has_metrics:
        score += 60
        feedback.append("Quantifiable metrics and measurable results detected (e.g., %, user counts, performance speedups).")
    else:
        score += 20
        suggestions.append("Add measurable outcomes to your projects (e.g., 'improved query speed by 30%', 'handled 500+ users', 'achieved 95% model accuracy').")

    return {
        "score": min(score, 100),
        "has_metrics": has_metrics,
        "action_verbs": detected_verbs,
        "feedback": feedback,
        "suggestions": suggestions
    }
