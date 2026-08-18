# Changelog

## [0.1.0] - Phase 0.1 (Data Contract Hardening)
### Added
- `"score_type": "reference_only"` attribute to all candidate records in `data/tech_reels.json` to clearly demarcate reference benchmark values from runtime gate evaluation.
- Gaming-adjacent candidates in `data/tech_reels.json` (`How game AI decides enemy behavior`, `What a game engine actually does`, `Gaming laptop specs that actually matter`).
- Checkpoint recommendation candidates in `data/tech_reels.json` (`Beginner programming concepts explained with memes`, `What software engineers actually do all day`).
- Cumulative multi-step checkpoints (`trap_after_R1`, `trap_after_R1_R2`, `trap_after_R1_R2_R3`, `trap_after_R1_R2_R3_R4`) with non-decreasing confidence progression in `data/expected_outputs.json`.
- Gaming-only false-positive test case `non_trap_gaming_only` with strict exclusion constraints in `data/trap_regression.json`.
- Gaming domain knowledge graph branch in `data/identity_graph.json` with 10 new nodes and 9 directed relational edges.
- Extended validation suite in `tools/validate_data.py` expanding contract tests from 17 to 28 checks.

### Changed
- Replaced non-trap watched reels `R5`, `R6`, and `R7` in `data/watched_reels.json` with gaming-only content completely free of software engineering signals.
- Standardized `data/trap_regression.json` to multi-case `cases` array schema.

### Fixed
- Prevented potential live-gate overfitting by explicitly tagging static dataset candidate scores as reference-only.

### Risks / Notes
- All 28 contract checks pass deterministically without network dependencies.

## [0.0.1] - Phase 0
### Added
- Initial repository setup, baseline data fixtures, graph schemas, and validation suite.
