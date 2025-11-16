import json
import subprocess
import sys
from pathlib import Path


def run_cli(args):
    """
    Helper to run the CLI and capture output.

    Args:
        args (list[str]): arguments after 'json_tools.py'

    Returns:
        (returncode, stdout, stderr)
    """
    cmd = [sys.executable, "json_tools.py"] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def test_pretty_command(tmp_path):
    # создаём простой JSON
    sample = tmp_path / "sample.json"
    sample.write_text('{"a": 1, "b": 2}', encoding="utf-8")

    code, out, err = run_cli(["pretty", str(sample)])

    # команда должна выполниться успешно
    assert code == 0
    assert err == ""

    # вывод должен быть валидным JSON
    data = json.loads(out)
    assert data == {"a": 1, "b": 2}


def test_minify_command(tmp_path):
    sample = tmp_path / "sample.json"
    sample.write_text('{\n  "a": 1,\n  "b": 2\n}', encoding="utf-8")

    code, out, err = run_cli(["minify", str(sample)])

    assert code == 0
    assert err == ""

    # снова проверяем, что вывод — валидный JSON
    data = json.loads(out)
    assert data == {"a": 1, "b": 2}


def test_validate_valid_json(tmp_path):
    sample = tmp_path / "valid.json"
    sample.write_text('{"ok": true}', encoding="utf-8")

    code, out, err = run_cli(["validate", str(sample)])

    # для валидного JSON достаточно, чтобы код возврата был 0
    assert code == 0


def test_validate_invalid_json(tmp_path):
    sample = tmp_path / "invalid.json"
    # специально ломаем JSON
    sample.write_text('{"broken": ', encoding="utf-8")

    code, out, err = run_cli(["validate", str(sample)])

    # ожидаем ошибку (ненулевой код возврата)
    assert code != 0

def test_schema_command_valid(tmp_path):
    data_path = tmp_path / "data.json"
    schema_path = tmp_path / "schema.json"

    data_path.write_text('{"age": 30}', encoding="utf-8")
    schema_path.write_text(
        '{"type": "object", "properties": {"age": {"type": "number"}}, "required": ["age"]}',
        encoding="utf-8",
    )

    code, out, err = run_cli(["schema", str(data_path), str(schema_path)])

    assert code == 0


def test_schema_command_invalid(tmp_path):
    data_path = tmp_path / "data_invalid.json"
    schema_path = tmp_path / "schema.json"

    data_path.write_text('{"age": "oops"}', encoding="utf-8")
    schema_path.write_text(
        '{"type": "object", "properties": {"age": {"type": "number"}}, "required": ["age"]}',
        encoding="utf-8",
    )

    code, out, err = run_cli(["schema", str(data_path), str(schema_path)])

    assert code != 0
