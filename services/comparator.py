from services.resume_builder import parse_resume_version_data, get_db_connection
from services.skill_extractor import extract_skills_from_text

def compare_resume_versions(user_id: int, version_id_a: int, version_id_b: int) -> dict:
    """
    Compares two resume versions side-by-side:
    Evaluates Skill count, Section coverage, Project detail, and gives explicit rationale.
    """
    conn = get_db_connection()
    row_a = conn.execute("SELECT * FROM resume_versions WHERE id = ? AND user_id = ?;", (version_id_a, user_id)).fetchone()
    row_b = conn.execute("SELECT * FROM resume_versions WHERE id = ? AND user_id = ?;", (version_id_b, user_id)).fetchone()
    conn.close()

    if not row_a or not row_b:
        raise ValueError("One or both resume versions were not found.")

    data_a = parse_resume_version_data(row_a)
    data_b = parse_resume_version_data(row_b)

    # Calculate skill counts
    skills_a_count = sum(len(v) if isinstance(v, list) else 1 for v in data_a.get("skills", {}).values())
    skills_b_count = sum(len(v) if isinstance(v, list) else 1 for v in data_b.get("skills", {}).values())

    proj_a_count = len(data_a.get("projects", []))
    proj_b_count = len(data_b.get("projects", []))

    exp_a_count = len(data_a.get("experience", []))
    exp_b_count = len(data_b.get("experience", []))

    score_a = min(100, (skills_a_count * 4) + (proj_a_count * 15) + (exp_a_count * 15) + (30 if data_a.get("summary") else 0))
    score_b = min(100, (skills_b_count * 4) + (proj_b_count * 15) + (exp_b_count * 15) + (30 if data_b.get("summary") else 0))

    if score_a > score_b:
        winner = data_a["version_name"]
        rationale = f"Version '{data_a['version_name']}' is stronger because it demonstrates higher technical skill density ({skills_a_count} vs {skills_b_count}) and deeper project details."
    elif score_b > score_a:
        winner = data_b["version_name"]
        rationale = f"Version '{data_b['version_name']}' is stronger because it contains more categorized technical skills ({skills_b_count} vs {skills_a_count}) and comprehensive work details."
    else:
        winner = "Tie"
        rationale = "Both resume versions display equivalent skill density and project coverage."

    return {
        "resume_a": {
            "id": data_a["id"],
            "name": data_a["version_name"],
            "target_role": data_a["target_role"],
            "skills_count": skills_a_count,
            "projects_count": proj_a_count,
            "experience_count": exp_a_count,
            "overall_score": score_a
        },
        "resume_b": {
            "id": data_b["id"],
            "name": data_b["version_name"],
            "target_role": data_b["target_role"],
            "skills_count": skills_b_count,
            "projects_count": proj_b_count,
            "experience_count": exp_b_count,
            "overall_score": score_b
        },
        "winner": winner,
        "rationale": rationale
    }
