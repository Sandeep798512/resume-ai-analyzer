import unittest
from services.job_matcher import calculate_job_match

class TestJobMatcher(unittest.TestCase):
    def test_job_matcher_high_similarity(self):
        resume_text = "Experienced Python Backend Developer with Flask, SQL, REST API, Git, Docker, AWS, and Linux knowledge."
        jd_text = "We are seeking a Python Backend Developer proficient in Python, Flask, SQL, REST API, Git, Docker, AWS, and Linux."
        
        result = calculate_job_match(resume_text, jd_text, "Python Backend Developer")
        
        self.assertGreaterEqual(result["overall_match_score"], 70)
        self.assertIn(result["recommendation"], ["Strong Match", "Moderate Match"])
        self.assertIn("Python", result["matched_skills"])

    def test_job_matcher_missing_skills_priority(self):
        resume_text = "Python developer with basic SQL knowledge."
        jd_text = "Looking for Docker Docker Docker AWS AWS Kubernetes Kubernetes specialist with Python and SQL."
        
        result = calculate_job_match(resume_text, jd_text, "DevOps Engineer")
        
        self.assertIn("Docker", result["missing_skills_prioritized"]["HIGH"])

if __name__ == "__main__":
    unittest.main()
