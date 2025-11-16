![GitHub release (latest by date)](https://img.shields.io/github/v/release/Idonotes9/json-tools)
![Build Status](https://github.com/Idonotes9/json-tools/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/github/license/Idonotes9/json-tools)
![Python](https://img.shields.io/badge/python-3.11-blue)

# json-tools (Extended)

Advanced Python CLI for working with JSON files.  
Includes a small utility script, JSON Schema validation, tests, and CI via GitHub Actions.

---

## Features

- **pretty** – Pretty-print JSON (optionally write changes back to file)
- **minify** – Compact JSON by removing unnecessary whitespace
- **validate** – Check JSON syntax and print validation result
- **pick** – Extract values by dotted path (e.g. `users[0].email`)
- **merge** – Deep-merge two JSON documents (right overrides left)
- **diff** – Show simple structural differences between two JSON objects
- **schema** – Validate JSON using a user-provided JSON Schema

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Idonotes9/json-tools.git
cd json-tools
