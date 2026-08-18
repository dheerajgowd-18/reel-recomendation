# Changelog

## [0.6.0] - Phase 5 (Safety/Quality/Hype Gate)
### Added
- `src/gate.py` implementing deterministic live evaluation of candidate safety, concept anchor substance ($S_{\text{concept}}$), depth, and hype pattern penalties ($P_{\text{hype}}$).
- `HARD_DENYLIST_PATTERNS`, `HYPE_PATTERNS`, and `CONCEPT_ANCHORS` in `src/config.py`.
- Borderline candidate `T97` ("10 AI tools worth learning") in `data/tech_reels.json` to prove the gate preserves high-concept educational listicles.
- Gate cache management (`cache/gate_results.json`) with version-aware invalidation and force refresh.
- Gate CLI supporting `--reels`, `--case`, `--all-checkpoints`, and `--out` writing to `output/gate.json`.
- `tools/validate_gate.py` validator script (18 checks) verifying anti-hype rejection of `T99`, acceptance of `T1`, `T24`, `T97`, and offline execution.
- `tests/test_phase5_gate.py` unit test suite with 15 test cases (bringing total suite to 64 tests).
- `prompts/concept_anchor.md` technical specification and prompt guidance.
- Updated `README.md` with Phase 5 instructions.

### Changed
- Configured versioning constant `GATE_VERSION = "v1"`.

### Risks / Notes
- Phase 5 filters the shortlisted candidates and flags rejected items. Final scoring, reranking, and explainable output assembly will be finalized in Phase 6.

## [0.5.0] - Phase 4 (Candidate Retrieval)
### Added
- `CONCEPT_ALIAS_MAP` in `src/config.py` unifying synonyms.
- `src/retrieve.py` implementing dual-source candidate retrieval.
- Retrieval CLI supporting `--reels`, `--case`, `--all-checkpoints`, and `--out`.
- `tools/validate_retrieval.py` validating 18 retrieval rules.
- `tests/test_phase4_retrieval.py` unit test suite (15 tests).

## [0.4.0] - Phase 3 (InterestState Aggregation & Graph Traversal)
### Added
- `tools/check_json_hygiene.py` verifying zero whitespace corruption.
- `src/persona.py` implementing multi-reel evidence synthesis into `InterestState`.
- `src/graph.py` implementing seed selection and one-hop deterministic traversal.
- `src/infer.py` coordinating inference, confidence bucketing, and explainable labels.
- `tools/validate_inference.py` validating 14 inference contract rules.
- `tests/test_phase3_inference.py` with 12 unit tests.

## [0.3.0] - Phase 2 (Signal Extraction Module)
### Added
- Structured `ReelSignal` specification in `src/config.py`.
- `src/signals.py` deterministic signal extraction engine and cache manager.
- `tools/validate_signals.py` validator script (18 checks).
- `tests/test_phase2_signals.py` unit test suite (12 tests).

## [0.2.0] - Phase 1 (End-to-End Stub Pipeline)
### Added
- `src/config.py`, `src/loaders.py`, `src/formatter.py`, `src/stub_pipeline.py`, `src/run.py`.
- `tests/test_phase1_stub.py` unit test suite (10 tests).

## [0.1.0] - Phase 0.1 (Data Contract Hardening)
### Added
- Reference-only candidate score tags, cumulative checkpoints, and 28-check validation suite.

## [0.0.1] - Phase 0
### Added
- Initial repository setup, baseline data fixtures, graph schemas, and validation suite.
