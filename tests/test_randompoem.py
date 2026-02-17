import unittest
from unittest.mock import patch, Mock

from scraping.randompoem import scrape


class TestScrape(unittest.TestCase):
    @patch("scraping.randompoem.requests.get")
    def test_scrape_returns_poem_dict(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"title": "Test", "author": "Author", "lines": ["a", "b"]}
        ]
        mock_get.return_value = mock_response

        result = scrape()

        self.assertEqual(result["title"], "Test")
        self.assertEqual(result["author"], "Author")
        self.assertEqual(result["content"], "a\nb")

    @patch("scraping.randompoem.requests.get")
    def test_scrape_returns_none_for_api_error_shape(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status": 404, "reason": "Not found"}
        mock_get.return_value = mock_response

        result = scrape(title="missing")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
