import unittest
from services.skill_extractor import extract_skills_from_text

class TestSkillExtractor(unittest.TestCase):
    def test_extract_programming_skills(self):
        sample_text = "Proficient in Python, C++, Java, and SQL databases."
        result = extract_skills_from_text(sample_text)
        detected_display = result["all_skills_display"]
        
        self.assertIn("Python", detected_display)
        self.assertIn("C++", detected_display)
        self.assertIn("Java", detected_display)
        self.assertIn("SQL", detected_display)

    def test_skill_aliases(self):
        sample_text = "Experience with ML models, NLP text analysis, Postgres DB, and ReactJS frontend."
        result = extract_skills_from_text(sample_text)
        detected_display = result["all_skills_display"]
        
        self.assertIn("Machine Learning", detected_display)
        self.assertIn("NLP", detected_display)
        self.assertIn("PostgreSQL", detected_display)
        self.assertIn("React", detected_display)

if __name__ == "__main__":
    unittest.main()
