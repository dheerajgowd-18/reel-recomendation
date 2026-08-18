# ScrollSense Repository Audit — Phase 0 / Phase 0.1 Verification

**Audit Timestamp**: 2026-08-18T10:43:00+05:30  
**Repository**: `https://github.com/dheerajgowd-18/reel-recomendation`  
**Current Phase**: Phase 0.1 (Data Contract Hardening)

---

## 1. GIT STATUS

```text
WORKING TREE CLEAN
```

---

## 2. GIT LOG

```text
ece209a feat: complete Phase 0 and Phase 0.1 data contracts and validation
 .env.example                 |   5 +
 .gitignore                   |  24 +++
 CHANGELOG.md                 |  25 +++
 PROGRESS.md                  |  37 ++++
 README.md                    |  29 +++
 cache/.gitkeep               |   1 +
 data/expected_outputs.json   |  42 +++++
 data/identity_graph.json     | 225 ++++++++++++++++++++++
 data/tech_reels.json         | 343 +++++++++++++++++++++++++++++++++
 data/trap_regression.json    |  69 +++++++
 data/watched_reels.json      |  58 ++++++
 output/.gitkeep              |   1 +
 prompts/concept_anchor.md    |   7 +
 prompts/signal_extraction.md |  10 +
 reports/PHASE_0_1_REPORT.md  |  80 ++++++++
 reports/PHASE_0_REPORT.md    |  76 ++++++++
 requirements.txt             |   3 +
 src/__init__.py              |   1 +
 tests/__init__.py            |   1 +
 tools/validate_data.py       | 440 +++++++++++++++++++++++++++++++++++++++++++
 20 files changed, 1477 insertions(+)
```

---

## 3. FILE TREE

```text
.
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── PROGRESS.md
├── README.md
├── requirements.txt
├── cache/
│   └── .gitkeep
├── data/
│   ├── expected_outputs.json
│   ├── identity_graph.json
│   ├── tech_reels.json
│   ├── trap_regression.json
│   └── watched_reels.json
├── output/
│   └── .gitkeep
├── prompts/
│   ├── concept_anchor.md
│   └── signal_extraction.md
├── reports/
│   ├── AUDIT_REPORT.md
│   ├── PHASE_0_1_REPORT.md
│   └── PHASE_0_REPORT.md
├── src/
│   └── __init__.py
├── tests/
│   └── __init__.py
└── tools/
    └── validate_data.py
```

---

## 4. VALIDATION OUTPUT

```text
[PASS] Check 01: data/watched_reels.json exists and is valid JSON - Valid JSON
[PASS] Check 02: data/tech_reels.json exists and is valid JSON - Valid JSON
[PASS] Check 03: data/identity_graph.json exists and is valid JSON - Valid JSON
[PASS] Check 04: data/trap_regression.json exists and is valid JSON - Valid JSON
[PASS] Check 05: data/expected_outputs.json exists and is valid JSON - Valid JSON
[PASS] Check 06: watched_reels.json contains between 6 and 8 Reels - Found 7 Reels
[PASS] Check 07: watched_reels.json contains R1, R2, R3, and R4 - Found all: {'R4', 'R3', 'R2', 'R1'}
[PASS] Check 08: tech_reels.json contains at least 25 candidates - Found 31 candidates
[PASS] Check 09: Every candidate has required fields - All required fields present
[PASS] Check 10: Every candidate CATEGORY is valid - All categories valid
[PASS] Check 11: Every candidate DIFFICULTY is valid - All difficulties valid
[PASS] Check 12: Every candidate has non-empty concept_tags - All concept_tags non-empty
[PASS] Check 13: The exact hype candidate T99 exists - T99 exact match found with reference_only score_type
[PASS] Check 14: identity_graph.json contains required nodes - Found all required 10 nodes
[PASS] Check 15: identity_graph.json contains required edges - Found all required 12 edges
[PASS] Check 16: trap_regression.json references R1, R2, R3, and R4 in trap_java_to_swe - References R1, R2, R3, R4
[PASS] Check 17: expected_outputs.json contains valid checkpoints dictionary - Found 4 checkpoints
[PASS] Check 18: Every candidate in tech_reels.json has score_type == 'reference_only' - All candidates have score_type='reference_only'
[PASS] Check 19: data/expected_outputs.json contains the 4 required checkpoints - All 4 checkpoints present
[PASS] Check 20: Each expected output entry contains all required output fields - All output fields present in all checkpoints
[PASS] Check 21: Confidence sequence across checkpoints is non-decreasing - Confidence sequence: ['Low', 'Medium', 'High', 'High']
[PASS] Check 22: Every RECOMMENDED TECH REEL exists as a title in tech_reels.json - All recommended titles found in candidate catalog
[PASS] Check 23: data/trap_regression.json contains cases array with required cases - Found trap_java_to_swe and non_trap_gaming_only
[PASS] Check 24: non_trap_gaming_only references R5, R6, and R7 - References R5, R6, R7
[PASS] Check 25: watched_reels.json contains R5, R6, and R7 - Found R5, R6, R7
[PASS] Check 26: R5, R6, R7 are gaming-related without forbidden software engineering signals - All gaming reels verified clean
[PASS] Check 27: identity_graph.json contains the gaming branch nodes - Found all 5 gaming nodes
[PASS] Check 28: identity_graph.json contains required gaming edges - Found all 5 gaming edges

==================================================
Validation Summary: 28/28 checks passed.
==================================================
```

