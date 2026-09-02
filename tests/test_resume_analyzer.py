import unittest
from services.resume_analyzer import analyze_resume_quality, extract_contact_info

class TestResumeAnalyzer(unittest.TestCase):
    def test_extract_contact_info(self):
        text = "Sandeep Gaud, Email: sandeep@example.com, Phone: 9876543210, linkedin.com/in/sandeep, github.com/sandeep"
        contact = extract_contact_info(text)
        
        self.assertTrue(contact["email_found"])
        self.assertTrue(contact["phone_found"])
        self.assertTrue(contact["github_found"])
        self.assertTrue(contact["linkedin_found"])

    def test_resume_quality_scoring(self):
        sample_resume = """
        Sandeep Gaud
        Email: sandeep@example.com | Phone: 9876543210
        GitHub: github.com/sandeep | LinkedIn: linkedin.com/in/sandeep

        EDUCATION
        B.Tech in Computer Science and Engineering (AI) - 2026

        TECHNICAL SKILLS
        Programming: Python, Java, C++
        Web: Flask, REST API, HTML, CSS
        Database: SQL, SQLite, MongoDB
        Tools: Git, GitHub, Docker

        CERTIFICATIONS & ACHIEVEMENTS
        - Certified Python Developer | HackerRank Problem Solving 5 Stars

        PROJECTS
        AI Resume Analyzer & Job Matcher
        - Built automated Flask web app using pypdf and scikit-learn.
        - Reduced resume processing latency by 35% and served 100+ tests.

        EXPERIENCE
        Python Developer Intern at TechCorp
        - Implemented RESTful APIs and database schemas.
        """
        analysis = analyze_resume_quality(sample_resume)
        
        self.assertGreaterEqual(analysis["overall_score"], 65)
        self.assertTrue(analysis["section_data"]["sections"]["Education"]["present"])
        self.assertTrue(analysis["section_data"]["sections"]["Projects"]["present"])

if __name__ == "__main__":
    unittest.main()
