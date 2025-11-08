# json-tools

Small but capable Python CLI for working with JSON files.

## Features
- **pretty**: pretty-print JSON with indentation (supports `--inplace`)
- **minify**: compact JSON (removes whitespace)
- **validate**: validate JSON (exit code 0/1)
- **pick**: extract value by dotted path with indexes, e.g. `a.b[0].c`
- **merge**: deep-merge two JSONs (right overrides left)
- **diff**: structural diff between two JSONs (added/removed/changed)

## Install (optional)
No external deps. You can just run it with Python:
```bash
python json_tools.py --help
```

## Examples
```bash
# pretty print to stdout
python json_tools.py pretty data.json

# in-place pretty formatting
python json_tools.py pretty data.json --inplace

# minify
python json_tools.py minify data.json > data.min.json

# validate
python json_tools.py validate data.json

# pick by path (dotted with indexes)
python json_tools.py pick data.json --path users[0].email

# merge (b overrides a)
python json_tools.py merge a.json b.json > merged.json

# diff
python json_tools.py diff old.json new.json
```
