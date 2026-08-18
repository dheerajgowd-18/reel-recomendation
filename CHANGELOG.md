# Changelog

## [0.7.0] - Phase 6 (Ranking, Explanation, and Exact Output Generation)
### Added
- `src/rank.py` implementing deterministic candidate ranking using heuristic weights (`HEURISTIC_WEIGHTS_V1`), graph fit, goal-stage fit, difficulty alignment, career relevance, and overgeneralization penalties.
- `src/explain.py` generating deterministic, structured `INTEREST DETECTED`, `WHY`, and `WHY THIS RECOMMENDATION` fields synthesizing multi-reel evidence.
- `src/pipeline.py` orchestrating end-to-end pipeline execution with `real`, `stub`, and `auto` fallback modes.
- `output/pipeline_trace.json` recording structured execution trace from inference, retrieval, gating, ranking, and explanation.
- `tools/validate_pipeline.py` validation script with 25 checks verifying exact output contract compliance, checkpoint targets, and offline execution.
- `tests/test_phase6_pipeline.py` unit test suite with 18 tests (expanding total suite to 82 tests).
- Updated `src/run.py` CLI supporting `--mode real|stub|auto` and `--all-checkpoints`.
- Enriched stage-fit tags in `data/tech_reels.json` for candidates T1, T4, T5, T7, T8, T22, T23, T24, T25, T26.

### Changed
- Configured versioning constants `RANKING_VERSION = "v1"` and `WEIGHTS_VERSION = "HEURISTIC_WEIGHTS_V1"`.
- Set default execution mode in CLI to `auto` while supporting explicit `real` and `stub` paths.

## [0.6.0] - Phase 5 (Safety/Quality/Hype Gate)
### Added
- `src/gate.py` implementing deterministic live evaluation of candidate safety, concept anchor substance, depth, and hype pattern penalties.
- `HARD_DENYLIST_PATTERNS`, `HYPE_PATTERNS`, and `CONCEPT_ANCHORS` in `src/config.py`.
- Candidate `T97` in `data/tech_reels.json`.
- Gate cache management (`cache/gate_results.json`).
- Gate CLI and `tools/validate_gate.py` (18 checks).
- `tests/test_phase5_gate.py` unit test suite (15 tests).

## [0.5.0] - Phase 4 (Candidate Retrieval)
### Added
- `CONCEPT_ALIAS_MAP` in `src/config.py`.
- `src/retrieve.py` implementing dual-source candidate retrieval.
- Retrieval CLI and `tools/validate_retrieval.py` (18 checks).
- `tests/test_phase4_retrieval.py` unit test suite (15 tests).

## [0.4.0] - Phase 3 (InterestState Aggregation & Graph Traversal)
### Added
- `tools/check_json_hygiene.py` verifying zero whitespace corruption.
- `src/persona.py` synthesizing multi-reel evidence into `InterestState`.
- `src/graph.py` implementing seed selection and one-hop traversal.
- `src/infer.py` coordinating inference and explainable labels.
- `tools/validate_inference.py` (14 checks).
- `tests/test_phase3_inference.py` (12 tests).

## [0.3.0] - Phase 2 (Signal Extraction Module)
### Added
- Structured `ReelSignal` specification in `src/config.py`.
- `src/signals.py` deterministic signal extraction engine and cache.
- `tools/validate_signals.py` (18 checks).
- `tests/test_phase2_signals.py` (12 tests).

## [0.2.0] - Phase 1 (End-to-End Stub Pipeline)
### Added
- `src/config.py`, `src/loaders.py`, `src/formatter.py`, `src/stub_pipeline.py`, `src/run.py`.
- `tests/test_phase1_stub.py` (10 tests).

## [0.1.0] - Phase 0.1 (Data Contract Hardening)
### Added
- Reference-only candidate score tags, cumulative checkpoints, and 28-check validation suite.

## [0.0.1] - Phase 0
### Added
- Initial repository setup, baseline data fixtures, graph schemas, and validation suite.
