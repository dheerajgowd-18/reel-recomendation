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

## Running Data Validation
To validate data contracts, fixtures, identity graphs, and regression specs offline:
```bash
python tools/validate_data.py
```

## Phase 1 — Stub Pipeline
Phase 1 implements a deterministic, offline end-to-end stub pipeline to verify CLI wiring, contract mapping, output formatting, and trace generation. It does not yet contain real signal extraction, graph reasoning, gating, or ranking.

### Commands
```bash
# Run data validation suite (28 checks)
python tools/validate_data.py

# Run Phase 1 unit test suite
python -m unittest discover -s tests -v

# Run reel sequences
python -m src.run --reels R1
python -m src.run --reels R1,R2
python -m src.run --reels R1,R2,R3
python -m src.run --reels R1,R2,R3,R4
python -m src.run --reels R5,R6,R7

# Run named test cases
python -m src.run --case trap_java_to_swe
python -m src.run --case non_trap_gaming_only
```

## Phase 2 — Signal Extraction
Phase 2 uses deterministic offline signal extraction. It produces structured interest evidence (`ReelSignal`) for every watched Reel describing latent professional identity, domain, tooling, skill, and career stage signals, but does not yet aggregate that evidence into `InterestState` (which is handled in Phase 3).

### Commands
```bash
# Validate data contracts and signal cache
python tools/validate_data.py
python tools/validate_signals.py

# Run all unit tests (Plumbing + Signal Extraction)
python -m unittest discover -s tests -v

# Generate or view signals
python -m src.signals --all
python -m src.signals --reel R1
python -m src.signals --reels R1,R2,R3,R4
python -m src.signals --reels R5,R6,R7
```

## Current Phase Status
- **Current Phase**: Phase 2 (Signal Extraction Module)
- **Status**: COMPLETE
