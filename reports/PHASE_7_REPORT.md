PHASE: 7
STATUS: COMPLETE

SUMMARY:
Implemented the judge-facing demonstration layer, naive baselines, demo traces, markdown report, and offline HTML presentation harness for ScrollSense. Preflight gates verified clean git status, zero whitespace corruption, and zero test regressions across all previous phases. Added naive candidate `T96` ("Learn Java in 60 seconds") in `data/tech_reels.json`. Implemented `src/baselines.py` with `topic_only` and `keyword_similarity` models that visibly fail the trap by overfitting to surface Java signals. Implemented `src/demo.py` generating `output/demo_trace.json`, `output/demo_report.md` (containing the exact mandatory pitch line), and `output/demo.html` (3-panel offline presentation). Validated 20 demo checks in `tools/validate_demo.py` and 21 new unit tests in `tests/test_phase7_baselines.py` and `tests/test_phase7_demo.py` (103 total unit tests across suite).

PREFLIGHT RESULTS:
Git status:
Working tree clean and synchronized prior to Phase 7 build.

Recent commits:
758aa54 feat: complete Phase 6 ranking, explanation, and pipeline orchestration
a44655b feat: complete Phase 5 safety/quality/hype gate
56ba503 feat: complete Phase 4 candidate retrieval layer
d57c435 feat: complete Phase 3 InterestState aggregation and graph traversal
a6e585b feat: complete Phase 2 structured signal extraction module

JSON hygiene:
All 11 JSON files in data, cache, and output directories verified clean without leading/trailing whitespace.

FILES CREATED:
- src/baselines.py
- src/demo.py
- tools/validate_demo.py
- tests/test_phase7_baselines.py
- tests/test_phase7_demo.py
- output/demo_trace.json
- output/demo_report.md
- output/demo.html
- reports/PHASE_7_REPORT.md

FILES MODIFIED:
- data/tech_reels.json
- README.md
- PROGRESS.md
- CHANGELOG.md

DATA VALIDATION OUTPUT:
[PASS] Check 01: data/watched_reels.json exists and is valid JSON - Valid JSON
[PASS] Check 02: data/tech_reels.json exists and is valid JSON - Valid JSON
[PASS] Check 03: data/identity_graph.json exists and is valid JSON - Valid JSON
[PASS] Check 04: data/trap_regression.json exists and is valid JSON - Valid JSON
[PASS] Check 05: data/expected_outputs.json exists and is valid JSON - Valid JSON
[PASS] Check 06: watched_reels.json contains between 6 and 8 Reels - Found 7 Reels
[PASS] Check 07: watched_reels.json contains R1, R2, R3, and R4 - Found all: {'R3', 'R2', 'R4', 'R1'}
[PASS] Check 08: tech_reels.json contains at least 25 candidates - Found 33 candidates
[PASS] Check 09: Every candidate has required fields - All required fields present
[PASS] Check 10: Every candidate CATEGORY is valid - All categories valid
[PASS] Check 11: Every candidate DIFFICULTY is valid - All difficulties valid
[PASS] Check 12: Every candidate has non-empty concept_tags - All concept_tags non-empty
[PASS] Check 13: The exact hype candidate T99 exists - T99 exact match found with reference_only score_type
[PASS] Check 14: identity_graph.json contains required nodes - Found all required 10 nodes
[PASS] Check 15: identity_graph.json contains required edges - Found all required 12 edges
[PASS] Check 16: trap_regression.json references R1, R2, R3, and R4 in trap_java_to_swe - References R1, R2, R3, R4
[PASS] Check 17: expected_outputs.json contains valid checkpoints dictionary - Found 5 checkpoints
[PASS] Check 18: Every candidate in tech_reels.json has score_type == 'reference_only' - All candidates have score_type='reference_only'
[PASS] Check 19: data/expected_outputs.json contains the 4 required checkpoints - All 4 required trap checkpoints present
[PASS] Check 20: Each expected output entry contains all required output fields - All output fields present in all 5 entries
[PASS] Check 21: Confidence sequence across checkpoints is non-decreasing - Confidence sequence: ['Low', 'Medium', 'High', 'High']
[PASS] Check 22: Every RECOMMENDED TECH REEL exists as a title in tech_reels.json - All recommended titles found in candidate catalog
[PASS] Check 23: data/trap_regression.json contains cases array with required cases - Found trap_java_to_swe and non_trap_gaming_only
[PASS] Check 24: non_trap_gaming_only references R5, R6, and R7 - References R5, R6, R7
[PASS] Check 25: watched_reels.json contains R5, R6, and R7 - Found R5, R6, R7
[PASS] Check 26: R5, R6, R7 are gaming-related without forbidden software engineering signals - All gaming reels verified clean
[PASS] Check 27: identity_graph.json contains the full gaming branch nodes - Found all 10 gaming nodes
[PASS] Check 28: identity_graph.json contains required gaming edges - Found all 5 gaming edges

