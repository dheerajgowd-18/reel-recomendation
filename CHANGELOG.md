# Changelog

## [0.2.0] - Phase 1 (End-to-End Stub Pipeline)
### Added
- Added `non_trap_gaming_only` expected output checkpoint fixture to `data/expected_outputs.json`.
- `src/config.py` with system paths, contract constraints, and deterministic mapping rules.
- `src/loaders.py` providing robust JSON loaders and error handling for data contracts.
- `src/formatter.py` providing strict validator and exact plain-text block formatter without LLM variability.
- `src/stub_pipeline.py` implementing modular stages (`normalize_input`, `resolve_expected_key`, `infer_interest_stub`, `recommend_stub`, `build_trace`).
- `src/run.py` CLI runner supporting `--reels`, `--case`, `--out`, and `--trace`.
- Structured JSON execution trace output (`output/trace.json`) and formatted output block (`output/result.txt`).
- `tests/test_phase1_stub.py` unit test suite with 10 test cases verifying mappings, validation bounds, error handling, and non-trap isolation.
- Updated `README.md` with Phase 1 usage and execution instructions.

### Changed
- Updated `tools/validate_data.py` to validate all expected output entries and full 10-node gaming branch while maintaining 28 passing checks.

### Fixed
- Fixed CLI input normalization to handle whitespace and properly validate reel IDs.

### Risks / Notes
- Phase 1 is a deterministic plumbing verification step; real signal extraction and identity graph traversal will be implemented in Phase 2 and Phase 3.

## [0.1.0] - Phase 0.1 (Data Contract Hardening)
### Added
- `"score_type": "reference_only"` attribute to all candidate records in `data/tech_reels.json`.
- Gaming-adjacent candidates and checkpoint recommendation candidates in `data/tech_reels.json`.
- Cumulative multi-step checkpoints (`trap_after_R1` through `trap_after_R1_R2_R3_R4`) in `data/expected_outputs.json`.
- Gaming-only false-positive test case `non_trap_gaming_only` in `data/trap_regression.json`.
- Gaming domain knowledge graph branch in `data/identity_graph.json`.
- Extended validation suite in `tools/validate_data.py` (28 checks).

## [0.0.1] - Phase 0
### Added
- Initial repository setup, baseline data fixtures, graph schemas, and validation suite.
