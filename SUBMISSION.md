# ScrollSense: Final Hackathon Submission Overview

> **One-Line Summary:** ScrollSense is an offline-capable, identity-gated AI recommendation agent that infers latent engineering interests from short-form engagement, traverses a skill knowledge graph, and delivers career-accelerating technical learning while defeating superficial keyword loops and clickbait hype.

---

## 1. The Trap & The Breakthrough Output Block

When a student watches a Java meme (`R1`), a junior software engineer vlog (`R2`), a whiteboard coding interview joke (`R3`), and a CS laptop comparison (`R4`), naive algorithms overfit to the keyword "Java" and recommend more memes or trivial syntax videos (*"Learn Java in 60 seconds"*).

ScrollSense infers the latent professional identity (**Software Engineering**) and produces the standard 8-line contract output:

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

---

## 2. Demonstration & Verification Commands

### A. Interactive Live Demo UI (Web Dashboard)
```bash
pip install -r requirements-ui.txt
python -m ui.server
```
Open **`http://127.0.0.1:8000`** in any browser.

### B. Live Presentation CLI Runner
```bash
python run_demo.py
```

### C. Comprehensive Automated Audit (All 11 Suites & 148 Tests)
```bash
python tools/final_audit.py
```

### D. Pytest Suite & Coverage
```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

---

## 3. Architecture Summary

ScrollSense operates a 6-stage deterministic pipeline:
1. **Signal Extraction** (`src/signals.py`): Extracts typed evidence (domain, identity, skills, tooling, career stage) from each reel.
2. **InterestState Aggregation & Graph Traversal** (`src/persona.py` & `src/graph.py`): Combines multi-reel evidence into latent personas and activates 1-hop adjacent engineering competencies.
3. **Dual-Source Retrieval** (`src/retrieve.py`): Combines direct concept matches with identity-activated graph nodes.
4. **Safety, Quality & Anti-Hype Gate** (`src/gate.py`): Filters clickbait with hard predatory denylists (rejecting `T99: "10 AI tools that will get you a job"`) and concrete concept-anchor substance scoring.
5. **Stage-Fit Ranking** (`src/rank.py`): Ranks candidates with heuristic weights, goal alignment, and overgeneralization penalties.
6. **Explanation & Contract Formatting** (`src/explain.py` & `src/formatter.py`): Produces explainable multi-signal rationales and strict schema-validated output blocks.

---

## 4. AI Layer Summary

- **Model**: **NVIDIA Nemotron 3.5 Lightning 30B A3B** (`nvidia/nemotron-3.5-lightning-30b-a3b`).
- **Safety & Guardrails**:
  - LLM never directly chooses the final recommended candidate.
  - LLM never modifies `CATEGORY`, `DIFFICULTY`, or `CONFIDENCE`.
  - Offline cache fixtures ensure 100% deterministic, zero-network execution on stage.
  - Automatic fallback to deterministic heuristics if AI output fails schema validation.

---

## 5. Google Services Usage

- Built end-to-end with Google Antigravity (agentic IDE).
- The deployed demo runs in cached mode for reproducible, offline-safe evaluation.

---

## 6. Problem Statement Alignment Table

| Problem Statement Requirement | Implementation in Codebase | Automated Verification |
|---|---|---|
| *"Analyzes the Reels a student interacts with"* | `src/signals.py` multi-signal extractor | `tools/validate_signals.py` (18 checks), `tests/test_phase2_signals.py` |
| *"Infers their underlying interests"* | `src/persona.py` + `src/graph.py` traversal | `tools/validate_inference.py` (14 checks), `tests/test_phase3_inference.py` |
| *"Recommends engaging technology-related Reels"* | `src/retrieve.py` + `src/rank.py` | `tools/validate_retrieval.py`, `tools/validate_pipeline.py` |
| *"Not rely on simple keyword matching"* | Latent graph expansion vs. naive baselines | `src/baselines.py`, `tests/test_phase7_baselines.py` |
| *"Not to stop social media use"* | Non-intrusive recommendation agent | Pure feed-enrichment design without blocking |
| *"Avoid blindly recommending hype content"* | `src/gate.py` hard predatory denylist | `tools/validate_gate.py`, `T99` rejection tests |
| *"Required output contract schema"* | `src/formatter.py` strict validator | `tests/test_contract_pytest.py` |