---

## 5. DATA CONTRACT SUMMARY

### A. `data/watched_reels.json`
- **Total number of watched reels**: 7
- **All reel_ids**: `["R1", "R2", "R3", "R4", "R5", "R6", "R7"]`
- **Individual Reel Details**:
  - `R1`:
    - **Title**: "When you miss a semicolon in Java after 4 hours of debugging"
    - **Content Type**: `meme`
    - **First 3 Hashtags**: `["javamemes", "codinghumor", "programmerlife"]`
  - `R2`:
    - **Title**: "Day in the life of a Junior Software Engineer in Austin"
    - **Content Type**: `lifestyle`
    - **First 3 Hashtags**: `["swe", "dayinthelife", "techcareer"]`
  - `R3`:
    - **Title**: "Interviewer: Invert a binary tree on this whiteboard right now"
    - **Content Type**: `humor`
    - **First 3 Hashtags**: `["leetcode", "codinginterview", "techhumor"]`
  - `R4`:
    - **Title**: "M3 Pro vs ThinkPad X1 Carbon for CS Undergrads & Devs"
    - **Content Type**: `comparison`
    - **First 3 Hashtags**: `["laptops", "devsetup", "programming"]`
  - `R5`:
    - **Title**: "Insane 1v5 clutch in ranked"
    - **Content Type**: `gaming`
    - **First 3 Hashtags**: `["gaming", "esports", "gameplay"]`
  - `R6`:
    - **Title**: "How game AI predicts your next move"
    - **Content Type**: `news`
    - **First 3 Hashtags**: `["gaming", "gameai", "ai"]`
  - `R7`:
    - **Title**: "Best gaming laptop specs explained"
    - **Content Type**: `comparison`
    - **First 3 Hashtags**: `["gaming", "hardware", "gaminglaptop"]`

### B. `data/tech_reels.json`
- **Total number of candidates**: 31
- **Number of candidates with `score_type == "reference_only"`**: 31
- **Number of candidates missing `score_type`**: 0
- **Whether T99 exists**: YES (`T99` - "10 AI tools that will get you a job")
- **Target Title Verification**:
  - *"Beginner programming concepts explained with memes"*: YES (`T22`)
  - *"What software engineers actually do all day"*: YES (`T23`)
  - *"What a coding interview is really testing"*: YES (`T5`)
  - *"How a junior software engineer ships a small feature"*: YES (`T1`)
  - *"How game AI decides enemy behavior"*: YES (`T24`)
  - *"What a game engine actually does"*: YES (`T25`)
  - *"Gaming laptop specs that actually matter"*: YES (`T26`)

### C. `data/expected_outputs.json`
- **Top-level keys**: `["trap_after_R1", "trap_after_R1_R2", "trap_after_R1_R2_R3", "trap_after_R1_R2_R3_R4"]`
- **Key Verification**:
  - `trap_after_R1`: YES
  - `trap_after_R1_R2`: YES
  - `trap_after_R1_R2_R3`: YES
  - `trap_after_R1_R2_R3_R4`: YES
