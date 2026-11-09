"""The public Workshop 3 tree must stay participant-only and safe to distribute."""

import json
import re
from pathlib import Path
from urllib.parse import unquote

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parents[1]


def test_workshop3_matches_explicit_public_file_allowlist():
    expected = set(json.loads((LAB / "public_files.json").read_text())["files"])
    actual = {
        p.relative_to(LAB).as_posix()
        for p in LAB.rglob("*")
        if p.is_file() and not {"__pycache__", ".pytest_cache", ".ruff_cache"}.intersection(p.parts)
    }
    assert actual == expected, "Review every added file before changing the public allowlist"
    assert not any(
        "facilitator" in p or "/private/" in p or p.endswith("/admin.py") or p.endswith("/pilot.py")
        for p in actual
    )


def test_new_public_material_contains_no_identifiers_or_private_keys():
    identifier = re.compile(r"ocid1\.[a-z0-9]+\.[A-Za-z0-9._-]{25,}")
    key_marker = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
    files = json.loads((LAB / "public_files.json").read_text())["files"]
    for relative in files:
        text = (LAB / relative).read_text(encoding="utf-8")
        assert not identifier.search(text), relative
        assert not key_marker.search(text), relative


def test_workshop3_entry_point_and_guide_links_resolve():
    docs = [
        ROOT / "README.md",
        ROOT / "docs/participant-guides/README.md",
        LAB / "README.md",
        *sorted((LAB / "docs").glob("*.md")),
    ]
    for document in docs:
        text = re.sub(r"```[\s\S]*?```", "", document.read_text(encoding="utf-8"))
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            path = unquote(target.split("#", 1)[0].strip("<>"))
            assert (document.parent / path).exists(), f"{document.relative_to(ROOT)}: {target}"
