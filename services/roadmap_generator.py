from services.skill_gap import analyze_skill_gap

def generate_learning_roadmap(resume_text: str, target_role: str = "Python Developer", custom_missing_skills: list = None) -> dict:
    """
    Constructs a phased 10-week personalized learning roadmap based on missing skills.
    """
    if custom_missing_skills is not None:
        missing_skills = custom_missing_skills
    else:
        gap = analyze_skill_gap(resume_text, target_role)
        missing_skills = [item["skill"] for item in gap["skill_breakdown"] if item["is_missing"]]

    # Fallback default missing skills if candidate already possesses all required skills
    if not missing_skills:
        missing_skills = ["Advanced System Design", "Docker & Kubernetes", "CI/CD & Cloud Deployment"]

    phases = []
    num_skills = len(missing_skills)

    # Week 1-2: Core Foundational Skill
    skill1 = missing_skills[0]
    phases.append({
        "timeframe": "Weeks 1–2",
        "phase_name": f"Foundations of {skill1}",
        "focus_skill": skill1,
        "objectives": [
            f"Understand fundamental concepts and core syntax of {skill1}.",
            f"Set up development environment and complete hands-on tutorials.",
            f"Build 2 small standalone practice exercises applying {skill1}."
        ]
    })

    # Week 3-4: Intermediate / Framework Integration
    if num_skills > 1:
        skill2 = missing_skills[1]
        phases.append({
            "timeframe": "Weeks 3–4",
            "phase_name": f"Mastering {skill2}",
            "focus_skill": skill2,
            "objectives": [
                f"Study architecture and best practices for {skill2}.",
                f"Integrate {skill2} with existing project codebases.",
                f"Write unit tests and verify functionality."
            ]
        })

    # Week 5-6: Advanced Tooling & Infrastructure
    if num_skills > 2:
        skill3 = missing_skills[2]
        phases.append({
            "timeframe": "Weeks 5–6",
            "phase_name": f"Practical Application of {skill3}",
            "focus_skill": skill3,
            "objectives": [
                f"Learn configuration, deployment, or database modeling with {skill3}.",
                f"Implement security and optimization patterns.",
                f"Troubleshoot common performance bottlenecks."
            ]
        })

    # Week 7-8: Specialized Skills / Testing
    if num_skills > 3:
        skill4 = missing_skills[3]
        phases.append({
            "timeframe": "Weeks 7–8",
            "phase_name": f"Deep Dive into {skill4}",
            "focus_skill": skill4,
            "objectives": [
                f"Explore production-grade patterns using {skill4}.",
                f"Incorporate logging, exception handling, and API documentation.",
                f"Review open-source examples and industry standards."
            ]
        })

    # Final Phase: Portfolio Project Integration
    phases.append({
        "timeframe": "Weeks 9–10",
        "phase_name": "Capstone Portfolio Project & Resume Update",
        "focus_skill": "Portfolio Capstone",
        "objectives": [
            f"Architect a full-stack or backend portfolio project combining {', '.join(missing_skills[:3])}.",
            "Publish clean, documented code to your public GitHub repository with a detailed README.",
            "Update your resume with new skill badges and quantifiable project achievements."
        ]
    })

    return {
        "target_role": target_role,
        "total_weeks": 10,
        "missing_skills": missing_skills,
        "phases": phases
    }