==================================================
Validation Summary: 28/28 checks passed.
==================================================

SIGNAL VALIDATION OUTPUT:
[PASS] Check 01: cache/signals.json exists and is valid JSON - Valid JSON
[PASS] Check 02: Every watched reel in watched_reels.json has a signal - Found signals for all 7 reels
[PASS] Check 03: Every signal contains required fields - All required signal fields present
[PASS] Check 04: Every evidence item contains required fields - All evidence fields present
[PASS] Check 05: Every evidence_type is allowed - All evidence_type values valid
[PASS] Check 06: Every strength is between 0.0 and 1.0 - All strength values within [0.0, 1.0]
[PASS] Check 07: R1 contains java topic exposure (strength 0.5-0.8) - Found java topic exposure
[PASS] Check 08: R1 software_engineer professional identity signal strength <= 0.45 - R1 SWE strength: [0.35]
[PASS] Check 09: R2 contains software_engineer professional identity signal >= 0.75 - Found strong software_engineer signal in R2
[PASS] Check 10: R3 contains career_stage_signal candidate >= 0.7 - Found candidate career stage in R3
[PASS] Check 11: R3 contains software_engineer professional identity signal >= 0.6 - Found SWE identity in R3
[PASS] Check 12: R4 contains tooling_signal developer_hardware >= 0.5 - Found developer_hardware tooling signal in R4
[PASS] Check 13: R5 contains gaming domain_signal >= 0.75 - Found gaming domain signal in R5
[PASS] Check 14: R6 contains game_ai skill_signal >= 0.65 - Found game_ai skill signal in R6
[PASS] Check 15: R7 contains gaming_hardware tooling_signal >= 0.65 - Found gaming_hardware tooling signal in R7
[PASS] Check 16: R5, R6, R7 do not contain software_engineer identity > 0.2 - All gaming reels clean of SWE identity
[PASS] Check 17: R5, R6, R7 do not contain career_stage_signal candidate - All gaming reels clean of candidate stage
[PASS] Check 18: R5, R6, R7 do not contain goal_signal career_prep - All gaming reels clean of career_prep goal

==================================================
Signal Validation Summary: 18/18 checks passed.
==================================================

INFERENCE VALIDATION OUTPUT:
[PASS] Check 01: All 5 inference scenarios execute successfully - R1, R1-R2, R1-R3, R1-R4, Gaming
[PASS] Check 02: InterestState contains all required schema keys - Schema verified
[PASS] Check 03: All InterestState weights are between 0.0 and 1.0 - Weights in bounds
[PASS] Check 04: R1 produces Low confidence and weak SWE identity (<= 0.45) - Confidence: Low, SWE: 0.35
[PASS] Check 05: R1+R2 produces Medium confidence and meaningful SWE identity (>= 0.75) - Confidence: Medium, SWE: 0.9
[PASS] Check 06: R1+R2+R3 produces High confidence and candidate career stage (>= 0.70) - Confidence: High, Candidate: 0.85
[PASS] Check 07: Final trap case produces High confidence and SWE identity >= 0.85 - Confidence: High, SWE: 0.95
[PASS] Check 08: Confidence progression is non-decreasing across trap sequence - Sequence: ['Low', 'Medium', 'High', 'High']
[PASS] Check 09: Trap graph traversal activates SWE core competency nodes - Activated: {'career', 'debugging', 'software_engineer', 'git', 'cloud', 'system_design', 'dsa'}
[PASS] Check 10: Gaming non-trap produces Medium confidence and gaming domain >= 0.75 - Confidence: Medium, Gaming: 1.0
[PASS] Check 11: Gaming non-trap contains no SWE identity (>0.2) or candidate career stage - SWE: 0.0, Candidate: 0.0
[PASS] Check 12: Gaming graph traversal activates gaming nodes without SWE activation - Gaming Activated: {'game_development', 'game_ai', 'graphics', 'game_developer'}
[PASS] Check 13: Inferred interest labels conform to domain boundary heuristics - Trap: 'Software engineering culture and early career preparation', Gaming: 'Gaming systems, game AI, and gaming hardware curiosity'
[PASS] Check 14: run_all_checkpoints returns all 5 standard benchmark results - Keys: {'non_trap_gaming_only', 'trap_after_R1_R2_R3', 'trap_after_R1_R2', 'trap_after_R1', 'trap_after_R1_R2_R3_R4'}

