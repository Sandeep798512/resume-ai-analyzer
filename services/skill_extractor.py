import re
from data.skills import SKILLS_DB, SKILL_DISPLAY_MAP
from services.text_processor import normalize_text

def extract_skills_from_text(text: str) -> dict:
    """
    Extracts technical and soft skills from input text based on SKILLS_DB.
    Returns:
    {
        "categorized": {
            "Programming": ["Python", "C++"],
            ...
        },
        "all_skills_lowercase": ["python", "c++", ...],
        "all_skills_display": ["Python", "C++", ...],
        "total_count": 2
    }
    """
    normalized_text = normalize_text(text)
    
    # We add extra padded spaces for boundary matching
    padded_text = f" {normalized_text} "
    
    detected_categorized = {}
    all_skills_lowercase = set()
    all_skills_display = set()

    for category, skill_list in SKILLS_DB.items():
        category_found = set()
        for skill in skill_list:
            skill_lower = skill.lower()
            
            # Build regex pattern for exact skill match taking tech symbols into account
            escaped_skill = re.escape(skill_lower)
            
            # Check boundary conditions
            # If skill starts/ends with word char, use \b, else match symbol
            pattern = r'(?<=[\s,;:\(\)\[\]\{\}\/])' + escaped_skill + r'(?=[\s,;:\(\)\[\]\{\}\/])'
            
            if re.search(pattern, padded_text) or (r'\b' + escaped_skill + r'\b' in pattern and re.search(r'\b' + escaped_skill + r'\b', normalized_text)):
                display_name = SKILL_DISPLAY_MAP.get(skill_lower, skill.title())
                category_found.add(display_name)
                all_skills_lowercase.add(skill_lower)
                all_skills_display.add(display_name)
            elif skill_lower in ["c++", "c#", ".net", "node.js", "express.js", "react.js", "vue.js", "next.js", "scikit-learn"]:
                # Special handle for symbols that regex \b might trip over
                if skill_lower in normalized_text:
                    display_name = SKILL_DISPLAY_MAP.get(skill_lower, skill.title())
                    category_found.add(display_name)
                    all_skills_lowercase.add(skill_lower)
                    all_skills_display.add(display_name)
        
        detected_categorized[category] = sorted(list(category_found))

    return {
        "categorized": detected_categorized,
        "all_skills_lowercase": sorted(list(all_skills_lowercase)),
        "all_skills_display": sorted(list(all_skills_display)),
        "total_count": len(all_skills_display)
    }
