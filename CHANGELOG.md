# Changelog

## [0.5.0] - Phase 4 (Candidate Retrieval)
### Added
- `CONCEPT_ALIAS_MAP` in `src/config.py` unifying synonyms across candidate tags, graph nodes, and domain signals.
- `src/retrieve.py` implementing dual-source candidate retrieval:
  - Source A: Topical matching from `InterestState.domains` and `InterestState.goals`.
  - Source B: Identity-adjacent graph matching from `InferenceResult.graph_traversal.activated_nodes`.
  - Weighted retrieval scoring (`0.45 * topical + 0.55 * identity_adjacent`) prioritizing identity over literal keyword matches.
- Retrieval CLI supporting `--reels`, `--case`, `--all-checkpoints`, and `--out` writing to `output/retrieval.json`.
- `tools/validate_retrieval.py` validating 18 retrieval rules including T1 retrieval, Career inclusion, and gaming isolation.
- `tests/test_phase4_retrieval.py` unit test suite with 15 test cases (bringing total suite to 49 unit tests).
- Updated `README.md` with Phase 4 retrieval execution details.

### Changed
- Enriched concept tags in `data/tech_reels.json` for key candidate benchmark reels (T1, T5, T22, T23, T24, T25, T26) to enable natural discovery while maintaining `score_type: "reference_only"`.

### Fixed
- Verified `case_name` validation in `src/infer.py` and `src/retrieve.py` raises standard `ValueError` for unknown named cases.

### Risks / Notes
- Phase 4 generates the un-gated candidate shortlist. Quality/anti-hype filtering, ranking, and explanation generation will be implemented in subsequent phases.

## [0.4.0] - Phase 3 (InterestState Aggregation & Graph Traversal)
### Added
- `tools/check_json_hygiene.py` verifying zero whitespace corruption across all data, cache, and output JSON artifacts.
- `src/persona.py` implementing multi-reel evidence synthesis into structured `InterestState`.
- `src/graph.py` implementing seed selection and one-hop deterministic activation scoring over `data/identity_graph.json`.
- `src/infer.py` coordinating inference, non-decreasing confidence bucketing, explainable label synthesis, and CLI runner.
- `tools/validate_inference.py` validating 14 inference contract rules.
- `tests/test_phase3_inference.py` with 12 unit tests.

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