==================================================
Inference Validation Summary: 14/14 checks passed.
==================================================

RETRIEVAL VALIDATION OUTPUT:
[PASS] Check 01: All 7 retrieval scenarios run successfully - R1, R1-R2, R1-R3, R1-R4, Gaming, cases
[PASS] Check 02: output/retrieval.json is valid JSON - output/retrieval.json
[PASS] Check 03: Every retrieval result contains required schema fields - All top-level keys present
[PASS] Check 04: Every candidate entry contains all required candidate fields - Candidate schema valid
[PASS] Check 05: Every candidate retrieval_score is between 0.0 and 1.0 - Scores in bounds
[PASS] Check 06: Final trap case retrieves at least 8 candidates - Found 24 candidates
[PASS] Check 07: Final trap case retrieves T1 ('How a junior software engineer ships a small feature') - T1 present: True
[PASS] Check 08: Final trap case top 5 candidates include at least one Career candidate - Top 5 categories: ['Career', 'Career', 'Career', 'Career', 'Career']
[PASS] Check 09: Final trap case top 5 candidates are not all Java candidates - Categories: ['Career', 'Career', 'Career', 'Career', 'Career']
[PASS] Check 10: Final trap case identity_adjacent source contains at least 5 candidates - Found 19 candidates
[PASS] Check 11: T99 is not top-ranked for final trap case - Top candidate: T1
[PASS] Check 12: T99 is not top-ranked for gaming case - Top gaming candidate: T24
[PASS] Check 13: Gaming case retrieves at least 5 candidates - Found 8 candidates
[PASS] Check 14: Gaming case retrieves at least one of T24, T25, T26 - Retrieved gaming targets: {'T25', 'T26', 'T24'}
[PASS] Check 15: Gaming case top 5 candidates do not include T1 - Top 5 gaming IDs: ['T24', 'T18', 'T19', 'T26', 'T25']
[PASS] Check 16: Gaming case top 5 candidates do not include T5 - Top 5 gaming IDs: ['T24', 'T18', 'T19', 'T26', 'T25']
[PASS] Check 17: Gaming case top 5 candidates do not include T23 - Top 5 gaming IDs: ['T24', 'T18', 'T19', 'T26', 'T25']
[PASS] Check 18: Retrieval is strictly deterministic on repeated execution - Deterministic: True

==================================================
Retrieval Validation Summary: 18/18 checks passed.
==================================================

