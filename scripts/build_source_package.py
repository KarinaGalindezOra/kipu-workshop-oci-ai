"""Create a source-only workshop archive without credentials or generated state."""

from __future__ import annotations

import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "delivery" / "khipu-workshop-labs-20261015-rc5-clean.zip"

EXCLUDED_DIRECTORIES = {
    ".git",
    ".codex-build",
    ".codex-finalizer",
    ".terraform",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "artifacts",
    "delivery",
    "output",
    "secrets",
    "transfer",
}
EXCLUDED_FILE_NAMES = {".env", "terraform.tfvars"}
EXCLUDED_SUFFIXES = {".key", ".pem", ".p12", ".jks", ".tfstate", ".zip"}


def is_included(path: Path) -> bool:
    """Return whether one repository file is safe to place in a source archive."""

    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRECTORIES for part in relative.parts[:-1]):
        return False
    if path.name in EXCLUDED_FILE_NAMES:
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if ".tfstate." in path.name:
        return False
    if "wallet" in path.name.lower():
        return False
    return True


def main() -> None:
    """Write the reproducible source package and print a safe manifest summary."""

    files: list[Path] = []
    for directory, subdirectories, file_names in os.walk(ROOT):
        subdirectories[:] = [
            item for item in subdirectories if item not in EXCLUDED_DIRECTORIES
        ]
        directory_path = Path(directory)
        for file_name in file_names:
            candidate = directory_path / file_name
            if is_included(candidate):
                files.append(candidate)
    files.sort()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for file_path in files:
            archive.write(file_path, file_path.relative_to(ROOT).as_posix())
    print(f"SOURCE_PACKAGE_READY {OUTPUT.name}")
    print(f"SOURCE_PACKAGE_FILES {len(files)}")
    print("SOURCE_PACKAGE_SECRETS_EXCLUDED true")


if __name__ == "__main__":
    main()
