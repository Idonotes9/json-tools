import subprocess
from pathlib import Path


def run_cli(args):
    result = subprocess.run(
        ["python", "json_tools.py"] + args,
        capture_output=True,
        text=True
    )
    return result.stdout.strip(), result.stderr.strip()


def test_pretty(tmp_path):
    sample = tmp_path / "sample.json"
    sample.write_text('{"a":1,"b":2}')

    out, err = run_cli(["pretty", str(sample)])
    assert err == ""
    assert out.startswith("{") and out.count("\n") > 1


def test_minify(tmp_path):
    sample = tmp_path / "sample.json"
    sample.write_text('{\n    "a": 1,\n    "b": 2\n}')

    out, err = run_cli(["minify", str(sample)])
    assert err == ""
    assert out == '{"a":1,"b":2}'


def test_validate_ok(tmp_path):
    sample = tmp_path / "ok.json"
    sample.write_text('{"ok": true}')

    out, err = run_cli(["validate", str(sample)])
    assert "valid" in out.lower()


def test_validate_fail(tmp_path):
    sample = tmp_path / "bad.json"
    sample.write_text('{"broken": ')

    out, err = run_cli(["validate", str(sample)])
    assert "invalid" in out.lower() or "error" in out.lower()