GATE VALIDATION OUTPUT:
[PASS] Check 01: All 7 gate scenarios run successfully - R1, R1-R2, R1-R3, R1-R4, Gaming, cases
[PASS] Check 02: output/gate.json is valid JSON - output/gate.json
[PASS] Check 03: Every gate result contains required top-level schema fields - All top-level keys present
[PASS] Check 04: Every passed candidate entry contains required fields - Passed schema valid
[PASS] Check 05: Every rejected candidate entry contains required fields - Rejected schema valid
[PASS] Check 06: Every gate_result object contains all required fields - GateResult schema valid
[PASS] Check 07: score_source is always 'computed' across all evaluated candidates - No reference scores used
[PASS] Check 08: T99 is rejected in the final trap case - T99 in rejected: True
[PASS] Check 09: T99 is rejected in the gaming case - T99 in gaming rejected: True
[PASS] Check 10: T99 rejection reason explicitly references denylist or hype/anchor - Reason: Hard denylist match: 'get you a job'
[PASS] Check 11: T1 passes the final trap case - T1 in passed: True
[PASS] Check 12: T24 passes the gaming case - T24 in passed: True
[PASS] Check 13: T97 ('10 AI tools worth learning') passes gate if retrieved - T97 not rejected: True
[PASS] Check 14: At least one candidate passes final trap case - Passed count: 20
[PASS] Check 15: At least one candidate passes gaming case - Passed count: 7
[PASS] Check 16: Every rejected candidate has a non-empty rejection_reason - All reasons present
[PASS] Check 17: Gate is strictly deterministic across runs - Deterministic: True
[PASS] Check 18: Gate execution completes offline without network dependencies - Offline execution verified

==================================================
Gate Validation Summary: 18/18 checks passed.
==================================================

PIPELINE VALIDATION OUTPUT:
[PASS] Check 01: Pipeline runs successfully in real mode across all cases - All executions succeeded
[PASS] Check 02: No fallback triggered in real mode validation - Real mode execution verified
[PASS] Check 03: output/result.txt exists and contains formatted output - output/result.txt
[PASS] Check 04: output/pipeline_trace.json exists and is valid JSON - output/pipeline_trace.json
[PASS] Check 05: Every output contains all 8 required contract labels - All fields present
[PASS] Check 06: Every recommended CATEGORY is in allowed set - Categories: ['Other', 'Career', 'Career', 'Career', 'AI']
[PASS] Check 07: Every recommended DIFFICULTY is in allowed set - Difficulties: ['Beginner', 'Beginner', 'Beginner', 'Beginner', 'Beginner']
[PASS] Check 08: Every recommendation CONFIDENCE is in allowed set - Confidences: ['Low', 'Medium', 'High', 'High', 'Medium']
[PASS] Check 09: R1 output recommends T22 ('Beginner programming concepts explained with memes') - Recommended: 'Beginner programming concepts explained with memes'
[PASS] Check 10: R1 confidence is Low - Confidence: Low
[PASS] Check 11: R1+R2 output recommends T23 ('What software engineers actually do all day') - Recommended: 'What software engineers actually do all day'
[PASS] Check 12: R1+R2 confidence is Medium - Confidence: Medium
[PASS] Check 13: R1+R2+R3 output recommends T5 ('What a coding interview is really testing') - Recommended: 'What a coding interview is really testing'
[PASS] Check 14: R1+R2+R3 confidence is High - Confidence: High
[PASS] Check 15: Final trap output recommends T1 ('How a junior software engineer ships a small feature') - Recommended: 'How a junior software engineer ships a small feature'
[PASS] Check 16: Final trap confidence is High - Confidence: High
[PASS] Check 17: Gaming output recommends T24 ('How game AI decides enemy behavior') - Recommended: 'How game AI decides enemy behavior'
[PASS] Check 18: Gaming confidence is Medium - Confidence: Medium
[PASS] Check 19: T99 is never recommended across any pipeline execution - T99 completely absent
[PASS] Check 20: Final trap INTEREST DETECTED contains software engineering wording - Interest: 'Software engineering culture and early career preparation'
[PASS] Check 21: Gaming INTEREST DETECTED contains gaming wording - Interest: 'Gaming systems, game AI, and gaming hardware curiosity'
[PASS] Check 22: Gaming INTEREST DETECTED does not contain software engineering wording - Interest: 'Gaming systems, game AI, and gaming hardware curiosity'
[PASS] Check 23: Final trap output matches expected fields in expected_outputs.json - Exact match on key contract fields
[PASS] Check 24: Gaming output matches expected fields in expected_outputs.json - Exact match on key contract fields
[PASS] Check 25: Pipeline output is strictly deterministic on repeated execution - Deterministic: True

