"""
ResumeAI Demo Seeding Script
Generates a sample valid PDF resume and populates a test user in SQLite.
"""

import os
from database.db import get_db_connection, init_db
from werkzeug.security import generate_password_hash

def seed_demo_data():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if demo user exists
    existing = cursor.execute("SELECT id FROM users WHERE email = ?;", ("student@demo.com",)).fetchone()
    if not existing:
        pw_hash = generate_password_hash("demo1234")
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?);", ("Demo Student", "student@demo.com", pw_hash))
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO profiles (user_id, college, degree, branch, graduation_year, github_url, linkedin_url) VALUES (?, ?, ?, ?, ?, ?, ?);",
                       (user_id, "State Institute of Technology", "B.Tech", "Computer Science (AI)", 2026, "https://github.com/demostudent", "https://linkedin.com/in/demostudent"))
        conn.commit()
        print("Created demo user: student@demo.com / demo1234")
    else:
        print("Demo user already exists.")
    
    conn.close()

if __name__ == "__main__":
    seed_demo_data()
