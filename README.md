![GitHub release (latest by date)](https://img.shields.io/badge/release-v0.2.0-blue)
![Build Status](https://github.com/Idonotes9/json-tools/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/github/license/Idonotes9/json-tools)
![Python](https://img.shields.io/badge/python-3.11-blue)

# json-tools (Extended)

Advanced Python CLI for working with JSON files.
Includes a small utility script, JSON Schema validation, tests, and CI via GitHub Actions.

------------------------------------------------------------

## Features

- pretty – Pretty-print JSON (optionally write changes back to file)
- minify – Compact JSON by removing unnecessary whitespace
- validate – Check JSON syntax and print validation result
- pick – Extract values by dotted path (e.g. users[0].email)
- merge – Deep-merge two JSON documents (right overrides left)
- diff – Show simple structural differences between two JSON objects
- schema – Validate JSON using a user-provided JSON Schema

------------------------------------------------------------

## Installation

Clone the repository:

git clone https://github.com/Idonotes9/json-tools.git
cd json-tools

(Optional) create virtual environment:

python -m venv .venv
source .venv/bin/activate     (Windows: .venv\Scripts\activate)

Install optional dependencies:

pip install -r requirements.txt

------------------------------------------------------------

## Usage

Run:

python json_tools.py <command> [options]

------------------------------------------------------------

## Commands

### pretty
Pretty-print JSON:

python json_tools.py pretty sample.json
python json_tools.py pretty sample.json -o formatted.json

### minify
Produce compact JSON:

python json_tools.py minify sample.json
python json_tools.py minify sample.json -o min.json

### validate
Check JSON syntax:

python json_tools.py validate sample.json

### pick
Extract nested value:

python json_tools.py pick data.json --path users[0].email

### merge
Deep merge:

python json_tools.py merge base.json override.json
python json_tools.py merge base.json override.json -o merged.json

### diff
Show structural differences:

python json_tools.py diff file1.json file2.json

Example output:

{
  "only_in_left": ["oldKey"],
  "only_in_right": ["newKey"]
}

### schema
Validate JSON using JSON Schema:

python json_tools.py schema data.json schema.json

Exit codes:
0 – matches schema
1 – validation failed

------------------------------------------------------------

## Tests

Tests use pytest and are in /tests.

Run manually:

pytest -q

CI automatically runs tests on push and pull requests.

------------------------------------------------------------

## Roadmap (v0.2.0)

- Improved diff for nested objects
- Additional CLI improvements
- More usage examples
- Expanded JSON Schema support
- Increased test coverage

------------------------------------------------------------

## Contributing

1. Open an Issue  
2. Create a feature branch  
3. Submit a Pull Request  
4. Ensure tests pass (pytest -q)

------------------------------------------------------------

## License

MIT License — see LICENSE file.