==================================================
Pipeline Validation Summary: 25/25 checks passed.
==================================================

DEMO VALIDATION OUTPUT:
[PASS] Check 01: Demo runs successfully for all cases - Cases: ['trap_after_R1', 'trap_after_R1_R2', 'trap_after_R1_R2_R3', 'trap_java_to_swe', 'non_trap_gaming_only']
[PASS] Check 02: output/demo_trace.json exists and is valid JSON - output/demo_trace.json
[PASS] Check 03: output/demo_report.md exists and contains text - output/demo_report.md
[PASS] Check 04: output/demo.html exists and contains HTML - output/demo.html
[PASS] Check 05: Final trap case includes Baseline 1 (topic_only) - Found: True
[PASS] Check 06: Final trap case includes Baseline 2 (keyword_similarity) - Found: True
[PASS] Check 07: Baseline 1 final trap recommendation is T96 or Java category - Recommended: T96 (Java)
[PASS] Check 08: Baseline 1 final trap recommendation is not T1 - Recommended: T96
[PASS] Check 09: Baseline 2 final trap recommendation is not T1 - Recommended: T96
[PASS] Check 10: ScrollSense final trap recommendation is T1 - Recommended: T1
[PASS] Check 11: ScrollSense final trap confidence is High - Confidence: High
[PASS] Check 12: ScrollSense final trap interest contains software engineering - Interest: 'Software engineering culture and early career preparation'
[PASS] Check 13: ScrollSense final trap trace includes graph activations - Activations count: 7
[PASS] Check 14: ScrollSense final trap trace includes T99 anti-hype rejection - T99 rejected: True
[PASS] Check 15: ScrollSense gaming recommendation is T24 - Recommended: T24
[PASS] Check 16: ScrollSense gaming interest contains gaming wording - Interest: 'Gaming systems, game AI, and gaming hardware curiosity'
[PASS] Check 17: ScrollSense gaming interest does not contain software engineering - Interest: 'Gaming systems, game AI, and gaming hardware curiosity'
[PASS] Check 18: ScrollSense gaming recommendation is not T1, T5, or T23 - Recommended: T24
[PASS] Check 19: Demo report markdown contains exact pitch line - Exact pitch line verified in markdown
[PASS] Check 20: Demo execution is strictly deterministic across runs - Deterministic: True

==================================================
Demo Validation Summary: 20/20 checks passed.
==================================================

TEST OUTPUT:
Ran 103 tests in 4.107s

OK

BASELINE FINAL TRAP SUMMARY:
Baseline 1 (Topic-Only):
- recommended candidate: T96
- title: Learn Java in 60 seconds
- category: Java
- failure mode: Collapses to literal surface topic (Java) from R1 meme instead of inferring software engineering.

Baseline 2 (Keyword-Similarity):
- recommended candidate: T96
- title: Learn Java in 60 seconds
- category: Java
- failure mode: Overfits to superficial keyword frequency without latent identity inference.

SCROLLSENSE FINAL TRAP SUMMARY:
- recommended candidate: T1
- title: How a junior software engineer ships a small feature
- category: Career
- confidence: High
- top identity: software_engineer
- graph activations: ['career', 'git', 'debugging', 'system_design', 'dsa', 'cloud']
- rejected hype candidate: T99 ("10 AI tools that will get you a job", Hard denylist match: 'get you a job')

SCROLLSENSE GAMING SUMMARY:
- recommended candidate: T24
- title: How game AI decides enemy behavior
- category: AI
- confidence: Medium
- top domain: gaming
- false-positive check result: PASS (Zero software-engineering leakage; clean domain boundary isolation maintained)

DEMO REPORT EXCERPT:
## Part 1: The Trap Case (`trap_java_to_swe`)

### 1. Watched Reels Sequence
- **R1**: *When you miss a semicolon in Java after 4 hours of debugging* (Type: `meme`, Topic: `Java`)
- **R2**: *Day in the life of a Junior Software Engineer in Austin* (Type: `lifestyle`, Topic: `Software Engineering`)
- **R3**: *Interviewer: Invert a binary tree on this whiteboard right now* (Type: `humor`, Topic: `Coding Interview`)
- **R4**: *M3 Pro vs ThinkPad X1 Carbon for CS Undergrads & Devs* (Type: `comparison`, Topic: `Developer Hardware`)

