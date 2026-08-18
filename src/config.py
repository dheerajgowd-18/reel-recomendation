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
GATE_CACHE_PATH = CACHE_DIR / "gate_results.json"

# Output directory and default files
OUTPUT_DIR = PROJECT_ROOT / "output"
DEFAULT_RESULT_PATH = OUTPUT_DIR / "result.txt"
DEFAULT_TRACE_PATH = OUTPUT_DIR / "trace.json"
DEFAULT_PIPELINE_TRACE_PATH = OUTPUT_DIR / "pipeline_trace.json"

# Versioning metadata
SIGNAL_VERSION = "v1"
ONTOLOGY_VERSION = "graph-v1"
MODEL_VERSION = "deterministic-rules-v1"
GATE_VERSION = "v1"
RANKING_VERSION = "v1"
WEIGHTS_VERSION = "HEURISTIC_WEIGHTS_V1"

# Heuristic weights for Phase 6 ranking (heuristic evidence combination, not learned/tuned)
HEURISTIC_WEIGHTS_V1: Dict[str, float] = {
    "identity_graph_fit": 0.26,
    "goal_stage_fit": 0.22,
    "difficulty_match": 0.16,
    "career_relevance": 0.14,
    "quality_score": 0.10,
    "retrieval_score": 0.08,
    "novelty": 0.04,
    "hype_penalty": -0.15,
    "overgeneralization_penalty": -0.20,
}

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

# Deterministic concept and node alias mapping for retrieval
CONCEPT_ALIAS_MAP: Dict[str, str] = {
    "software engineering": "software_engineering",
    "software_engineering": "software_engineering",
    "developer workflow": "software_engineering",
    "developer_workflow": "software_engineering",
    "developer_skills": "software_engineering",
    "engineering_culture": "software_engineering",
    "work_culture": "software_engineering",
    "workflow": "software_engineering",
    "teamwork": "career",
    "collaboration": "career",
    "career": "career",
    "tech career": "career",
    "tech_career": "career",
    "career_insights": "career",
    "day_in_life": "software_engineering",
    "code review": "code_review",
    "code_review": "code_review",
    "debugging": "debugging",
    "breakpoints": "debugging",
    "stack_traces": "debugging",
    "git": "git",
    "branching": "git",
    "version_control": "git",
    "merge_conflicts": "git",
    "system design": "system_design",
    "system_design": "system_design",
    "scalability": "system_design",
    "architecture": "system_design",
    "load_balancer": "system_design",
    "caching": "system_design",
    "databases": "system_design",
    "database_indexing": "system_design",
    "b_tree": "system_design",
    "sql": "system_design",
    "rest_api": "system_design",
    "backend": "system_design",
    "dsa": "dsa",
    "algorithms": "dsa",
    "interview preparation": "dsa",
    "interview_prep": "dsa",
    "coding interview": "dsa",
    "coding_interview": "dsa",
    "problem_solving": "dsa",
    "binary_tree": "dsa",
    "binary_search": "dsa",
    "two_pointer": "dsa",
    "cloud": "cloud",
    "devops": "cloud",
    "ci_cd": "cloud",
    "deployment": "cloud",
    "github_actions": "cloud",
    "aws": "cloud",
    "serverless": "cloud",
    "infrastructure": "cloud",
    "java": "java",
    "jvm": "java",
    "hashmap": "java",
    "garbage_collection": "java",
    "programming humor": "programming_humor",
    "programming_humor": "programming_humor",
    "programming_basics": "programming_humor",
    "humor": "programming_humor",
    "gaming": "gaming",
    "esports": "gaming",
    "competitive_gameplay": "gaming",
    "gameplay": "gaming",
    "fps": "gaming",
    "game ai": "game_ai",
    "game_ai": "game_ai",
    "behavior trees": "game_ai",
    "pathfinding": "game_ai",
    "enemy_behavior": "game_ai",
    "game engine": "game_development",
    "game_engine": "game_development",
    "game development": "game_development",
    "game_development": "game_development",
    "game loop": "game_development",
    "graphics": "graphics",
    "rendering": "graphics",
    "gpu": "gaming_hardware",
    "gaming laptop": "gaming_hardware",
    "gaming_hardware": "gaming_hardware",
    "hardware": "hardware",
    "chips": "hardware",
    "cpu": "gaming_hardware",
    "thermals": "gaming_hardware",
    "refresh rate": "gaming_hardware",
    "arm": "hardware",
    "x86": "hardware",
    "instruction_set": "hardware",
    "cpu_cache": "hardware",
    "hardware_design": "hardware",
    "ai": "ai",
    "transformers": "ai",
    "self_attention": "ai",
    "deep_learning": "ai",
    "ai tools": "ai",
    "practical_project": "software_engineering",
    "first_feature": "software_engineering",
    "codebase_reading": "software_engineering",
    "candidate_readiness": "dsa",
    "beginner_theory": "system_design",
    "practical_skill": "debugging",
    "meme_learning": "programming_humor",
    "role_overview": "career",
    "gaming_specific": "gaming",
    "docker": "cloud",
    "kubernetes": "cloud",
    "rag": "ai",
    "vector databases": "ai",
    "vector_databases": "ai",
    "hype": "hype",
    "bootcamp": "career",
    "guaranteed_job": "career",
    "recruiting_hacks": "career",
    "coding_hacks": "career",
    "shortcuts": "career",
    "linux": "developer_workflow",
    "bash": "developer_workflow",
    "cli_tools": "developer_workflow",
    "auth": "cybersecurity",
    "jwt": "cybersecurity",
    "security_headers": "cybersecurity",
    "web_security": "cybersecurity",
    "sql_injection": "cybersecurity",
    "appsec": "cybersecurity",
    "owasp": "cybersecurity",
}

