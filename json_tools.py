import argparse
import json
import sys
from pathlib import Path

from schema_validator import validate_json_with_schema


# ---------------------------------------------------------
#  PATH PARSER (старый формат, который ожидают тесты)
# ---------------------------------------------------------
def parse_path(path: str):
    """
    Parse dotted/indexed path like 'a.b[2].c' into tokens:
        ["a", "b", 2, "c"]
    """
    tokens = []
    buf = ""
    i = 0

    while i < len(path):
        ch = path[i]

        if ch == ".":      # разделитель
            if buf:
                tokens.append(buf)
                buf = ""
            i += 1

        elif ch == "[":    # индекс массива
            if buf:
                tokens.append(buf)
                buf = ""

            j = path.index("]", i)
            idx_str = path[i + 1 : j]
            tokens.append(int(idx_str))
            i = j + 1

            if i < len(path) and path[i] == ".":
                i += 1

        else:              # обычный символ
            buf += ch
            i += 1

    if buf:
        tokens.append(buf)

    return tokens


# ---------------------------------------------------------
#  JSON helpers
# ---------------------------------------------------------
def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------
#  COMMAND IMPLEMENTATIONS
# ---------------------------------------------------------
def cmd_pretty(args):
    data = load_json(Path(args.input))
    if args.output:
        save_json(Path(args.output), data)
    else:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


def cmd_minify(args):
    data = load_json(Path(args.input))
    text = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")


def cmd_validate(args):
    path = Path(args.input)
    try:
        load_json(path)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Invalid JSON: {e}\n")
        sys.exit(1)
    else:
        sys.stdout.write("Valid JSON\n")


def get_by_path(data, dotted_path: str):
    cur = data
    for token in parse_path(dotted_path):
        cur = cur[token]
    return cur


def cmd_pick(args):
    data = load_json(Path(args.input))
    value = get_by_path(data, args.path)
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def deep_merge(left, right):
    if isinstance(left, dict) and isinstance(right, dict):
        out = dict(left)
        for k, v in right.items():
            if k in out:
                out[k] = deep_merge(out[k], v)
            else:
                out[k] = v
        return out
    return right


def cmd_merge(args):
    left = load_json(Path(args.left))
    right = load_json(Path(args.right))
    merged = deep_merge(left, right)
    if args.output:
        save_json(Path(args.output), merged)
    else:
        json.dump(merged, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


def cmd_diff(args):
    left = load_json(Path(args.left))
    right = load_json(Path(args.right))

    if isinstance(left, dict) and isinstance(right, dict):
        diff = {
            "only_in_left": sorted(set(left.keys()) - set(right.keys())),
            "only_in_right": sorted(set(right.keys()) - set(left.keys())),
        }
    else:
        diff = {"only_in_left": [], "only_in_right": []}

    json.dump(diff, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def cmd_schema(args):
    ok = validate_json_with_schema(args.data, args.schema)
    if ok:
        sys.stdout.write("JSON matches schema\n")
        sys.exit(0)
    else:
        sys.exit(1)


# ---------------------------------------------------------
#  ARGPARSE
# ---------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="json-tools: small CLI for working with JSON files."
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # pretty
    p = sub.add_parser("pretty", help="Pretty-print JSON")
    p.add_argument("input")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_pretty)

    # minify
    p = sub.add_parser("minify", help="Minify JSON")
    p.add_argument("input")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_minify)

    # validate syntax
    p = sub.add_parser("validate", help="Validate JSON syntax")
    p.add_argument("input")
    p.set_defaults(func=cmd_validate)

    # pick
    p = sub.add_parser("pick", help="Pick value by dotted path")
    p.add_argument("input")
    p.add_argument("--path", required=True)
    p.set_defaults(func=cmd_pick)

    # merge
    p = sub.add_parser("merge", help="Merge two JSON files")
    p.add_argument("left")
    p.add_argument("right")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_merge)

    # diff
    p = sub.add_parser("diff", help="Diff keys of two JSON objects")
    p.add_argument("left")
    p.add_argument("right")
    p.set_defaults(func=cmd_diff)

    # schema
    p = sub.add_parser("schema", help="Validate JSON using JSON Schema")
    p.add_argument("data")
    p.add_argument("schema")
    p.set_defaults(func=cmd_schema)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