### 2. Baseline 1 Failure (Surface Topic-Only)
- **Recommendation**: `T96` — *Learn Java in 60 seconds*
- **Category**: `Java` | **Confidence**: `Low`
- **Failure Mode**: Collapses to literal surface topic (Java) from R1 meme instead of inferring software engineering.

### 3. Baseline 2 Failure (Keyword Token Similarity)
- **Recommendation**: `T96` — *Learn Java in 60 seconds*
- **Category**: `Java` | **Confidence**: `Low`
- **Failure Mode**: Overfits to superficial keyword frequency without latent identity inference.

### 4. ScrollSense Inferred Latent Interest
- **Detected Interest**: Software engineering culture and early career preparation
- **Inferred Identity**: `software_engineer` (Confidence: `High`)
- **Inferred Goals**: `career_prep, career_curiosity`

### 5. Identity Graph Traversal
Activated Competency & Tooling Nodes: `career, git, debugging, system_design, dsa, cloud`

### 6. Anti-Hype Gate Rejections
- **T99** (*10 AI tools that will get you a job*): `Hard denylist match: 'get you a job'`
- **T100** (*Become a software engineer in 30 days*): `Hard denylist match: 'become a software engineer in'`
- **T102** (*Top 5 coding hacks to get hired fast*): `Hard denylist match: 'get hired fast'`
- **T103** (*Guaranteed tech job roadmap*): `Hard denylist match: 'guaranteed job'`

### 7. Final ScrollSense Standard Output
```text
CURRENT REEL: session: R1, R2, R3, R4
INTEREST DETECTED: Software engineering culture and early career preparation
WHY: Java meme shows programming humor; software-engineer lifestyle Reel shows role curiosity; coding interview joke shows career-preparation interest; laptop comparison shows interest in developer tooling.
RECOMMENDED TECH REEL: How a junior software engineer ships a small feature
CATEGORY: Career
WHY THIS RECOMMENDATION: It matches the inferred software-engineering identity and career curiosity, rather than overfitting to the Java keyword from the meme.
DIFFICULTY: Beginner
CONFIDENCE: High
```

### 8. Demo Pitch
> **Judge Pitch Line**:
> This is the trap in the problem statement. A shallow system sees Java and recommends another Java Reel. ScrollSense infers the latent professional identity — software engineering — from heterogeneous signals: a meme, a lifestyle Reel, an interview joke, and a laptop comparison. It then retrieves useful adjacent tech content and explicitly rejects hype like “10 AI tools that will get you a job.”

DEMO HTML CHECK:
- exists: YES (`output/demo.html`)
- offline-safe: YES (Self-contained, inline CSS only, zero external JS)
- no CDN links: YES (Zero external URLs / network requests)

ACCEPTANCE CRITERIA:
- [x] Git clean
- [x] Phase 6 committed
- [x] JSON hygiene passes
- [x] validate_data.py passes
- [x] validate_signals.py passes
- [x] validate_inference.py passes
- [x] validate_retrieval.py passes
- [x] validate_gate.py passes
- [x] validate_pipeline.py passes
- [x] validate_demo.py passes
- [x] unittest passes
- [x] Baseline 1 fails trap
- [x] Baseline 2 fails trap
- [x] ScrollSense recommends T1
- [x] ScrollSense recommends T24 for gaming
- [x] T99 rejection visible
- [x] demo report contains pitch line
- [x] demo HTML offline-safe
- [x] demo deterministic
- [x] README updated
- [x] PROGRESS.md updated
- [x] CHANGELOG.md updated

BLOCKERS:
- None

ASSUMPTIONS MADE:
- Phase 7 creates a judge-facing comparison harness and offline dashboard without modifying the underlying deterministic pipeline recommendation logic.

NEXT PHASE RECOMMENDATION:
Phase 8 — Hardening, offline demo freeze, and final audit

PROGRESS.md UPDATED: YES
CHANGELOG.md UPDATED: YES
