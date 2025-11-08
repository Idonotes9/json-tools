#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterator, Tuple

def load_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(obj: Any, path: str | Path, pretty: bool = True) -> None:
    with open(path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write("\n")
        else:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))

def pretty_cmd(args: argparse.Namespace) -> int:
    obj = load_json(args.input)
    if args.inplace:
        save_json(obj, args.input, pretty=True)
    else:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    return 0

def minify_cmd(args: argparse.Namespace) -> int:
    obj = load_json(args.input)
    if args.inplace:
        save_json(obj, args.input, pretty=False)
    else:
        print(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
    return 0

def validate_cmd(args: argparse.Namespace) -> int:
    try:
        _ = load_json(args.input)
        print("OK")
        return 0
    except json.JSONDecodeError as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 1

def parse_path(path: str) -> list[tuple[str | int, bool]]:
    """
    Parse dotted path like a.b[0].c into a list of segments.
    Segment tuple: (key_or_index, is_index)
    """
    segments: list[tuple[str | int, bool]] = []
    i = 0
    token = ""
    while i < len(path):
        ch = path[i]
        if ch == ".":
            if token:
                segments.append((token, False))
                token = ""
            i += 1
        elif ch == "[":
            if token:
                segments.append((token, False))
                token = ""
            j = path.find("]", i)
            if j == -1:
                raise ValueError("Unclosed '[' in path")
            idx_str = path[i+1:j].strip()
            if not idx_str.isdigit():
                raise ValueError(f"Index must be integer inside [], got: {idx_str}")
            segments.append((int(idx_str), True))
            i = j + 1
        else:
            token += ch
            i += 1
    if token:
        segments.append((token, False))
    return segments

def pick(obj: Any, path: str) -> Any:
    segs = parse_path(path)
    cur = obj
    for key, is_index in segs:
        if is_index:
            if not isinstance(cur, list):
                raise KeyError(f"Expected list before index, got {type(cur).__name__}")
            cur = cur[key]
        else:
            if not isinstance(cur, dict):
                raise KeyError(f"Expected object before key '{key}', got {type(cur).__name__}")
            cur = cur[key]
    return cur

def pick_cmd(args: argparse.Namespace) -> int:
    obj = load_json(args.input)
    val = pick(obj, args.path)
    print(json.dumps(val, ensure_ascii=False, indent=2))
    return 0

def deep_merge(a: Any, b: Any) -> Any:
    """Merge b into a (non-destructive: returns new structure)."""
    if isinstance(a, dict) and isinstance(b, dict):
        res = dict(a)
        for k, v in b.items():
            if k in res:
                res[k] = deep_merge(res[k], v)
            else:
                res[k] = v
        return res
    elif isinstance(a, list) and isinstance(b, list):
        # simple policy: concatenate, then unique by JSON string form
        seen = set()
        out = []
        for item in a + b:
            s = json.dumps(item, sort_keys=True, ensure_ascii=False)
            if s not in seen:
                seen.add(s)
                out.append(item)
        return out
    else:
        return b  # b overrides a

def merge_cmd(args: argparse.Namespace) -> int:
    a = load_json(args.a)
    b = load_json(args.b)
    merged = deep_merge(a, b)
    print(json.dumps(merged, ensure_ascii=False, indent=2))
    return 0

def walk(obj: Any, prefix: str = "") -> Iterator[Tuple[str, Any]]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            yield from walk(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{prefix}[{i}]"
            yield from walk(v, p)
    else:
        yield prefix, obj

def diff_cmd(args: argparse.Namespace) -> int:
    a = load_json(args.a)
    b = load_json(args.b)

    map_a = dict(walk(a))
    map_b = dict(walk(b))

    keys_a = set(map_a.keys())
    keys_b = set(map_b.keys())

    added = sorted(keys_b - keys_a)
    removed = sorted(keys_a - keys_b)
    common = sorted(keys_a & keys_b)

    changed = [k for k in common if map_a[k] != map_b[k]]

    def print_section(title: str, items: list[str]):
        if items:
            print(f"== {title} ({len(items)}) ==")
            for k in items:
                if title == "Changed":
                    print(f"{k}: {map_a[k]!r} -> {map_b[k]!r}")
                else:
                    print(k)
            print()

    print_section("Added", added)
    print_section("Removed", removed)
    print_section("Changed", changed)
    return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="JSON utilities CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("pretty", help="Pretty-print JSON")
    sp.add_argument("input")
    sp.add_argument("--inplace", action="store_true")
    sp.set_defaults(func=pretty_cmd)

    sp = sub.add_parser("minify", help="Minify JSON")
    sp.add_argument("input")
    sp.add_argument("--inplace", action="store_true")
    sp.set_defaults(func=minify_cmd)

    sp = sub.add_parser("validate", help="Validate JSON")
    sp.add_argument("input")
    sp.set_defaults(func=validate_cmd)

    sp = sub.add_parser("pick", help="Extract value by dotted path with indexes, e.g. a.b[0].c")
    sp.add_argument("input")
    sp.add_argument("--path", required=True)
    sp.set_defaults(func=pick_cmd)

    sp = sub.add_parser("merge", help="Deep-merge two JSONs (right overrides left)")
    sp.add_argument("a")
    sp.add_argument("b")
    sp.set_defaults(func=merge_cmd)

    sp = sub.add_parser("diff", help="Diff two JSON files")
    sp.add_argument("a")
    sp.add_argument("b")
    sp.set_defaults(func=diff_cmd)

    return p

def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
