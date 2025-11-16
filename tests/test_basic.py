from json_tools import load_json, deep_merge, pick, parse_path

def test_parse_path():
    path = "a.b[2].c"
    result = parse_path(path)
    # Наш парсер возвращает простые токены: "a", "b", 2, "c"
    assert result == ["a", "b", 2, "c"]

def test_deep_merge_dicts():
    a = {"x": 1, "nested": {"a": 1, "b": 2}}
    b = {"nested": {"b": 10, "c": 20}, "y": 2}
    merged = deep_merge(a, b)
    assert merged["nested"]["b"] == 10
    assert merged["nested"]["c"] == 20
    assert merged["x"] == 1

def test_pick_simple():
    obj = {"users": [{"email": "a@b.com"}]}
    assert pick(obj, "users[0].email") == "a@b.com"
