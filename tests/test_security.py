import unittest
import os
import tempfile
from app import app
from database.db import init_db
from services.pdf_parser import validate_pdf_file, PDFParsingError

class TestSecurityAndAuth(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False # Enable testing bypass for route simulation
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def test_health_check_endpoint(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'ok')

    def test_pdf_magic_bytes_validation(self):
        # Create non-PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"NOT A REAL PDF CONTENT")
            temp_path = f.name
        
        try:
            with self.assertRaises(PDFParsingError):
                validate_pdf_file(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()
