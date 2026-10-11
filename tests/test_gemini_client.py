import io
import json
import unittest
import urllib.error
from unittest.mock import patch

from src.providers.gemini import GeminiError, generate_reply


def response(data):
    return io.BytesIO(json.dumps(data).encode())


def model(name, methods=None):
    return {"name": "models/" + name, "supportedGenerationMethods": methods or ["generateContent"]}


def answer(*parts):
    return {"candidates": [{"content": {"parts": list(parts)}}]}


class GeminiClientTests(unittest.TestCase):
    @patch("src.providers.gemini.urllib.request.urlopen")
    def test_auto_paginates_filters_and_prefers_recent_stable_flash(self, open_url):
        open_url.side_effect = [
            response({"models": [model("gemini-1.5-flash"), model("gemini-9-flash-preview")], "nextPageToken": "next page"}),
            response({"models": [model("gemini-3.8-flash"), model("gemini-4-pro"), model("gemini-9-flash-image"), model("gemini-9-embedding", ["embedContent"])]}),
            response(answer({"text": "Olá "}, {"text": "segredo", "thought": True}, {"text": "mundo"})),
        ]
        self.assertEqual(generate_reply("oi", " secret "), "Olá mundo")
        calls = open_url.call_args_list
        self.assertIn("pageToken=next+page", calls[1].args[0].full_url)
        request = calls[2].args[0]
        self.assertTrue(request.full_url.endswith("models/gemini-3.8-flash:generateContent"))
        self.assertNotIn("secret", request.full_url)
        self.assertEqual(request.get_header("X-goog-api-key"), "secret")
        self.assertEqual(json.loads(request.data)["contents"][0]["parts"][0]["text"], "oi")

    @patch("src.providers.gemini.urllib.request.urlopen")
    def test_explicit_model_is_used_without_listing(self, open_url):
        open_url.return_value = response(answer({"text": "ok"}))
        self.assertEqual(generate_reply("oi", "key", "models/gemini-custom"), "ok")
        self.assertEqual(open_url.call_count, 1)
        self.assertIn("models/gemini-custom:generateContent", open_url.call_args.args[0].full_url)

    @patch("src.providers.gemini.urllib.request.urlopen")
    def test_retired_saved_model_uses_discovered_replacement(self, open_url):
        open_url.side_effect = [
            urllib.error.HTTPError("url", 404, "missing", {}, None),
            response({"models": [model("gemini-new-flash")]}),
            response(answer({"text": "ok"})),
        ]
        self.assertEqual(generate_reply("oi", "key", "gemini-1.5-flash"), "ok")
        self.assertEqual(open_url.call_count, 3)

    @patch("src.providers.gemini.urllib.request.urlopen")
    def test_http_failures_do_not_retry_other_models_or_expose_key(self, open_url):
        for code in (400, 401, 403, 429, 500, 503):
            with self.subTest(code=code):
                open_url.reset_mock()
                open_url.side_effect = urllib.error.HTTPError("url?key=secret", code, "secret", {}, None)
                with self.assertRaises(GeminiError) as error:
                    generate_reply("oi", "secret", "gemini-custom")
                self.assertEqual(error.exception.status, code)
                self.assertNotIn("secret", str(error.exception))
                self.assertEqual(open_url.call_count, 1)

    @patch("src.providers.gemini.urllib.request.urlopen")
    def test_empty_or_blocked_responses_are_errors(self, open_url):
        for data in ({}, answer(), {"promptFeedback": {"blockReason": "SAFETY"}},
                     {"candidates": [{"finishReason": "SAFETY", "content": {"parts": [{"text": "blocked"}]}}]}):
            with self.subTest(data=data):
                open_url.return_value = response(data)
                with self.assertRaises(GeminiError):
                    generate_reply("oi", "key", "gemini-custom")

    @patch("src.providers.gemini.urllib.request.urlopen")
    def test_network_errors(self, open_url):
        for error in (urllib.error.URLError("secret"), TimeoutError()):
            open_url.side_effect = error
            with self.assertRaisesRegex(GeminiError, "conectar"):
                generate_reply("oi", "key")

    @patch("src.providers.gemini.urllib.request.urlopen")
    def test_no_compatible_models(self, open_url):
        open_url.return_value = response({"models": [model("gemini-embedding", ["embedContent"])]})
        with self.assertRaisesRegex(GeminiError, "Nenhum modelo"):
            generate_reply("oi", "key")

    @patch("src.providers.gemini.urllib.request.urlopen")
    def test_disappearing_listed_model_tries_next(self, open_url):
        open_url.side_effect = [
            response({"models": [model("gemini-4-flash"), model("gemini-3-flash")]}),
            urllib.error.HTTPError("url", 404, "missing", {}, None),
            response(answer({"text": "ok"})),
        ]
        self.assertEqual(generate_reply("oi", "key"), "ok")


if __name__ == "__main__":
    unittest.main()
