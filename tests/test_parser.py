import unittest
import json
from pyrestfileparser.parser import parse_rest_file, HTTPRequest

class TestRestParser(unittest.TestCase):
    def test_valid_requests(self):
        sample_text = (
            "GET https://api.example.com HTTP/1.1\n"
            "Content-Type: application/json\n"
            "Authorization: Bearer abc123\n"
            "\n"
            '{"key": "value"}\n'
            "###\n"
            "POST https://api.example.com/submit HTTP/1.1\n"
            "Content-Type: application/json\n"
            "\n"
            '{"message": "Hello, world!"}\n'
        )
        requests_parsed = parse_rest_file(sample_text)

        self.assertEqual(len(requests_parsed), 2)
        

        req1: HTTPRequest = requests_parsed[0]
        self.assertEqual(req1.method, "GET")
        self.assertEqual(req1.url, "https://api.example.com")
        self.assertEqual(req1.http_version, "HTTP/1.1")
        self.assertEqual(req1.headers.get("Content-Type"), "application/json")
        self.assertEqual(req1.headers.get("Authorization"), "Bearer abc123")
        body1 = json.loads(req1.body)
        self.assertEqual(body1, {"key": "value"})
        

        req2: HTTPRequest = requests_parsed[1]
        self.assertEqual(req2.method, "POST")
        self.assertEqual(req2.url, "https://api.example.com/submit")
        self.assertEqual(req2.http_version, "HTTP/1.1")
        self.assertEqual(req2.headers.get("Content-Type"), "application/json")
        body2 = json.loads(req2.body)
        self.assertEqual(body2, {"message": "Hello, world!"})
    
    def test_invalid_content_type(self):
        sample_text = (
            "POST https://api.example.com/submit HTTP/1.1\n"
            "Content-Type: text/plain\n"
            "\n"
            '{"message": "Hello, world!"}\n'
        )
        with self.assertRaises(ValueError):
            parse_rest_file(sample_text)
    
    def test_invalid_json_body(self):
        sample_text = (
            "POST https://api.example.com/submit HTTP/1.1\n"
            "Content-Type: application/json\n"
            "\n"
            '{"message": "Hello, world!"\n'  # Missing closing brace.
        )
        with self.assertRaises(ValueError):
            parse_rest_file(sample_text)

if __name__ == '__main__':
    unittest.main()
