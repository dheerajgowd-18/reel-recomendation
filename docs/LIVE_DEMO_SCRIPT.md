# ScrollSense: Live Presentation & Judge Talk Track

This guide provides the presentation script and steps for demonstrating ScrollSense to hackathon judges via the Interactive Live Demo UI or Terminal.

---

## 1. Executive Pitch (30 seconds)

> *"Short-form video feeds often trap students in superficial loops. When a student watches a programming meme, the algorithm recommends more memes or basic syntax tutorials.*
>
> *ScrollSense is an offline-capable, explainable recommendation agent. It extracts structured signals from heterogeneous engagement (memes, lifestyle vlogs, interview jokes, hardware comparisons), synthesizes a latent professional identity, traverses an engineering skill knowledge graph, and recommends substantive, career-building tech reels while rejecting clickbait hype."*

---

## 2. Interactive Live Demo UI Flow (60 seconds)

### Start Local UI Server:
```bash
python -m ui.server
```
Open in browser: `http://127.0.0.1:8000`

### Step-by-Step UI Presentation Script:
1. **Select Trap Scenario**:
   - In dropdown, select `The Trap: Java Meme to SWE (R1-R4)`.
   - Point to Panel 1: show the 4 watched reels (Java meme, SWE lifestyle, interview humor, laptop comparison).
2. **Run Baselines**:
   - Click `Run Baselines Only`.
   - Point to Panel 2: Highlight how both naive baselines collapse to `T96: "Learn Java in 60 seconds"` due to superficial Java keyword overfitting.
3. **Run ScrollSense Comparison**:
   - Click `Run Full Comparison`.
   - Point to Panel 3 & 4: ScrollSense extracts latent interest: **Software engineering culture and early career preparation** (High Confidence) and traverses graph activating `career`, `git`, `debugging`, `system_design`, `dsa`.
4. **Highlight Anti-Hype Filter**:
   - Point to Panel 5: Show that predatory clickbait `T99` (*"10 AI tools that will get you a job"*) is explicitly rejected by the live gate (`Hard denylist match: 'get you a job'`).
5. **Display Final Contract & AI Status**:
   - Point to Panel 6 & 7: Show that recommendation `T1: "How a junior software engineer ships a small feature"` is rendered strictly in the required 8-line output schema.
   - Point to AI Panel: Show `nvidia/nemotron-3.5-lightning-30b-a3b` evidence layer operating with verified deterministic guardrails.
6. **Deliver Pitch Line**:
   > *"A shallow system sees Java and recommends another Java Reel. ScrollSense infers the latent professional identity — software engineering — from heterogeneous signals: a meme, a lifestyle Reel, an interview joke, and a laptop comparison. It then retrieves useful adjacent tech content and explicitly rejects hype like '10 AI tools that will get you a job'."*

---

## 3. Terminal Demonstration Alternative (CLI)

```bash
python run_demo.py
```

### Domain Isolation Check (Zero SWE Leakage on Gaming):
```bash
python -m src.run --case non_trap_gaming_only --mode real
```

---

## 4. Full Comprehensive Audit (15 seconds)

```bash
python tools/final_audit.py
```
- Proves 100% test pass rate (133 unit tests across 9 suites, 137+ automated assertions, 0 failures, 100% offline).
