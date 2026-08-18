"""Data loader utilities for ScrollSense."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.config import (
    EXPECTED_OUTPUTS_PATH,
    IDENTITY_GRAPH_PATH,
    TECH_REELS_PATH,
    TRAP_REGRESSION_PATH,
    WATCHED_REELS_PATH,
)


def _load_json_file(path: Path) -> Any:
    """Load and parse a JSON file with explicit error handling."""
    if not path.is_file():
        raise FileNotFoundError(f"Required data file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse JSON file {path}: {exc}") from exc
    except Exception as exc:
        raise IOError(f"Error reading file {path}: {exc}") from exc


def load_watched_reels(path: Path = WATCHED_REELS_PATH) -> List[Dict[str, Any]]:
    """Load watched reels dataset."""
    data = _load_json_file(path)
    if not isinstance(data, list):
        raise ValueError(f"Expected list in {path}, got {type(data).__name__}")
    return data


def load_tech_reels(path: Path = TECH_REELS_PATH) -> List[Dict[str, Any]]:
    """Load tech reels candidate catalog."""
    data = _load_json_file(path)
    if not isinstance(data, list):
        raise ValueError(f"Expected list in {path}, got {type(data).__name__}")
    return data


def load_expected_outputs(path: Path = EXPECTED_OUTPUTS_PATH) -> Dict[str, Dict[str, str]]:
    """Load expected outputs benchmark fixtures."""
    data = _load_json_file(path)
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict in {path}, got {type(data).__name__}")
    return data


def load_identity_graph(path: Path = IDENTITY_GRAPH_PATH) -> Dict[str, Any]:
    """Load identity and skill graph."""
    data = _load_json_file(path)
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict in {path}, got {type(data).__name__}")
    return data


def load_trap_regression(path: Path = TRAP_REGRESSION_PATH) -> Dict[str, Any]:
    """Load trap regression benchmark specifications."""
    data = _load_json_file(path)
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict in {path}, got {type(data).__name__}")
    return data
