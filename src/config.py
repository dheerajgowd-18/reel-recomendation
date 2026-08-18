"""Configuration and constants for ScrollSense pipeline."""

from pathlib import Path
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data directory and files
DATA_DIR = PROJECT_ROOT / "data"
WATCHED_REELS_PATH = DATA_DIR / "watched_reels.json"
TECH_REELS_PATH = DATA_DIR / "tech_reels.json"
EXPECTED_OUTPUTS_PATH = DATA_DIR / "expected_outputs.json"
IDENTITY_GRAPH_PATH = DATA_DIR / "identity_graph.json"
TRAP_REGRESSION_PATH = DATA_DIR / "trap_regression.json"

# Cache directory and files
CACHE_DIR = PROJECT_ROOT / "cache"
SIGNALS_CACHE_PATH = CACHE_DIR / "signals.json"

# Output directory and default files
OUTPUT_DIR = PROJECT_ROOT / "output"
DEFAULT_RESULT_PATH = OUTPUT_DIR / "result.txt"
DEFAULT_TRACE_PATH = OUTPUT_DIR / "trace.json"

# Versioning metadata
SIGNAL_VERSION = "v1"
ONTOLOGY_VERSION = "graph-v1"
MODEL_VERSION = "deterministic-rules-v1"

# Contract validation rules
REQUIRED_OUTPUT_FIELDS: List[str] = [
    "CURRENT REEL",
    "INTEREST DETECTED",
    "WHY",
    "RECOMMENDED TECH REEL",
    "CATEGORY",
    "WHY THIS RECOMMENDATION",
    "DIFFICULTY",
    "CONFIDENCE",
]

ALLOWED_CATEGORIES: Set[str] = {
    "AI",
    "DSA",
    "Java",
    "HLD",
    "Cybersecurity",
    "Cloud",
    "Hardware",
    "Career",
    "Other",
}

ALLOWED_DIFFICULTIES: Set[str] = {
    "Beginner",
    "Intermediate",
    "Advanced",
}

ALLOWED_CONFIDENCES: Set[str] = {
    "High",
    "Medium",
    "Low",
}

# Signal schema validation rules
ALLOWED_EVIDENCE_TYPES: Set[str] = {
    "topic_exposure",
    "domain_signal",
    "professional_identity_signal",
    "career_stage_signal",
    "goal_signal",
    "skill_signal",
    "tooling_signal",
    "content_preference_signal",
}

ALLOWED_FORMATS: Set[str] = {
    "meme",
    "lifestyle",
    "humor",
    "comparison",
    "news",
    "gaming",
    "unboxing",
}

ALLOWED_TONES: Set[str] = {
    "humorous",
    "aspirational",
    "informational",
    "comparative",
    "entertainment",
}

ALLOWED_DEPTHS: Set[str] = {
    "surface",
    "conceptual",
    "technical",
}

REQUIRED_SIGNAL_FIELDS: List[str] = [
    "reel_id",
    "signal_version",
    "ontology_version",
    "model_version",
    "generated_at",
    "topic",
    "format",
    "tone",
    "depth",
    "concept_tags",
    "interest_evidence",
]

REQUIRED_EVIDENCE_FIELDS: List[str] = [
    "evidence_type",
    "value",
    "strength",
    "source_hint",
]

# Deterministic mappings for Phase 1 stub pipeline
CHECKPOINT_MAPPING: Dict[str, str] = {
    "R1": "trap_after_R1",
    "R1,R2": "trap_after_R1_R2",
    "R1,R2,R3": "trap_after_R1_R2_R3",
    "R1,R2,R3,R4": "trap_after_R1_R2_R3_R4",
    "R5,R6,R7": "non_trap_gaming_only",
}

CASE_MAPPING: Dict[str, str] = {
    "trap_java_to_swe": "trap_after_R1_R2_R3_R4",
    "non_trap_gaming_only": "non_trap_gaming_only",
}
