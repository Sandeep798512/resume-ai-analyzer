import json
from services.job_matcher import calculate_job_match
from services.resume_builder import duplicate_resume_version, parse_resume_version_data, get_db_connection

def optimize_resume_for_job(user_id: int, original_version_id: int, job_title: str, company_name: str, job_description: str) -> dict:
    """
    Targeted Resume Optimization Workflow:
    - Analyzes existing resume version against specific job posting.
    - Identifies missing skills & keywords.
    - Creates a new optimized version (e.g., 'Python Resume — Google Optimized').
    - NEVER alters the original resume version.
    """
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM resume_versions WHERE id = ? AND user_id = ?;", (original_version_id, user_id)).fetchone()
    conn.close()

    if not row:
        raise ValueError("Original resume version not found.")

    version_data = parse_resume_version_data(row)
    
    # Construct combined text string for matching
    combined_text = f"{version_data['summary']}\n"
    for cat, skills in version_data.get('skills', {}).items():
        combined_text += f"{cat}: {', '.join(skills) if isinstance(skills, list) else skills}\n"
    for proj in version_data.get('projects', []):
        combined_text += f"{proj.get('title', '')} {proj.get('tech_stack', '')} {proj.get('description', '')}\n"
    for exp in version_data.get('experience', []):
        combined_text += f"{exp.get('title', '')} {exp.get('company', '')} {exp.get('description', '')}\n"

    # Calculate Hybrid Match
    match_result = calculate_job_match(combined_text, job_description, job_title, company_name)

    # Create new optimized version name
    clean_company = company_name.strip() if company_name else "Target Job"
    new_version_name = f"{row['version_name']} — {clean_company} Optimized"

    # Duplicate version safely
    new_version_id = duplicate_resume_version(user_id, original_version_id, new_version_name)

    # Update new version's target role
    conn = get_db_connection()
    conn.execute("UPDATE resume_versions SET target_role = ? WHERE id = ?;", (job_title, new_version_id))
    conn.commit()
    conn.close()

    return {
        "original_version_id": original_version_id,
        "new_version_id": new_version_id,
        "new_version_name": new_version_name,
        "match_result": match_result
    }
