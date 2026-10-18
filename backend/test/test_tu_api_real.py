import json
import os
import unittest
from unittest.mock import patch

from app.services.tu_api import _real_verify


class FakeResponse:
    status = 200

    def __init__(self, body: dict):
        self.body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.body


class RealTUApiTests(unittest.TestCase):
    @patch.dict(
        os.environ,
        {
            "TU_API_URL": "https://tu.example.test/auth",
            "TU_API_KEY": "test-application-key",
            "TU_API_TIMEOUT": "5",
        },
        clear=False,
    )
    @patch("app.services.tu_api.urlopen")
    def test_real_provider_uses_tu_contract(self, urlopen):
        urlopen.return_value = FakeResponse(
            {
                "status": True,
                "message": "Success",
                "displayname_th": "นักศึกษาตัวอย่าง",
                "type": "student",
            }
        )

        account = _real_verify("6800000000", "example-password")

        self.assertEqual(account.username, "6800000000")
        self.assertEqual(account.display_name, "นักศึกษาตัวอย่าง")
        self.assertEqual(account.account_type, "student")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Application-key"), "test-application-key")
        self.assertEqual(
            json.loads(request.data.decode("utf-8")),
            {"UserName": "6800000000", "PassWord": "example-password"},
        )


if __name__ == "__main__":
    unittest.main()
