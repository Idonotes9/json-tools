import argparse
import json
import sys
from pathlib import Path

from schema_validator import validate_json_with_schema


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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
    for part in dotted_path.split("."):
        if part.endswith("]"):
            # list access: name[index]
            name, idx = part.split("[", 1)
            idx = int(idx[:-1])
            if name:
                cur = cur[name]
            cur = cur[idx]
        else:
            cur = cur[part]
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
    # simple structural diff: keys present in one and not other
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
    """Новая команда: проверка JSON по JSON Schema."""
    ok = validate_json_with_schema(args.data, args.schema)
    if ok:
        sys.stdout.write("JSON matches schema\n")
        sys.exit(0)
    else:
        # validate_json_with_schema уже напечатает ошибку
        sys.exit(1)


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

    # schema (НОВАЯ КОМАНДА)
    p_schema = subparsers.add_parser(
        "schema", help="Validate JSON file using JSON Schema"
    )
    p_schema.add_argument("data", help="JSON data file")
    p_schema.add_argument("schema", help="JSON Schema file")
    p_schema.set_defaults(func=cmd_schema)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
