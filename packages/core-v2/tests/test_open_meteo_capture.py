"""Transport/ledger/replay negatives using explicit fixtures; no live calls."""
from datetime import datetime, timedelta, timezone
from email.message import Message
import hashlib
from io import BytesIO
from http.client import IncompleteRead
import json
from pathlib import Path
import signal
import ssl
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import open_meteo_hourly_pilot as tool
om = tool.adapter
INPUTS = om.load_inputs()
URL = om.build_request(INPUTS)
RAW = (Path(__file__).parent / "fixtures/open-meteo/synthetic-hourly.json").read_bytes()
T = "2026-10-19T16:05:00Z"


class Response:
    def __init__(self, raw=RAW, status=200, url=URL, content_type="application/json", **headers):
        self.raw, self.status, self.url = raw, status, url
        self.headers = {"Content-Type":content_type, "Date":"Mon, 19 Oct 2026 00:00:00 GMT", **headers}
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def geturl(self): return self.url
    def read(self, size): return self.raw[:size]


class Opener:
    def __init__(self, response): self.response, self.calls = response, []
    def open(self, request, timeout):
        self.calls.append((request, timeout))
        if isinstance(self.response, Exception): raise self.response
        return self.response


def archive(directory):
    receipt = {"contract_sha":om.CONTRACT_SHA, "pilot_binding_sha256":om.BINDING_SHA256,
               "schema_sha256":om.SCHEMA_SHA256, "request":om.request_metadata(INPUTS),
               "request_url":URL, "final_url":URL, "requested_at_utc":T,
               "retrieved_at_utc":T, "normalized_at_utc":T,
               "retrieval_mode":"TEST_FIXTURE", "http_status":200, "body_complete":True,
               "raw_sha256":hashlib.sha256(RAW).hexdigest(), "raw_size":len(RAW), "error":None}
    (directory / "response-body.bin").write_bytes(RAW)
    tool._write(directory / "capture.json", receipt)
    return receipt


