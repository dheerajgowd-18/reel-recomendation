"""JSON hygiene verification script for ScrollSense."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, List, Tuple


def check_object(obj: Any, path_prefix: str = "") -> List[str]:
    """Recursively check for leading/trailing whitespace in keys and string values."""
    errors: List[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            current_path = f"{path_prefix}.{k}" if path_prefix else k
            if k != k.strip():
                errors.append(f"Key has leading/trailing whitespace: '{k}' at {path_prefix or '<root>'}")
            errors.extend(check_object(v, current_path))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            current_path = f"{path_prefix}[{idx}]"
            errors.extend(check_object(item, current_path))
    elif isinstance(obj, str):
        if obj != obj.strip():
            errors.append(f"String value has leading/trailing whitespace: '{obj}' at {path_prefix}")
    return errors


def run_hygiene_check() -> bool:
    root_dir = Path(__file__).resolve().parent.parent
    target_dirs = [root_dir / "data", root_dir / "cache", root_dir / "output"]

    json_files: List[Path] = []
    for d in target_dirs:
        if d.is_dir():
            json_files.extend(sorted(d.glob("*.json")))

    if not json_files:
        print("[FAIL] No JSON files found to inspect.")
        return False

    all_passed = True
    files_checked = 0

    print("=" * 60)
    print(f"Checking JSON hygiene across {len(json_files)} files...")
    print("=" * 60)

    for jf in json_files:
        rel_path = jf.relative_to(root_dir)
        files_checked += 1
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
            violations = check_object(data)
            if violations:
                print(f"[FAIL] {rel_path}:")
                for v in violations:
                    print(f"       - {v}")
                all_passed = False
            else:
                print(f"[PASS] {rel_path} is clean")
        except Exception as exc:
            print(f"[FAIL] {rel_path} parse error: {exc}")
            all_passed = False

    print("=" * 60)
    print(f"Hygiene Summary: {'ALL PASSED' if all_passed else 'VIOLATIONS FOUND'} ({files_checked} files checked)")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = run_hygiene_check()
    if not success:
        sys.exit(1)
    sys.exit(0)
