# Changelog

## [1.3.0] - Phase 9C (Platform Scoring Optimization & Hard Freeze)
### Added
- Pytest-native test suite `tests/test_contract_pytest.py` with parametrized contract regression tests.
- `requirements-dev.txt` pinning pytest, pytest-cov, and ruff.
- `pytest.ini` and `ruff.toml` configurations.
- `SECURITY.md` detailing defense-in-depth architecture, zero-secrets policy, and HTTP security headers.
- Security response headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`) and strict Pydantic HTTP 422 input validation in `ui/server.py`.
- WCAG AA accessibility improvements: skip-to-content links, `role="alert"`, `aria-live="polite"`, `:focus-visible` styling, and explicit text badges.
- `SUBMISSION.md` comprehensive hackathon submission briefing.
- `reports/PHASE_9C_REPORT.md` and `reports/FINAL_FREEZE_REPORT.md`.

## [1.2.0] - Phase 9B (Live Demo UI for ScrollSense)
### Added
- `ui/server.py` FastAPI local live demo server running on port 8000.
- `ui/static/index.html`, `ui/static/styles.css`, `ui/static/app.js` projector-optimized interactive UI dashboard.
- REST API endpoints: `GET /api/health`, `GET /api/cases`, `POST /api/run`, `GET /api/cached-demo`.
- AI/Nemotron status panel and emergency demo fallback button.
- `requirements-ui.txt` with UI dependencies.
- `tools/validate_ui.py` automated validator (23 checks).
- `tests/test_phase9_ui.py` unit test suite.

## [1.1.0] - Phase 9A-NVIDIA (NVIDIA Nemotron Integration)
### Added
- Optional AI layer powered by **NVIDIA Nemotron 3.5 Lightning 30B A3B** (`nvidia/nemotron-3.5-lightning-30b-a3b`).
- `src/llm_client.py` supporting `mock`, `cache`, and `openai_compatible` endpoints with retry logic and JSON fence stripping.
- Structured system prompts: `prompts/nemotron_signal_extraction.md` and `prompts/nemotron_explanation.md`.
- `src/ai_cache.py` managing offline persisted cache files (`cache/llm/signals.json`, `cache/llm/explanations.json`, `cache/llm/concept_anchor.json`).
- `src/ai_signals.py` and `src/ai_explainer.py` implementing hybrid AI extraction/explanation with strict domain boundary checks and deterministic fallback.
- AI telemetry logging in `output/pipeline_trace.json`.
- `tests/test_phase9_nvidia.py` unit test suite.

## [1.0.0] - Phase 8 (Hardening, Offline Demo Freeze, and Final Audit)
### Added
- `run_demo.py` master entrypoint for live judge presentations with baseline comparison, trap escape explanation, and HTML dashboard rendering.
- `tools/final_audit.py` comprehensive audit tool executing all 9 validation and test suites.
- `reports/FINAL_AUDIT_REPORT.md` audit certificate verifying unit tests and 100% offline compliance.
- `docs/LIVE_DEMO_SCRIPT.md` presentation script and judge talk track.
- Final polished `README.md` submission document.

## [0.8.0] - Phase 7 (Baselines, Demo Trace, and Final Presentation Harness)
### Added
- `src/baselines.py` implementing naive `topic_only` and `keyword_similarity` recommenders demonstrating trap failure modes.
- Naive baseline candidate `T96` in `data/tech_reels.json`.
- `src/demo.py` demo harness generating `output/demo_trace.json`, `output/demo_report.md`, and `output/demo.html`.
- `tools/validate_demo.py` validator script with 20 checks.
- `tests/test_phase7_baselines.py` and `tests/test_phase7_demo.py` unit test suites.

## [0.7.0] - Phase 6 (Ranking, Explanation, and Exact Output Generation)
### Added
- `src/rank.py` implementing deterministic candidate ranking using heuristic weights (`HEURISTIC_WEIGHTS_V1`), graph fit, goal-stage fit, difficulty alignment, career relevance, and overgeneralization penalties.
- `src/explain.py` generating deterministic, structured `INTEREST DETECTED`, `WHY`, and `WHY THIS RECOMMENDATION` fields.
- `src/pipeline.py` orchestrating end-to-end pipeline execution with `real`, `stub`, and `auto` fallback modes.
- `output/pipeline_trace.json` recording structured execution trace.
- `tools/validate_pipeline.py` validation script with 25 checks.
- `tests/test_phase6_pipeline.py` unit test suite.

## [0.6.0] - Phase 5 (Safety/Quality/Hype Gate)
### Added
- `src/gate.py` implementing deterministic live evaluation of candidate safety, concept anchor substance, depth, and hype pattern penalties.
- `HARD_DENYLIST_PATTERNS`, `HYPE_PATTERNS`, and `CONCEPT_ANCHORS` in `src/config.py`.
- Candidate `T97` in `data/tech_reels.json`.
- Gate cache management (`cache/gate_results.json`).
- `tools/validate_gate.py` (18 checks) and `tests/test_phase5_gate.py` (15 tests).

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
