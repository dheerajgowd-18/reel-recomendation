# ScrollSense

ScrollSense is an AI-powered recommendation agent that analyzes short-form video engagement, decodes underlying latent interests across heterogeneous content, and recommends high-utility, educational technology Reels that advance student careers and skills. Rather than relying on superficial keyword matching, ScrollSense performs deterministic signal extraction, maps evidence to an identity/skill knowledge graph, applies quality and anti-hype gates, and generates explainable recommendations.

## The Trap Case
A student frequently scrolls through a Java meme, a software engineer lifestyle vlog, a coding interview joke, and a laptop comparison video. A shallow recommendation system falls into the trap of recommending another superficial Java meme or syntax tutorial. ScrollSense identifies the latent synthesis: curiosity about software engineering culture, tooling, and career preparation. It connects these signals across the identity graph and recommends foundational career and engineering content while rejecting deceptive clickbait hype (such as "10 AI tools that will get you a job").

## Required Output Format
All final recommendations conform strictly to the standard contract:
```text
CURRENT REEL: [reference]
INTEREST DETECTED: [topic / interest]
WHY: [evidence from content]
RECOMMENDED TECH REEL: [topic/title]
CATEGORY: [AI / DSA / Java / HLD / Cybersecurity / Cloud / Hardware / Career / Other]
WHY THIS RECOMMENDATION: [connection to interest]
DIFFICULTY: [Beginner / Intermediate / Advanced]
CONFIDENCE: [High / Medium / Low]
```

## Running Data & Pipeline Validation
To validate data contracts, fixtures, signal caches, hygiene, inference, and candidate retrieval offline:
```bash
python tools/check_json_hygiene.py
python tools/validate_data.py
python tools/validate_signals.py
python tools/validate_inference.py
python tools/validate_retrieval.py
python -m unittest discover -s tests -v
```

## Phase 1 — Stub Pipeline
Phase 1 implements a deterministic, offline end-to-end stub pipeline to verify CLI wiring, contract mapping, output formatting, and trace generation.

### Commands
```bash
python -m src.run --reels R1
python -m src.run --reels R1,R2
python -m src.run --reels R1,R2,R3
python -m src.run --reels R1,R2,R3,R4
python -m src.run --reels R5,R6,R7
python -m src.run --case trap_java_to_swe
python -m src.run --case non_trap_gaming_only
```

## Phase 2 — Signal Extraction
Phase 2 uses deterministic offline signal extraction. It produces structured interest evidence (`ReelSignal`) for every watched Reel describing latent professional identity, domain, tooling, skill, and career stage signals.

### Commands
```bash
python -m src.signals --all
python -m src.signals --reel R1
python -m src.signals --reels R1,R2,R3,R4
python -m src.signals --reels R5,R6,R7
```

## Phase 3 — InterestState Aggregation and Graph Traversal
Phase 3 aggregates individual `ReelSignal` items into an integrated `InterestState`, performs one-hop deterministic activation traversal across the `Identity/Skill Graph`, applies deterministic confidence bucketing (`Low`, `Medium`, `High`), and generates explainable inferred interest labels.

### Commands
```bash
python -m src.infer --reels R1
python -m src.infer --reels R1,R2
python -m src.infer --reels R1,R2,R3
python -m src.infer --reels R1,R2,R3,R4
python -m src.infer --reels R5,R6,R7
python -m src.infer --case trap_java_to_swe
python -m src.infer --case non_trap_gaming_only
python -m src.infer --all-checkpoints
```

## Phase 4 — Candidate Retrieval
Phase 4 retrieves candidate Reels using topical and identity-adjacent graph signals. It combines Source A (topical matching) and Source B (graph identity-adjacent activation) into a unified shortlisted candidate catalog. It does not yet apply the hype gate or final ranking.

### Commands
```bash
python -m src.retrieve --reels R1
python -m src.retrieve --reels R1,R2
python -m src.retrieve --reels R1,R2,R3
python -m src.retrieve --reels R1,R2,R3,R4
python -m src.retrieve --reels R5,R6,R7
python -m src.retrieve --case trap_java_to_swe
python -m src.retrieve --case non_trap_gaming_only
python -m src.retrieve --all-checkpoints
```

## Current Phase Status
- **Current Phase**: Phase 4 (Candidate Retrieval)
- **Status**: COMPLETE
