from __future__ import annotations

from pathlib import Path
import sys


BENCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_DIR))

from llm_client import _is_nested_transient  # noqa: E402


def test_nested_provider_errors_are_retryable():
    assert _is_nested_transient('{"message":"model_not_provisioned"}')
    assert _is_nested_transient('{"message":"No available channel for model x"}')


def test_invalid_request_is_not_retryable():
    assert not _is_nested_transient('{"message":"invalid request parameter"}')
