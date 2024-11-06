# src/util_tools/failures_utils.py
import pytest

def report(failures, message="테스트 실패 항목"):
    """실패 항목을 모아서 pytest.fail로 보고하는 함수."""
    if failures:
        failure_report = "\n".join(failures)
        pytest.fail(f"{message}:\n{failure_report}")