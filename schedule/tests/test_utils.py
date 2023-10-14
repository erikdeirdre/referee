import unittest
from helpers.utils import HttpError


class TestHttpError(unittest.TestCase):
    def test_http_error(self):
        http_error = HttpError("This is an error", 500)
        self.assertEqual(http_error.error, "This is an error")
        self.assertEqual(http_error.status_code, 500)
