# Changelog

## [0.4.0] - Phase 3 (InterestState Aggregation & Graph Traversal)
### Added
- `tools/check_json_hygiene.py` verifying zero whitespace corruption across all data, cache, and output JSON artifacts.
- `src/persona.py` implementing multi-reel evidence synthesis into structured `InterestState` (identity, career stage, domain, goal, depth, preferences).
- `src/graph.py` implementing seed selection and one-hop deterministic activation scoring over `data/identity_graph.json`.
- `src/infer.py` coordinating inference, non-decreasing confidence bucketing, explainable label synthesis, and CLI runner (`--reels`, `--case`, `--all-checkpoints`, `--out`).
- `tools/validate_inference.py` validating 14 inference contract rules, state schema compliance, and anti-leakage constraints.
- `tests/test_phase3_inference.py` with 12 unit tests (bringing test suite to 34 tests total).
- Updated `README.md` with Phase 3 instructions.

### Changed
- Configured default inference output path to `output/inference.json`.

### Fixed
- Ensured `tools/validate_inference.py` includes project root in `sys.path` for standalone invocation.

### Risks / Notes
- Phase 3 produces internal inference states and graph activations. Candidate catalog retrieval, anti-hype gating, ranking, and explanation formatting will be connected in subsequent phases.

## [0.3.0] - Phase 2 (Signal Extraction Module)
### Added
- Structured `ReelSignal` specification and validation schema in `src/config.py`.
- `src/signals.py` deterministic signal extraction engine and cache manager.
- `tools/validate_signals.py` validator script (18 checks).
- `tests/test_phase2_signals.py` unit test suite (12 tests).
- Updated `prompts/signal_extraction.md` prompt documentation.

## [0.2.0] - Phase 1 (End-to-End Stub Pipeline)
### Added
- `src/config.py`, `src/loaders.py`, `src/formatter.py`, `src/stub_pipeline.py`, `src/run.py`.
- Structured JSON execution trace output (`output/trace.json`) and formatted output block (`output/result.txt`).
- `tests/test_phase1_stub.py` unit test suite (10 tests).

## [0.1.0] - Phase 0.1 (Data Contract Hardening)
### Added
- Reference-only candidate score tags, cumulative checkpoints, gaming domain branch, and 28-check validation suite.

## [0.0.1] - Phase 0
### Added
- Initial repository setup, baseline data fixtures, graph schemas, and validation suite.
