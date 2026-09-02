from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from services.text_processor import normalize_text, tokenize_words
from services.skill_extractor import extract_skills_from_text
from services.semantic_matcher import compute_semantic_similarity
from data.skills import SKILL_DISPLAY_MAP

def calculate_job_match(resume_text: str, job_description: str, job_title: str = "Target Role", company_name: str = "") -> dict:
    """
    Hybrid Job Description Compatibility Engine V2:
    Combines:
    1. TF-IDF Text Similarity (25%)
    2. Semantic Vector Cosine Similarity (35%) via Sentence Transformers
    3. Categorized Skill Overlap Match (30%)
    4. Keyword Coverage Analysis (10%)
    """
    normalized_resume = normalize_text(resume_text)
    normalized_jd = normalize_text(job_description)

    # 1. TF-IDF Similarity (25%)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([normalized_resume, normalized_jd])
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        tfidf_score_pct = round(float(cosine_sim) * 100, 1)
    except Exception:
        tfidf_score_pct = 50.0

    # 2. Semantic Embedding Similarity (35%)
    semantic_score_pct = compute_semantic_similarity(resume_text, job_description)

    # 3. Categorized Skill Extraction & Overlap (30%)
    resume_skills_info = extract_skills_from_text(resume_text)
    jd_skills_info = extract_skills_from_text(job_description)

    resume_skills_lower = set(resume_skills_info["all_skills_lowercase"])
    jd_skills_lower = set(jd_skills_info["all_skills_lowercase"])

    matched_skills_lower = resume_skills_lower.intersection(jd_skills_lower)
    missing_skills_lower = jd_skills_lower - resume_skills_lower

    matched_skills = [SKILL_DISPLAY_MAP.get(s, s.title()) for s in sorted(list(matched_skills_lower))]
    missing_skills_raw = list(missing_skills_lower)

    if len(jd_skills_lower) > 0:
        skill_match_pct = round((len(matched_skills_lower) / len(jd_skills_lower)) * 100, 1)
    else:
        skill_match_pct = 75.0

    # Priority missing skills classification
    high_priority = []
    medium_priority = []
    low_priority = []

    for skill in missing_skills_raw:
        display_name = SKILL_DISPLAY_MAP.get(skill, skill.title())
        freq = normalized_jd.count(skill)
        if freq >= 3:
            high_priority.append(display_name)
        elif freq == 2:
            medium_priority.append(display_name)
        else:
            low_priority.append(display_name)

    # 4. Keyword Coverage Analysis (10%)
    vectorizer_kw = TfidfVectorizer(max_features=15, stop_words='english')
    try:
        vectorizer_kw.fit([normalized_jd])
        top_jd_keywords = list(vectorizer_kw.get_feature_names_out())
    except Exception:
        jd_tokens = tokenize_words(normalized_jd, remove_stopwords=True)
        top_jd_keywords = list(set(jd_tokens))[:10]

    keyword_breakdown = []
    matched_kw_count = 0
    for kw in top_jd_keywords:
        in_resume = kw in normalized_resume
        if in_resume:
            matched_kw_count += 1
        keyword_breakdown.append({
            "keyword": kw,
            "matched": in_resume
        })

    if len(top_jd_keywords) > 0:
        keyword_coverage_pct = round((matched_kw_count / len(top_jd_keywords)) * 100, 1)
    else:
        keyword_coverage_pct = 50.0

    # 5. Hybrid Weighted Final Score
    hybrid_score = round(
        (tfidf_score_pct * 0.25) +
        (semantic_score_pct * 0.35) +
        (skill_match_pct * 0.30) +
        (keyword_coverage_pct * 0.10)
    )
    hybrid_score = max(0, min(100, hybrid_score))

    if hybrid_score >= 80:
        recommendation = "Strong Match"
        recommendation_desc = "Your resume demonstrates excellent technical and semantic alignment with this job description."
    elif hybrid_score >= 60:
        recommendation = "Moderate Match"
        recommendation_desc = "Good alignment overall. Addressing high-priority missing skills will significantly improve your match rate."
    else:
        recommendation = "Weak Match"
        recommendation_desc = "Significant skill gaps and semantic differences identified relative to the job requirements."

    score_breakdown = {
        "Semantic Similarity (35%)": semantic_score_pct,
        "Skill Match Rate (30%)": skill_match_pct,
        "TF-IDF Text Match (25%)": tfidf_score_pct,
        "Keyword Coverage (10%)": keyword_coverage_pct
    }

    return {
        "job_title": job_title,
        "company_name": company_name,
        "overall_match_score": hybrid_score,
        "recommendation": recommendation,
        "recommendation_desc": recommendation_desc,
        "score_breakdown": score_breakdown,
        "matched_skills": matched_skills,
        "missing_skills_prioritized": {
            "HIGH": sorted(high_priority),
            "MEDIUM": sorted(medium_priority),
            "LOW": sorted(low_priority)
        },
        "all_missing_skills": [SKILL_DISPLAY_MAP.get(s, s.title()) for s in sorted(missing_skills_raw)],
        "keyword_breakdown": keyword_breakdown,
        "keyword_coverage_pct": keyword_coverage_pct,
        "jd_skills_count": len(jd_skills_lower),
        "matched_skills_count": len(matched_skills)
    }
