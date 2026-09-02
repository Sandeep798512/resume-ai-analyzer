-- ResumeAI V2 Database Schema (SQLite & PostgreSQL Compatible)

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER PRIMARY KEY,
    college TEXT,
    degree TEXT,
    branch TEXT,
    graduation_year INTEGER,
    github_url TEXT,
    linkedin_url TEXT,
    phone TEXT,
    target_role TEXT DEFAULT 'Software Engineer',
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS resume_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    version_name TEXT NOT NULL,
    target_role TEXT DEFAULT 'Software Engineer',
    summary TEXT,
    contact_info_json TEXT,
    education_json TEXT,
    skills_json TEXT,
    experience_json TEXT,
    projects_json TEXT,
    certifications_json TEXT,
    template_name TEXT DEFAULT 'ats_classic',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    resume_version_id INTEGER,
    resume_filename TEXT NOT NULL,
    resume_score INTEGER NOT NULL,
    job_title TEXT,
    company_name TEXT,
    job_match_score INTEGER,
    recommended_role TEXT,
    analysis_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(resume_version_id) REFERENCES resume_versions(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    target_role TEXT NOT NULL,
    job_title TEXT,
    questions_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_analyses_user ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_resumes_user ON resume_versions(user_id);
