import json
from database.db import get_db_connection

def create_resume_version(user_id: int, version_name: str, target_role: str = "Software Engineer", initial_data: dict = None) -> int:
    """
    Creates a new independent resume version record.
    """
    data = initial_data or {}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resume_versions (
            user_id, version_name, target_role, summary,
            contact_info_json, education_json, skills_json,
            experience_json, projects_json, certifications_json, template_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        user_id,
        version_name,
        target_role,
        data.get("summary", ""),
        json.dumps(data.get("contact_info", {})),
        json.dumps(data.get("education", [])),
        json.dumps(data.get("skills", {})),
        json.dumps(data.get("experience", [])),
        json.dumps(data.get("projects", [])),
        json.dumps(data.get("certifications", [])),
        data.get("template_name", "ats_classic")
    ))
    version_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return version_id

def duplicate_resume_version(user_id: int, original_id: int, new_name: str) -> int:
    """
    Duplicates an existing resume version without altering the original.
    """
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM resume_versions WHERE id = ? AND user_id = ?;", (original_id, user_id)).fetchone()
    if not row:
        conn.close()
        raise ValueError("Original resume version not found.")

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resume_versions (
            user_id, version_name, target_role, summary,
            contact_info_json, education_json, skills_json,
            experience_json, projects_json, certifications_json, template_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        user_id,
        new_name,
        row['target_role'],
        row['summary'],
        row['contact_info_json'],
        row['education_json'],
        row['skills_json'],
        row['experience_json'],
        row['projects_json'],
        row['certifications_json'],
        row['template_name']
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_user_resume_versions(user_id: int) -> list:
    """
    Fetches all resume versions owned by a user.
    """
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM resume_versions WHERE user_id = ? ORDER BY id DESC;", (user_id,)).fetchall()
    conn.close()
    return rows

def parse_resume_version_data(row) -> dict:
    """
    Parses database row into JSON dict structure.
    """
    if not row:
        return {}
    
    cert_data = json.loads(row["certifications_json"] or "{}") if isinstance(row["certifications_json"], str) and row["certifications_json"].startswith("{") else json.loads(row["certifications_json"] or "[]")
    
    cert_list = []
    ach_list = []
    
    if isinstance(cert_data, dict):
        cert_list = cert_data.get("certifications", [])
        ach_list = cert_data.get("achievements", [])
    elif isinstance(cert_data, list):
        cert_list = cert_data

    return {
        "id": row["id"],
        "version_name": row["version_name"],
        "target_role": row["target_role"],
        "summary": row["summary"] or "",
        "contact_info": json.loads(row["contact_info_json"] or "{}"),
        "education": json.loads(row["education_json"] or "[]"),
        "skills": json.loads(row["skills_json"] or "{}"),
        "experience": json.loads(row["experience_json"] or "[]"),
        "projects": json.loads(row["projects_json"] or "[]"),
        "certifications": cert_list,
        "achievements": ach_list,
        "template_name": row["template_name"] or "ats_classic",
        "created_at": row["created_at"]
    }