- **Checkpoint Details**:
  - `trap_after_R1`:
    - **CURRENT REEL**: `R1`
    - **CONFIDENCE**: `Low`
    - **RECOMMENDED TECH REEL**: `Beginner programming concepts explained with memes`
  - `trap_after_R1_R2`:
    - **CURRENT REEL**: `session: R1, R2`
    - **CONFIDENCE**: `Medium`
    - **RECOMMENDED TECH REEL**: `What software engineers actually do all day`
  - `trap_after_R1_R2_R3`:
    - **CURRENT REEL**: `session: R1, R2, R3`
    - **CONFIDENCE**: `High`
    - **RECOMMENDED TECH REEL**: `What a coding interview is really testing`
  - `trap_after_R1_R2_R3_R4`:
    - **CURRENT REEL**: `session: R1, R2, R3, R4`
    - **CONFIDENCE**: `High`
    - **RECOMMENDED TECH REEL**: `How a junior software engineer ships a small feature`

### D. `data/trap_regression.json`
- **Whether it has a cases array**: YES
- **All case_id values**: `["trap_java_to_swe", "non_trap_gaming_only"]`
- **Watched Reel IDs per case**:
  - `trap_java_to_swe`: `["R1", "R2", "R3", "R4"]`
  - `non_trap_gaming_only`: `["R5", "R6", "R7"]`
- **Whether `non_trap_gaming_only` exists**: YES
- **Whether `non_trap_gaming_only` references R5, R6, and R7**: YES

### E. `data/identity_graph.json`
- **Total node count**: 23
- **Total edge count**: 21
- **Gaming Branch Node Verification**:
  - `gaming`: YES
  - `game_development`: YES
  - `game_developer`: YES
  - `game_ai`: YES
  - `graphics`: YES
  - `gaming_hardware`: YES
  - `hardware`: YES
  - `gameplay_highlight`: YES
  - `game_ai_content`: YES
  - `gaming_laptop`: YES
- **Gaming Branch Edge Verification**:
  - `gameplay_highlight -> gaming`: YES (weight: 0.8)
  - `game_ai_content -> game_ai`: YES (weight: 0.8)
  - `gaming_laptop -> gaming_hardware`: YES (weight: 0.7)
  - `gaming -> game_development`: YES (weight: 0.65)
  - `gaming_hardware -> hardware`: YES (weight: 0.7)

---

## 6. VALIDATOR COVERAGE SUMMARY

Direct inspection of `tools/validate_data.py` confirms presence of all requirements:

| Required Check | Implemented in Validator | Verification Detail |
|---|---|---|
| Check `score_type == "reference_only"` | YES | Check 18 |
| Check four expected-output checkpoint keys | YES | Check 19 |
| Check confidence non-decreasing order | YES | Check 21 (`Low` <= `Medium` <= `High` <= `High`) |
| Check recommended titles exist in `tech_reels.json` | YES | Check 22 |
| Check `trap_regression` cases array | YES | Check 23 (`trap_java_to_swe`, `non_trap_gaming_only`) |
| Check `non_trap_gaming_only` references R5/R6/R7 | YES | Check 24 |
| Check R5/R6/R7 are gaming-related | YES | Check 26 (checks `gaming`/`game` presence) |
| Check forbidden coding terms in R5/R6/R7 | YES | Check 26 (rejects java, coding, swe, etc.) |
| Check gaming identity graph nodes | YES | Check 27 |
| Check gaming identity graph edges | YES | Check 28 |

---

## 7. PHASE COMPLIANCE VERDICT

- **PHASE 0 ORIGINAL CONTRACT**: **PASS**
- **PHASE 0.1 HARDENED CONTRACT**: **PASS**

### MISSING ITEMS:
- **None**

### EVIDENCE:
1. `tools/validate_data.py` executes successfully with **28/28 checks passing**.
2. Git working tree is completely clean and tracked under repository `dheerajgowd-18/reel-recomendation` on branch `main`.
3. All required cumulative checkpoints, reference score attributes, and false-positive non-trap test cases match the strict specification.
