import argparse
import json
import sys
from pathlib import Path
from typing import Any, List, Tuple

from schema_validator import validate_json_with_schema


# -------------------------
# Базовые функции работы с JSON
# -------------------------


def load_json(path: Path) -> Any:
    """Загрузить JSON-файл в Python-объект."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    """Сохранить Python-объект в JSON-файл с красивым форматированием."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -------------------------
# Парсинг пути и выбор значения
# -------------------------


def parse_path(path: str) -> List[Tuple[Any, bool]]:
    """
    Разобрать строку вида 'a.b[2].c' в список токенов.

    Возвращает список кортежей (token, is_index), где:
      - token: str для ключа словаря или int для индекса списка
      - is_index: True, если token — индекс списка, False — ключ словаря

    Пример:
      parse_path("a.b[2].c")
      -> [("a", False), ("b", False), (2, True), ("c", False)]
    """
    tokens: List[Tuple[Any, bool]] = []
    buf = ""
    i = 0

    while i < len(path):
        ch = path[i]

        if ch == ".":  # разделитель полей
            if buf:
                tokens.append((buf, False))
                buf = ""
            i += 1

        elif ch == "[":  # индекс списка [2]
            if buf:
                tokens.append((buf, False))
                buf = ""
            j = path.index("]", i)
            idx_str = path[i + 1 : j]
            idx = int(idx_str)
            tokens.append((idx, True))
            i = j + 1
            # допускаем запись вида a[0].b
            if i < len(path) and path[i] == ".":
                i += 1

        else:
            buf += ch
            i += 1

    if buf:
        tokens.append((buf, False))

    return tokens


def pick(data: Any, dotted_path: str) -> Any:
    """
    Вернуть значение из вложенной структуры JSON-подобного объекта
    по строковому пути, используя представление parse_path.
    """
    cur = data
    for token, is_index in parse_path(dotted_path):
        if is_index:
            # token — индекс списка
            cur = cur[token]
        else:
            # token — ключ словаря
            cur = cur[token]
    return cur


# -------------------------
# Глубокое слияние и diff
# -------------------------


def deep_merge(left: Any, right: Any) -> Any:
    """
    Рекурсивно объединить два JSON-совместимых объекта.

    Словари мержатся по ключам (правый перезаписывает левый),
    остальные типы заменяются правым значением.
    """
    if isinstance(left, dict) and isinstance(right, dict):
        out = dict(left)
        for k, v in right.items():
            if k in out:
                out[k] = deep_merge(out[k], v)
            else:
                out[k] = v
        return out
    return right


def structural_diff(left: Any, right: Any) -> dict:
    """
    Очень простой diff для словарей: какие ключи есть только слева / справа.
    Для несопоставимых типов просто возвращает пустые списки.
    """
    if isinstance(left, dict) and isinstance(right, dict):
        return {
            "only_in_left": sorted(set(left.keys()) - set(right.keys())),
            "only_in_right": sorted(set(right.keys()) - set(left.keys())),
        }
    return {"only_in_left": [], "only_in_right": []}


# -------------------------
# Команды CLI
# -------------------------


def cmd_pretty(args: argparse.Namespace) -> None:
    data = load_json(Path(args.input))
    if args.output:
        save_json(Path(args.output), data)
    else:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


def cmd_minify(args: argparse.Namespace) -> None:
    data = load_json(Path(args.input))
    text = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")


def cmd_validate(args: argparse.Namespace) -> None:
    path = Path(args.input)
    try:
        load_json(path)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Invalid JSON: {e}\n")
        sys.exit(1)
    else:
        sys.stdout.write("Valid JSON\n")


def cmd_pick(args: argparse.Namespace) -> None:
    data = load_json(Path(args.input))
    value = pick(data, args.path)
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def cmd_merge(args: argparse.Namespace) -> None:
    left = load_json(Path(args.left))
    right = load_json(Path(args.right))
    merged = deep_merge(left, right)
    if args.output:
        save_json(Path(args.output), merged)
    else:
        json.dump(merged, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


def cmd_diff(args: argparse.Namespace) -> None:
    left = load_json(Path(args.left))
    right = load_json(Path(args.right))
    diff = structural_diff(left, right)
    json.dump(diff, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def cmd_schema(args: argparse.Namespace) -> None:
    """
    Проверка JSON с помощью JSON Schema.

    Использует вспомогательную функцию validate_json_with_schema
    из модуля schema_validator.py
    """
    ok = validate_json_with_schema(args.data, args.schema)
    if ok:
        sys.stdout.write("JSON matches schema\n")
        sys.exit(0)
    else:
        # schema_validator уже напечатает описание ошибки
        sys.exit(1)


# -------------------------
# Построение argparse CLI
# -------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="json-tools: small CLI for working with JSON files."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # pretty
    p_pretty = subparsers.add_parser("pretty", help="Pretty-print JSON file")
    p_pretty.add_argument("input", help="Input JSON file")
    p_pretty.add_argument("-o", "--output", help="Optional output file")
    p_pretty.set_defaults(func=cmd_pretty)

    # minify
    p_minify = subparsers.add_parser("minify", help="Minify JSON file")
    p_minify.add_argument("input", help="Input JSON file")
    p_minify.add_argument("-o", "--output", help="Optional output file")
    p_minify.set_defaults(func=cmd_minify)

    # validate
    p_validate = subparsers.add_parser("validate", help="Validate JSON syntax")
    p_validate.add_argument("input", help="Input JSON file")
    p_validate.set_defaults(func=cmd_validate)

    # pick
    p_pick = subparsers.add_parser("pick", help="Pick value by dotted path")
    p_pick.add_argument("input", help="Input JSON file")
    p_pick.add_argument(
        "--path",
        required=True,
        help="Dotted path (e.g., users[0].email)",
    )
    p_pick.set_defaults(func=cmd_pick)

    # merge
    p_merge = subparsers.add_parser("merge", help="Deep-merge two JSON files")
    p_merge.add_argument("left", help="Left JSON file")
    p_merge.add_argument("right", help="Right JSON file")
    p_merge.add_argument("-o", "--output", help="Optional output file")
    p_merge.set_defaults(func=cmd_merge)

    # diff
    p_diff = subparsers.add_parser(
        "diff",
        help="Show simple structural diff for two JSON files",
    )
    p_diff.add_argument("left", help="Left JSON file")
    p_diff.add_argument("right", help="Right JSON file")
    p_diff.set_defaults(func=cmd_diff)

    # schema
    p_schema = subparsers.add_parser(
        "schema",
        help="Validate JSON file using JSON Schema",
    )
    p_schema.add_argument("data", help="JSON data file")
    p_schema.add_argument("schema", help="JSON Schema file")
    p_schema.set_defaults(func=cmd_schema)

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
