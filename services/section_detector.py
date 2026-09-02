import re
from data.section_keywords import SECTION_KEYWORDS
from services.text_processor import normalize_text

def detect_resume_sections(text: str) -> dict:
    """
    Detects which standard resume sections are present or missing in the text.
    Returns:
    {
        "sections": {
            "Education": {"present": True, "matched_keyword": "education"},
            "Experience": {"present": False, "matched_keyword": None},
            ...
        },
        "present_count": 5,
        "total_count": 11,
        "missing_sections": ["Certifications", ...]
    }
    """
    normalized = normalize_text(text)
    
    section_results = {}
    present_count = 0
    missing_sections = []

    for section_name, keywords in SECTION_KEYWORDS.items():
        found = False
        matched_kw = None
        
        for kw in keywords:
            # Match keyword as standalone line or header
            pattern = r'(?i)\b' + re.escape(kw) + r'\b'
            if re.search(pattern, normalized):
                found = True
                matched_kw = kw
                break
        
        section_results[section_name] = {
            "present": found,
            "matched_keyword": matched_kw
        }
        
        if found:
            present_count += 1
        else:
            missing_sections.append(section_name)

    return {
        "sections": section_results,
        "present_count": present_count,
        "total_count": len(SECTION_KEYWORDS),
        "missing_sections": missing_sections
    }
