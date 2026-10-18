"""Offline transport attribution and end-to-end fail-closed regressions."""
from email.message import Message
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nws_transport_probe as probe
from test_forecast_runtime import CANONICAL, FixedClock, POLICY, documents
import forecast_runtime as runtime
from adapters import nws_snapshot as snapshot


class TransportProbeTests(unittest.TestCase):
    def test_connect_denial_is_not_target_http_403(self):
        self.assertEqual(probe.classify(403, 0, 56), "PROXY_CONNECT_REJECTED")
        self.assertEqual(probe.classify(407, 0, 56), "PROXY_CONNECT_REJECTED")
        self.assertEqual(probe.classify(200, 403, 0), "HTTP_403_CAUSE_AND_ORIGIN_UNVERIFIED")

    def test_rate_limit_and_transfer_failure_are_separate(self):
        self.assertEqual(probe.classify(200, 429, 0),
                         "HTTP_429_RATE_LIMIT_SIGNAL_ORIGIN_UNVERIFIED")
        self.assertEqual(probe.classify(0, 200, 63), "HTTP_RESPONSE_TRANSFER_FAILED")
        self.assertEqual(probe.classify(0, 0, 60), "DNS_TCP_TLS_OR_PROXY_FAILURE_UNRESOLVED")
        self.assertEqual(probe.classify(0, 200, 0), "HTTP_200_TRANSPORT_ONLY")

    def test_response_headers_preserve_layer_order_but_drop_secrets(self):
        blocks = probe.header_blocks("HTTP/1.1 200 Connection established\r\n\r\n"
            "HTTP/2 403\r\nServer: edge\r\nSet-Cookie: secret\r\n"
            "Authorization: secret\r\nRetry-After: 5\r\n")
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[1]["headers"], {"server": ["edge"], "retry-after": ["5"]})

    def test_403_429_and_connect_failure_at_either_request_never_make_scores(self):
        for failure in (HTTPError(probe.URL, 403, "Forbidden", Message(), None),
                        HTTPError(probe.URL, 429, "Too Many Requests", Message(), None),
                        URLError("Tunnel connection failed: 403 Forbidden")):
            for request_index in (0, 1):
                with self.subTest(error=type(failure).__name__, request_index=request_index):
                    points = snapshot.b64decode(documents()[0]["body_base64"])
                    replies = [failure] if request_index == 0 else [({}, points), failure]
                    with patch.object(runtime, "datetime", FixedClock), \
                         patch.object(snapshot.nws, "_get_json_bytes", side_effect=replies) as get:
                        result = runtime.run_forecast(CANONICAL.read_bytes(),
                            local_date="2026-10-13", freshness_policy=POLICY)
                    self.assertEqual(get.call_count, request_index + 1)
                    self.assertEqual(result["weather"]["source_state"], "UNKNOWN")
                    self.assertEqual(result["weather"]["records"], [])
                    self.assertEqual(result["weather"]["documents"], [])
                    self.assertEqual(result["evaluation"]["decision"], "UNKNOWN")
                    self.assertTrue(all(c["state"] == "UNKNOWN"
                                        for c in result["evaluation"]["conditions"]))
                    self.assertEqual(result["photography_verdict"], "NOT_EVALUABLE")
                    self.assertFalse(result["recommendation_eligible"])
                    self.assertNotIn("score", result)


if __name__ == "__main__":
    unittest.main()
