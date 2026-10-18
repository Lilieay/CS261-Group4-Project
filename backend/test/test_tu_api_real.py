import http.client
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from app.services.tu_api import TUVerificationError, verify_tu_account


class FakeResponse:
    def __init__(self, body: bytes, status: int = 200):
        self.body = body
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.body


class RealTUApiTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(
            os.environ,
            {
                "TU_API_MODE": "real",
                "TU_API_URL": "https://tu.example.test/auth",
                "TU_API_KEY": "test-application-key",
                "TU_API_TIMEOUT": "5",
            },
            clear=False,
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

    @patch("app.services.tu_api.urlopen")
    def test_real_provider_sends_official_request_and_parses_thai_name(self, urlopen):
        urlopen.return_value = FakeResponse(
            b'{"status":true,"type":"student","displayname_th":"\\u0e19\\u0e31\\u0e01\\u0e28\\u0e36\\u0e01\\u0e29\\u0e32"}'
        )

        account = verify_tu_account(" 6800000000 ", "example-password")

        self.assertEqual(account.username, "6800000000")
        self.assertEqual(account.display_name, "\u0e19\u0e31\u0e01\u0e28\u0e36\u0e01\u0e29\u0e32")
        self.assertEqual(account.account_type, "student")
        self.assertTrue(account.active)
        request, timeout = urlopen.call_args.args[0], urlopen.call_args.kwargs["timeout"]
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Application-key"), "test-application-key")
        self.assertEqual(timeout, 5)
        self.assertEqual(
            json.loads(request.data.decode("utf-8")),
            {"UserName": " 6800000000 ", "PassWord": "example-password"},
        )

    @patch("app.services.tu_api.urlopen")
    def test_english_name_is_used_when_thai_name_is_not_a_string(self, urlopen):
        urlopen.return_value = FakeResponse(
            b'{"status":true,"type":" STUDENT ","displayname_th":{"bad":1},"displayname_en":" Student Name "}'
        )
        account = verify_tu_account("6800000000", "pw")
        self.assertEqual(account.display_name, "Student Name")

    @patch("app.services.tu_api.urlopen")
    def test_english_name_is_used_when_thai_name_is_blank(self, urlopen):
        urlopen.return_value = FakeResponse(
            b'{"status":true,"type":"student","displayname_th":"  ","displayname_en":"Student Name"}'
        )
        self.assertEqual(verify_tu_account("6800000000", "pw").display_name, "Student Name")

    @patch("app.services.tu_api.urlopen")
    def test_ineligible_or_malformed_eligibility_fields_are_rejected(self, urlopen):
        cases = [
            b'{"status":false,"type":"student","displayname_en":"Name"}',
            b'{"type":"student","displayname_en":"Name"}',
            b'{"status":"true","type":"student","displayname_en":"Name"}',
            b'{"status":1,"type":"student","displayname_en":"Name"}',
            b'{"status":true,"displayname_en":"Name"}',
            b'{"status":true,"type":7,"displayname_en":"Name"}',
            b'{"status":true,"type":"employee","displayname_en":"Name"}',
            b'{"status":true,"type":"student","displayname_th":4,"displayname_en":[]}',
            b'{"status":true,"type":"student","displayname_th":"  ","displayname_en":null}',
            b'{"status":true,"type":"student"}',
        ]
        for body in cases:
            with self.subTest(body=body):
                urlopen.return_value = FakeResponse(body)
                self.assertIsNone(verify_tu_account("6800000000", "pw"))

    @patch("app.services.tu_api.urlopen")
    def test_invalid_json_utf8_and_non_object_raise_provider_error(self, urlopen):
        for body in (b"{", b"\xff", b"[]"):
            with self.subTest(body=body):
                urlopen.return_value = FakeResponse(body)
                with self.assertRaises(TUVerificationError):
                    verify_tu_account("6800000000", "pw")

    def test_missing_config_and_invalid_timeout_raise_provider_error(self):
        for name, value in (("TU_API_URL", ""), ("TU_API_KEY", ""), ("TU_API_TIMEOUT", "bad"), ("TU_API_TIMEOUT", "0"), ("TU_API_TIMEOUT", "inf")):
            with self.subTest(name=name, value=value), patch.dict(os.environ, {name: value}):
                with self.assertRaises(TUVerificationError):
                    verify_tu_account("6800000000", "pw")

    @patch("app.services.tu_api.urlopen")
    def test_http_network_timeout_and_read_errors_raise_provider_error(self, urlopen):
        errors = [
            HTTPError("https://tu.example.test/auth", 503, "Unavailable", {}, None),
            URLError("offline"),
            TimeoutError("timed out"),
            http.client.InvalidURL("bad URL"),
            http.client.BadStatusLine("malformed status"),
            OSError("read failed"),
        ]
        for error in errors:
            with self.subTest(error=type(error).__name__):
                urlopen.side_effect = error
                with self.assertRaises(TUVerificationError):
                    verify_tu_account("6800000000", "pw")
        urlopen.side_effect = None
        urlopen.return_value = FakeResponse(b'{"status":true}')
        read_errors = (OSError("read failed"), http.client.IncompleteRead(b"partial", 10))
        for read_error in read_errors:
            with patch.object(urlopen.return_value, "read", side_effect=read_error):
                with self.assertRaises(TUVerificationError):
                    verify_tu_account("6800000000", "pw")

        urlopen.return_value = FakeResponse(b'{"status":true}', status=503)
        with self.assertRaises(TUVerificationError):
            verify_tu_account("6800000000", "pw")


if __name__ == "__main__":
    unittest.main()