# Hard Denylist Patterns (case-insensitive substring match)
HARD_DENYLIST_PATTERNS: List[str] = [
    "get you a job",
    "will get you a job",
    "guaranteed job",
    "become a developer in",
    "become a software engineer in",
    "secret tools",
    "no one tells you",
    "make money fast",
    "six figures",
    "without coding",
    "hack your career",
    "get hired fast",
    "recruiting hacks",
    "ai secrets",
    "interview cheats",
    "get_rich",
    "guaranteed_job",
]

# Soft Hype Patterns for pattern penalty scoring
HYPE_PATTERNS: List[str] = [
    "10",
    "5",
    "top",
    "tools",
    "hacks",
    "tips",
    "tricks",
    "secrets",
    "ways",
    "fast",
    "instantly",
    "guaranteed",
    "roadmap",
    "get hired",
    "job",
    "career hacks",
    "speedrun",
    "get rich",
    "cheat",
    "hype",
]

# Concrete Technical Concept Anchors for quality scoring
CONCEPT_ANCHORS: Set[str] = {
    "git",
    "github",
    "http",
    "api",
    "rest api",
    "rest_api",
    "debugging",
    "code review",
    "code_review",
    "binary tree",
    "binary_tree",
    "dsa",
    "system design",
    "system_design",
    "cloud",
    "docker",
    "kubernetes",
    "rag",
    "vector databases",
    "vector_databases",
    "gpu",
    "cpu",
    "cache hierarchy",
    "cpu_cache",
    "arm",
    "x86",
    "game engine",
    "game_engine",
    "game development",
    "game_development",
    "rendering",
    "graphics",
    "behavior trees",
    "pathfinding",
    "game loop",
    "game_loop",
    "linux",
    "bash",
    "sql",
    "testing",
    "compiler",
    "memory_locality",
    "hashmap",
    "jvm",
    "garbage_collection",
    "binary_search",
    "two_pointer",
    "auth",
    "jwt",
    "owasp",
    "sql_injection",
    "software_engineering",
    "developer_workflow",
    "algorithms",
    "load_balancer",
    "caching",
    "databases",
    "database_indexing",
    "b_tree",
    "transformers",
    "self_attention",
    "deep_learning",
    "game_ai",
}
