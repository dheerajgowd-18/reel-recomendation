# ScrollSense Demonstration & Evaluation Report

## Executive Summary
ScrollSense is an AI-powered tech recommendation agent designed to escape superficial recommendation traps. This report demonstrates how naive baseline recommenders fail by overfitting to surface keywords or single topics, while ScrollSense synthesizes latent professional identity, activates knowledge graphs, rejects deceptive hype, and delivers career-accelerating recommendations.

---

## Part 1: The Trap Case (`trap_java_to_swe`)

### 1. Watched Reels Sequence
- **R1**: *When you miss a semicolon in Java after 4 hours of debugging* (Type: `meme`, Topic: ``)
- **R2**: *Day in the life of a Junior Software Engineer in Austin* (Type: `lifestyle`, Topic: ``)
- **R3**: *Interviewer: Invert a binary tree on this whiteboard right now* (Type: `humor`, Topic: ``)
- **R4**: *M3 Pro vs ThinkPad X1 Carbon for CS Undergrads & Devs* (Type: `comparison`, Topic: ``)

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
Activated Competency & Tooling Nodes: `git, system_design, debugging, dsa, career, cloud, software_engineer`

### 6. Anti-Hype Gate Rejections
- **T99** (*10 AI tools that will get you a job*): `Hard denylist match: 'get you a job'`
- **T100** (*Become a software engineer in 30 days*): `Hard denylist match: 'become a software engineer in'`
- **T102** (*Top 5 coding hacks to get hired fast*): `Hard denylist match: 'get hired fast'`
- **T103** (*Guaranteed tech job roadmap*): `Hard denylist match: 'guaranteed_job'`

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

---

## Part 2: Non-Trap Gaming Case (`non_trap_gaming_only`)

### 1. Watched Reels Sequence
- **R5**: *Insane 1v5 clutch in ranked* (Type: `gaming`, Topic: ``)
- **R6**: *How game AI predicts your next move* (Type: `news`, Topic: ``)
- **R7**: *Best gaming laptop specs explained* (Type: `comparison`, Topic: ``)

### 2. Baseline Behavior
- **Topic Baseline**: `T24` — *How game AI decides enemy behavior*
- **Keyword Baseline**: `T26` — *Gaming laptop specs that actually matter*

### 3. ScrollSense Inferred Latent Interest
- **Detected Interest**: Gaming systems, game AI, and gaming hardware curiosity
- **Top Domains**: `gaming, hardware, ai`
- **Confidence**: `Medium`

### 4. Gaming Graph Traversal
Activated Gaming Nodes: `game_development, graphics, game_ai, game_developer`

### 5. Final ScrollSense Standard Output
```text
CURRENT REEL: session: R5, R6, R7
INTEREST DETECTED: Gaming systems, game AI, and gaming hardware curiosity
WHY: Esports gameplay shows high-level mechanics; game AI Reel shows curiosity about decision-making systems; gaming laptop review shows interest in graphics hardware and thermals.
RECOMMENDED TECH REEL: How game AI decides enemy behavior
CATEGORY: AI
WHY THIS RECOMMENDATION: Explores the algorithmic logic and enemy behaviors underlying gameplay mechanics, connecting gaming excitement to real game intelligence engineering.
DIFFICULTY: Beginner
CONFIDENCE: Medium
```

### 6. False-Positive Safety Check
- Inferred SWE Identity: `None / 0.0`
- Software Engineering wording leakage: **ZERO (Pass)**
- Clean domain isolation between gaming and career preparation maintained.
