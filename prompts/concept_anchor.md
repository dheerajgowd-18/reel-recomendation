# Concept Anchor & Quality Gating Documentation

This document describes the design, scoring rules, and heuristics for the ScrollSense Safety/Quality/Anti-Hype Gate (Phase 5). It serves as technical documentation and the prompt specification for future optional LLM evaluation.

---

## 1. Objective

The goal of the Quality Gate is to protect students from low-utility, misleading, and sensationalized "hype" content (e.g., *"10 AI tools that will get you a job"* or *"Become a software engineer in 30 days"*) while ensuring high-utility educational engineering content reaches them.

Crucially, the gate is **not a blunt listicle or keyword ban**. A video entitled *"10 AI tools worth learning"* that discusses Docker, Kubernetes, RAG, and Vector Databases contains real substance and must pass.

---

## 2. Three-Tiered Gate Architecture

The gate evaluates candidate Reels along three independent axes:

### Tier 1: Hard Denylist & Safety
- **Rule**: Hard match against predatory, get-rich-quick, or misleading career promises triggers **immediate rejection** (`effective_reject = True`).
- **Patterns**:
  - `get you a job`, `will get you a job`, `guaranteed job`
  - `become a developer in`, `become a software engineer in`
  - `secret tools`, `no one tells you`, `make money fast`
  - `six figures`, `without coding`, `hack your career`

### Tier 2: Concept-Anchor Scoring (Substance)
- **Concept Anchor Score** ($S_{\text{concept}} \in [0.0, 1.0]$):
  Measures whether the Reel teaches verifiable, checkable technical mechanisms, tools, or concepts.
- **Concrete Anchors**:
  `git`, `github`, `debugging`, `code review`, `system design`, `dsa`, `binary tree`, `binary search`, `cloud`, `docker`, `kubernetes`, `rag`, `vector databases`, `gpu`, `cpu cache`, `arm`, `x86`, `game engine`, `rendering`, `game ai`, `behavior trees`, `pathfinding`, `linux`, `sql`, `jwt`, `owasp`, `software engineering workflow`.
- **Vague / Non-Anchors**:
  `tools`, `hype`, `career`, `tips`, `secrets`, `hacks`, `ai tools`, `roadmap`.

### Tier 3: Soft Hype Pattern Penalty
- **Hype Pattern Penalty** ($P_{\text{hype}} \in [0.0, 1.0]$):
  Measures sensationalism, clickbait phrasing, and promotional density.
- **Patterns**:
  `10`, `5`, `top`, `tools`, `hacks`, `tips`, `tricks`, `secrets`, `fast`, `instantly`, `guaranteed`, `get hired`, `speedrun`.

---

## 3. Effective Decision Rule

$$\text{effective\_reject} = \text{safety\_fail} \lor \text{hard\_denylist\_match} \lor (S_{\text{concept}} < 0.35 \land P_{\text{hype}} > 0.65)$$

- **Pure Hype Rejection Example (`T99`)**:
  - Title: *"10 AI tools that will get you a job"*
  - Concepts: `[]` ($S_{\text{concept}} = 0.0$)
  - Hype Penalty: $P_{\text{hype}} = 1.0$ (Hard denylist match on `"get you a job"`)
  - **Result**: `REJECTED`
- **Borderline Useful Listicle Acceptance Example (`T97`)**:
  - Title: *"10 AI tools worth learning"*
  - Concepts: `docker`, `kubernetes`, `rag`, `vector databases` ($S_{\text{concept}} = 1.0$)
  - Hype Penalty: $P_{\text{hype}} = 0.70$ (`"10"`, `"tools"`)
  - **Result**: `PASSED` ($S_{\text{concept}} \ge 0.35$ anchors the substance)
