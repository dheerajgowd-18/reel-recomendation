# ScrollSense: Identity-Gated Tech Reel Recommender

ScrollSense is an AI-powered recommendation agent that transforms passive short-form video browsing into career-accelerating technical learning. Instead of trapping students in superficial keyword loops or serving sensationalized clickbait, ScrollSense infers latent professional identity from heterogeneous engagement signals, traverses an engineering skill knowledge graph, filters candidates through a strict anti-hype quality gate, and generates explainable recommendations.

Built with standard library Python 3 as a modular monolith, ScrollSense runs 100% offline, deterministically, and reproducibly with zero external API or network dependencies.

---

## The Problem & The Trap

A college student scrolls through short-form videos and watches:
1. **R1**: A comedic Java programming meme about missing semicolons (`#javamemes`).
2. **R2**: A junior software engineer vlog showing daily workflows and standups (`#swe`).
3. **R3**: A whiteboard coding interview joke about inverting binary trees (`#leetcode`).
4. **R4**: A comparison of developer laptops handling Docker and IntelliJ (`#devsetup`).

### The Superficial Trap
Standard recommendation engines overfit to surface keywords and literal category frequencies. They see the word "Java" in `R1` and trap the student with more programming memes or basic syntax tutorials like *"Learn Java in 60 seconds"*.

### The ScrollSense Solution
ScrollSense decodes the underlying synthesis: the student is not just browsing Java jokes—they are actively exploring **Software Engineering Culture and Early Career Preparation**. ScrollSense activates developer tooling and core competency concepts across its identity graph and recommends practical engineering craftsmanship: *"How a junior software engineer ships a small feature"*.

---

## The Architecture

ScrollSense executes an offline 6-stage deterministic pipeline:

