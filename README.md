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

## Current Phase Status
- **Current Phase**: Phase 0 (Data contracts, fixtures, validation, progress tracking)
- **Status**: COMPLETE
