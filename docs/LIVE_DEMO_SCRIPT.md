# ScrollSense: Live Presentation & Judge Talk Track

This guide provides the presentation script and steps for demonstrating ScrollSense to hackathon judges.

---

## 1. Executive Pitch (30 seconds)

> *"Short-form video feeds often trap students in superficial loops. When a student watches a programming meme, the algorithm recommends more memes or basic syntax tutorials.*
>
> *ScrollSense is an offline-capable, explainable recommendation agent. It extracts structured signals from heterogeneous engagement (memes, lifestyle vlogs, interview jokes, hardware comparisons), synthesizes a latent professional identity, traverses an engineering skill knowledge graph, and recommends substantive, career-building tech reels while rejecting clickbait hype."*

---

## 2. Live Terminal Demonstration (60 seconds)

### Command:
```bash
python run_demo.py
```

### Key Talking Points to Highlight on Screen:
1. **The Trap Setup**:
   - Show the session reels: `R1` (Java meme), `R2` (SWE lifestyle), `R3` (Whiteboard interview humor), `R4` (CS student laptop review).
2. **Naive Baseline Failure**:
   - Show that Baseline 1 (Topic-only) and Baseline 2 (Keyword overlap) both collapse to `T96: "Learn Java in 60 seconds"`.
   - Explain why: Naive algorithms overfit to literal keywords from the meme.
3. **ScrollSense Latent Inference**:
   - ScrollSense recognizes the synthesis: **Software engineering culture and early career preparation** (Confidence: **High**).
   - Knowledge graph activates core competencies: `git`, `debugging`, `system design`, `career`, `DSA`.
4. **Anti-Hype Quality Gate**:
   - Point out that `T99` (*"10 AI tools that will get you a job"*) was retrieved but **rejected by the live computed gate** due to hard predatory denylists and low concept anchor substance.
5. **The Winning Recommendation**:
   - Recommends `T1`: *"How a junior software engineer ships a small feature"* (Category: `Career`, Difficulty: `Beginner`).
   - Generates exact explainable `WHY` and `WHY THIS RECOMMENDATION` text.

---

## 3. Domain Isolation Check (30 seconds)

### Command:
```bash
python -m src.run --case non_trap_gaming_only --mode real
```

### Talking Point:
- Show that for pure gaming reels (`R5, R6, R7`), ScrollSense cleanly recommends `T24: "How game AI decides enemy behavior"` with **zero software-engineering leakage**.

---

## 4. Full Automated Verification (15 seconds)

### Command:
```bash
python tools/final_audit.py
```
- Proves 100% test pass rate (103 unit tests, 123+ automated assertions, 0 failures, 100% offline).