```
Watched Reels Sequence (R1, R2, R3, R4)
                 │
                 ▼
 1. Signal Extraction (src/signals.py)
    └─ Structured ReelSignal (identities, domains, tooling, skills, career stages)
                 │
                 ▼
 2. InterestState & Graph Traversal (src/persona.py & src/graph.py)
    └─ Multi-reel aggregation + 1-hop activation traversal across Identity Graph
                 │
                 ▼
 3. Dual-Source Candidate Retrieval (src/retrieve.py)
    └─ Source A (topical matching) + Source B (graph identity-adjacent activation)
                 │
                 ▼
 4. Safety / Quality / Anti-Hype Gate (src/gate.py)
    └─ Hard predatory denylists + concrete concept-anchor substance scoring
    └─ [NOTE: Candidate catalog scores are 'reference_only'; gate scores are computed live]
                 │
                 ▼
 5. Heuristic Ranking & Stage Fit (src/rank.py)
    └─ HEURISTIC_WEIGHTS_V1: identity fit, goal fit, difficulty match, overgen penalties
                 │
                 ▼
 6. Explanation & Output Formatting (src/explain.py & src/formatter.py)
    └─ Exact contract generation with explainable WHY & WHY THIS RECOMMENDATION
---

## AI Model

ScrollSense uses **NVIDIA Nemotron 3.5 Lightning 30B A3B** as an optional AI-assisted layer.

```text
LLM_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b
```

The model is utilized strictly for:
- **Reel signal extraction** (synthesizing rich domain, tooling, and career cues into structured schema)
- **Explanation refinement** (generating fluent multi-evidence rationales)
- **Optional concept-anchor judgment** (evaluating technical substance in retrieved candidates)

### AI Safety & Guardrails
- **The model is NEVER allowed to directly choose the final recommendation.**
- **The model is NEVER allowed to modify CATEGORY, DIFFICULTY, or CONFIDENCE.**
- All AI outputs are schema-validated against strict contract rules.
- Invalid, corrupted, or overgeneralized LLM outputs automatically trigger deterministic fallbacks (`fallback_used = True`).
- All demo and regression modes operate 100% offline via persisted LLM cache fixtures (`cache/llm/`).

---

## How It Defeats the Trap

### Live Comparison on Trap Session (`trap_java_to_swe`)

| Recommender | Inferred Interest | Recommended Tech Reel | Category | Verdict |
|---|---|---|---|---|
| **Baseline 1 (Topic-Only)** | `Java` (Surface frequency) | *Learn Java in 60 seconds* (`T96`) | Java | ❌ **Trap Failure** (Superficial loop) |
| **Baseline 2 (Keyword Overlap)** | `java, programming` (Tokens) | *Learn Java in 60 seconds* (`T96`) | Java | ❌ **Trap Failure** (Keyword overfitting) |
| **ScrollSense (Real Pipeline)** | `Software engineering culture and early career preparation` | **How a junior software engineer ships a small feature** (`T1`) | **Career** | ✅ **Trap Defeated** (Latent identity match) |

### Anti-Hype Gate: Rejection of Clickbait
Deceptive career-promise content such as `T99` (*"10 AI tools that will get you a job"*) is shortlisted during initial retrieval but **strictly rejected by the quality gate**:
- **Gate Match**: `hard_denylist_match: True` (Matched `'get you a job'`)
- **Concept Anchor Score**: `0.0` (Zero concrete technical mechanisms)
- **Gate Result**: `effective_reject: True`

Meanwhile, legitimate educational listicles such as `T97` (*"10 AI tools worth learning"*, teaching Docker, Kubernetes, RAG, and Vector DBs) pass the gate because of strong concrete concept anchors ($S_{\text{concept}} = 1.0$).

---

## Repository Structure

```text
reel-recomendation/
├── run_demo.py               # Master entrypoint for live judge presentation
├── data/                     # Data contracts & candidate catalog
│   ├── watched_reels.json    # Watched reel session fixtures (R1-R7)
│   ├── tech_reels.json       # Candidate tech catalog (T1-T103, score_type: reference_only)
│   ├── identity_graph.json   # 10-node ontology of roles, skills, and tools
│   ├── expected_outputs.json # Standard contract benchmark outputs
│   └── trap_regression.json  # Regression test case definitions
├── src/                      # Monolithic core pipeline modules
│   ├── config.py             # Schema, paths, weights, and alias mappings
│   ├── loaders.py            # Strict schema data loaders
│   ├── signals.py            # Structured signal extraction & cache
│   ├── persona.py            # InterestState aggregation
│   ├── graph.py              # Identity graph activation traversal
│   ├── infer.py              # Inference coordinator & confidence scoring
│   ├── retrieve.py           # Dual-source candidate retrieval
│   ├── gate.py               # Safety, quality & anti-hype live gate
│   ├── rank.py               # Heuristic candidate ranker
│   ├── explain.py            # Deterministic explanation synthesizer
│   ├── formatter.py          # Output contract validator & formatter
│   ├── pipeline.py           # End-to-end pipeline orchestrator (real/stub/auto)
│   ├── baselines.py          # Naive topic & keyword baseline models
│   ├── demo.py               # Multi-case demo harness & trace generator
│   └── run.py                # Main CLI runner
├── tools/                    # Validation and audit utilities
│   ├── check_json_hygiene.py # Whitespace & corruption checker
│   ├── validate_data.py      # Contract validation (28 checks)
│   ├── validate_signals.py   # Signal extraction validation (18 checks)
│   ├── validate_inference.py # Inference validation (14 checks)
│   ├── validate_retrieval.py # Retrieval validation (18 checks)
│   ├── validate_gate.py      # Quality gate validation (18 checks)
│   ├── validate_pipeline.py  # Pipeline validation (25 checks)
│   ├── validate_demo.py      # Demo & baseline validation (20 checks)
│   └── final_audit.py        # Comprehensive master audit runner
├── tests/                    # 103 Unit tests across 8 test suites
├── output/                   # Generated artifacts (result.txt, traces, demo.html)
├── docs/                     # Documentation & presentation scripts
└── reports/                  # Phase-by-phase verification reports
```

---

## Live Demo UI

ScrollSense features a full local interactive demonstration dashboard:

```bash
# 1. Install optional UI server dependencies
pip install -r requirements-ui.txt

# 2. Start the local demo server (default: port 8000)
python -m ui.server
```

Then open **`http://127.0.0.1:8000`** in any browser.

The UI provides interactive controls for:
- Evaluating the Trap case and comparing against naive Baselines 1 & 2.
- Inspecting multi-reel signals and 1-hop Identity Graph activations.
- Viewing live anti-hype gating decisions and clickbait filter logs.
- Viewing the AI/Nemotron status panel and deterministic guardrails.
- Instant fallback mode (`Load Cached Demo`) for guaranteed 100% offline stability on stage.

