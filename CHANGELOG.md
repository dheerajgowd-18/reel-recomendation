# Changelog

## [0.3.0] - Phase 2 (Signal Extraction Module)
### Added
- Structured `ReelSignal` specification and validation schema in `src/config.py` with 8 evidence categories (`topic_exposure`, `domain_signal`, `professional_identity_signal`, `career_stage_signal`, `goal_signal`, `skill_signal`, `tooling_signal`, `content_preference_signal`).
- `src/signals.py` implementing deterministic feature extraction from reel titles, captions, hashtags, content types, and engagements.
- Local signal cache management (`cache/signals.json`) with version-aware cache invalidation and force refresh.
- Signal CLI runner supporting `--all`, `--reel`, `--reels`, and `--refresh` options with JSON formatting.
- `tools/validate_signals.py` validator script verifying 18 critical signal integrity, evidence bounds, and anti-leakage constraints.
- `tests/test_phase2_signals.py` unit test suite with 12 comprehensive test cases (expanding total test count to 22 tests).
- Updated `prompts/signal_extraction.md` prompt documentation.
- Updated `README.md` with Phase 2 documentation and execution commands.

### Changed
- Configured versioning constants `SIGNAL_VERSION = "v1"`, `ONTOLOGY_VERSION = "graph-v1"`, and `MODEL_VERSION = "deterministic-rules-v1"`.

### Fixed
- Verified `output/trace.json` formatting is clean and devoid of key/value whitespace padding.

### Risks / Notes
- Phase 2 extracts standalone per-reel evidence. Multi-reel evidence synthesis and graph traversal to infer `InterestState` will occur in Phase 3.

## [0.2.0] - Phase 1 (End-to-End Stub Pipeline)
### Added
- Added `non_trap_gaming_only` expected output checkpoint fixture to `data/expected_outputs.json`.
- `src/config.py`, `src/loaders.py`, `src/formatter.py`, `src/stub_pipeline.py`, `src/run.py`.
- Structured JSON execution trace output (`output/trace.json`) and formatted output block (`output/result.txt`).
- `tests/test_phase1_stub.py` unit test suite with 10 test cases.

## [0.1.0] - Phase 0.1 (Data Contract Hardening)
### Added
- `"score_type": "reference_only"` attribute in `data/tech_reels.json`.
- Gaming-adjacent and checkpoint recommendation candidates.
- Multi-step cumulative checkpoints in `data/expected_outputs.json`.
- Gaming false-positive test case in `data/trap_regression.json`.
- Gaming domain knowledge graph branch in `data/identity_graph.json`.
- Extended validation suite in `tools/validate_data.py` (28 checks).

## [0.0.1] - Phase 0
### Added
- Initial repository setup, baseline data fixtures, graph schemas, and validation suite.