class ManualCapture(unittest.TestCase):
    def test_one_bounded_request_and_http_date_is_transport_only(self):
        opener = Opener(Response())
        packet = tool.fetch_one(URL, opener=opener)
        self.assertIsNone(packet["error"])
        self.assertEqual(packet["raw"], RAW)
        self.assertEqual(len(opener.calls), 1)
        request, timeout = opener.calls[0]
        self.assertEqual(timeout, 20)
        self.assertEqual(request.get_header("Accept-encoding"), "identity")
        self.assertEqual(packet["http_date"], "Mon, 19 Oct 2026 00:00:00 GMT")

    def test_http_errors_archive_body_and_never_retry_429(self):
        for status in [301, 302, 403, 429, 500]:
            headers = Message(); headers["Retry-After"] = "3600"; headers["Content-Type"] = "application/json"
            opener = Opener(HTTPError(URL, status, "test only", headers, BytesIO(b'{"error":true}')))
            packet = tool.fetch_one(URL, opener=opener)
            with self.subTest(status=status):
                self.assertEqual(packet["error"], "HTTP_"+str(status))
                self.assertEqual(packet["retry_after"], "3600")
                self.assertEqual(packet["raw"], b'{"error":true}')
                self.assertEqual(len(opener.calls), 1)
        self.assertIsNone(tool.NoRedirect().redirect_request(None, None, 302, "test", {}, "https://other.invalid"))

    def test_redirected_success_response_is_rejected(self):
        result = tool.fetch_one(URL, opener=Opener(Response(url="https://other.invalid/forecast")))
        self.assertEqual(result["error"], "REDIRECT_REJECTED")

    def test_tls_failure_timeout_and_network_failure_have_no_weather(self):
        for error in [URLError(ssl.SSLError("test TLS failure")), TimeoutError("test deadline"), URLError("test network denied"), IncompleteRead(b"partial")]:
            opener = Opener(error); packet = tool.fetch_one(URL, opener=opener)
            with self.subTest(error=str(error)):
                self.assertIsNone(packet["raw"]); self.assertIsNotNone(packet["error"])
                self.assertEqual(len(opener.calls), 1)

    def test_html_wrong_encoding_and_oversized_bodies_cannot_be_json(self):
        for response, reason in [(Response(raw=b"<html>",content_type="text/html"),"NON_JSON_CONTENT_TYPE"),
                                 (Response(**{"Content-Encoding":"gzip"}),"UNSUPPORTED_CONTENT_ENCODING"),
                                 (Response(raw=b"x"*(om.MAX_BYTES+9)),"OVERSIZED_BODY_TRUNCATED")]:
            packet = tool.fetch_one(URL, opener=Opener(response))
            self.assertEqual(packet["error"], reason)
            self.assertLessEqual(len(packet["raw"]), om.MAX_BYTES+1)
        # An invalid source-unit string must not crash archive serialization.
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"invalid-unit.json"
            tool._write(path,{"source_unit":"\ud800"})
            self.assertEqual(json.loads(path.read_text())["source_unit"],"\ud800")

    @unittest.skipUnless(hasattr(signal, "SIGALRM") and hasattr(signal, "setitimer"),
                         "POSIX wall-clock deadline is unavailable on this platform")
    def test_wall_clock_deadline_restores_signal_handler(self):
        previous = signal.getsignal(signal.SIGALRM)
        with self.assertRaises(TimeoutError):
            with tool.network_deadline(0.01): time.sleep(0.1)
        self.assertEqual(signal.getsignal(signal.SIGALRM), previous)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL)[0], 0)

    def test_ledger_reserves_failure_attempt_and_enforces_refresh(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"ledger.jsonl"
            t = datetime(2026,10,19,tzinfo=timezone.utc)
            tool.reserve_capture(path, t)
            for delta in [-1, 0, 10799]:
                with self.assertRaisesRegex(om.PilotFailure,"CAPTURE_REFRESH_BUDGET"):
                    tool.reserve_capture(path, t+timedelta(seconds=delta))
            tool.reserve_capture(path, t+timedelta(seconds=10800))
            self.assertEqual(len(path.read_text().splitlines()),2)

    def test_ledger_corruption_future_and_shared_limit_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"ledger.jsonl"; t=om.utc(T)
            path.write_text("corrupt\n")
            with self.assertRaisesRegex(om.PilotFailure,"INVALID_CAPTURE_LEDGER"): tool.reserve_capture(path,t)
            path.write_text("".join(json.dumps({"requested_at_utc":om.stamp(t-timedelta(hours=4))})+"\n" for _ in range(8)))
            with self.assertRaisesRegex(om.PilotFailure,"CAPTURE_DAILY_BUDGET"): tool.reserve_capture(path,t)
            path.write_text(json.dumps({"requested_at_utc":om.stamp(t+timedelta(days=1))})+"\n")
            with self.assertRaises(om.PilotFailure): tool.reserve_capture(path,t)

    def test_failed_capture_keeps_original_error_and_unverified_no_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            packet=tool.fetch_one(URL,opener=Opener(URLError("test-only denied")))
            with patch.object(tool,"fetch_one",return_value=packet):
                receipt=tool.capture_once(root/"capture",root/"ledger","TEST ONLY mock; not real evidence")
            self.assertEqual(receipt["http_attempts"],1)
            self.assertEqual(receipt["provider_acceptance"],"UNVERIFIED")
            self.assertIsNone(receipt["result"]["artifact"])
            self.assertFalse((root/"capture/artifact.json").exists())
            self.assertFalse((root/"capture/response-body.bin").exists())
            with self.assertRaises(FileExistsError): tool.capture_once(root/"capture",root/"ledger","test")

    def test_offline_replay_preserves_fixture_mode_and_original_clocks(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp); archive(path)
            with patch.object(tool,"fetch_one",side_effect=AssertionError("replay must not fetch")):
                replay=tool.replay_capture(path,checked_at=T)
            self.assertEqual(replay["operation"],"OFFLINE_REPLAY")
            self.assertEqual(replay["network_attempts"],0)
            self.assertFalse(replay["new_live_capture"])
            a=replay["result"]["artifact"]
            self.assertEqual(a["source"]["retrieval_mode"],"TEST_FIXTURE")
            self.assertEqual(a["source"]["retrieved_at_utc"],T)
            later=tool.replay_capture(path,checked_at=om.utc(T)+timedelta(seconds=21601))
            self.assertEqual(later["result"]["availability"],"STALE")

    def test_replay_rejects_modified_body_identity_and_failed_capture(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp); receipt=archive(path)
            (path/"response-body.bin").write_bytes(b"x"*len(RAW))
            self.assertIsNone(tool.replay_capture(path,checked_at=T)["result"]["artifact"])
            receipt=archive(path);receipt["request"]["latitude"]=0
            tool._write(path/"capture.json",receipt)
            self.assertIsNone(tool.replay_capture(path,checked_at=T)["result"]["artifact"])
            receipt=archive(path);receipt["http_status"]=429;receipt["error"]="HTTP_429"
            tool._write(path/"capture.json",receipt)
            self.assertIsNone(tool.replay_capture(path,checked_at=T)["result"]["artifact"])

    def test_cli_requires_explicit_live_opt_in_and_has_no_implicit_capture(self):
        result=subprocess.run([sys.executable,str(Path(tool.__file__)),"capture"],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn("--live",result.stderr)


if __name__=="__main__": unittest.main()