---

## How to Run the Demo

### 1. Terminal Presentation Demo (CLI)
Run the master presentation script:
```bash
python run_demo.py
```
This prints the baseline vs. ScrollSense comparison, explains the trap escape, displays anti-hype rejections, outputs the exact required contract block, and creates an offline-ready HTML dashboard at `output/demo.html`.

### 2. Run Comprehensive Full Audit
Execute the entire validation and test suite (all 10 suites, 133 unit tests, 137+ assertions):
```bash
python tools/final_audit.py
```

### 3. Run Pipeline CLI
Run recommendations for specific reels or named benchmark cases:
```bash
# Final Trap Case (Real Pipeline)
python -m src.run --case trap_java_to_swe --mode real

# Gaming Non-Trap Case (Proves zero SWE leakage)
python -m src.run --case non_trap_gaming_only --mode real

# Arbitrary Reel Sequences
python -m src.run --reels R1,R2,R3 --mode real

# All Standard Checkpoints
python -m src.run --all-checkpoints --mode real
```

---

## Google Services Usage

- Built end-to-end with Google Antigravity (agentic IDE).
- The deployed demo runs in cached mode for reproducible, offline-safe evaluation.

---

## Honest v1 Scope

- Engagement metadata (liked/saved/watched) is captured; strength-weighting by interaction type is future work.
- The identity/skill graph is hand-authored v1 domain knowledge. The identity is inferred from evidence; the adjacency edges are encoded, not learned.
- "Engaging" is modeled via content format preference (humor, lifestyle, gameplay), not a live engagement model.

---

## Problem Statement Alignment

| Problem Statement Requirement | Architecture Component | Verification & Evidence |
|---|---|---|
| *"Analyzes the Reels a student interacts with"* | `src/signals.py` structured multi-signal evidence extractor | `tools/validate_signals.py` (18 checks), `tests/test_phase2_signals.py` |
| *"Infers their underlying interests"* | `src/persona.py` InterestState synthesizer + `src/graph.py` 1-hop traversal | `tools/validate_inference.py` (14 checks), `tests/test_phase3_inference.py` |
| *"Recommends engaging technology-related Reels"* | `src/retrieve.py` dual-source retriever + `src/rank.py` stage-fit ranker | `tools/validate_retrieval.py`, `tools/validate_pipeline.py` |
| *"Not rely on simple keyword matching"* | Latent identity-adjacent graph activation vs. failing naive baselines | `src/baselines.py`, `tests/test_phase7_baselines.py` |
| *"Not to stop social media use"* | Non-intrusive recommendation-only agent (no blocking or detox gates) | Pure feed-enrichment design architecture |
| *"Avoid blindly recommending hype content"* | `src/gate.py` hard predatory denylist + concrete concept-anchor substance floor | `tools/validate_gate.py`, `T99` rejection tests |
| *"Required output contract schema"* | `src/formatter.py` strict 8-line schema validator | `tests/test_contract_pytest.py`, `tests/test_phase6_pipeline.py` |

---

## Efficiency and Caching

- **ReelSignal Cache**: Pre-extracted signals indexed by `reel_id` (`cache/signals.json`), eliminating repetitive parsing.
- **Live Gate Cache**: Substance evaluations and concept-anchor scores cached per candidate (`cache/gate_results.json`).
- **LLM Evidence Cache**: Pre-validated prompt responses cached by model and version (`cache/llm/`).
- **Linear Complexity**: Single-pass candidate retrieval and ranking runs in $\mathcal{O}(|\mathcal{C}|)$ time, taking $< 15\text{ms}$ per request.
- **Offline Integrity**: 100% local standard library execution without network dependencies.

---

## Testing & Code Quality

```bash
# Run unit and regression tests with Pytest
pip install -r requirements-dev.txt
python -m pytest -q

# Run coverage analysis
python -m pytest --cov=src --cov-report=term-missing

# Run code linter
ruff check .
```

---

## Standard Contract Output Format
All generated recommendations strictly adhere to the standard contract schema:
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
