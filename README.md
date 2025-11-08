# json-tools (Extended)

Advanced Python CLI for working with JSON files.  
Includes testing, CI workflow, and sample data for demonstrations.

## Features
- **pretty** — Pretty-print JSON (supports `--inplace`)
- **minify** — Compact JSON by removing spaces
- **validate** — Validate JSON and print result
- **pick** — Extract values by dotted path (e.g., `users[0].email`)
- **merge** — Deep-merge two JSONs (right overrides left)
- **diff** — Show structural differences (added / removed / changed)

## Example usage
```bash
# Pretty-print a file
python json_tools.py pretty sample.json

# Extract first user's email
python json_tools.py pick sample.json --path users[0].email

# Validate JSON
python json_tools.py validate sample.json

# Create diff between two JSON files
python json_tools.py diff sample.json sample_changed.json
```

## Running tests
```bash
pytest -q
```

---
GitHub Actions runs tests automatically on every commit.
