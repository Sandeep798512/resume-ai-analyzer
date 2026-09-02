import unittest
from app import app
from database.db import init_db

class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-key'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ResumeAI", response.data)

    def test_about_page_loads(self):
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Viva Reference", response.data)

    def test_protected_route_redirects_unauthenticated(self):
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b"Please log in to access this page", response.data)

if __name__ == "__main__":
    unittest.main()
