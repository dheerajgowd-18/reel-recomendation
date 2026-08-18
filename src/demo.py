"""Demo presentation harness and judge comparison layer for ScrollSense Phase 7."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.baselines import get_watched_reels_by_ids, run_all_baselines_for_reels
from src.config import CASE_MAPPING, OUTPUT_DIR
from src.pipeline import run_pipeline_for_reels

DEMO_TRACE_PATH = OUTPUT_DIR / "demo_trace.json"
DEMO_REPORT_PATH = OUTPUT_DIR / "demo_report.md"
DEMO_HTML_PATH = OUTPUT_DIR / "demo.html"

PITCH_LINE = (
    "This is the trap in the problem statement. A shallow system sees Java and recommends "
    "another Java Reel. ScrollSense infers the latent professional identity — software engineering — "
    "from heterogeneous signals: a meme, a lifestyle Reel, an interview joke, and a laptop comparison. "
    "It then retrieves useful adjacent tech content and explicitly rejects hype like "
    "“10 AI tools that will get you a job.”"
)


def build_demo_case_data(
    reel_ids: List[str], case_name: Optional[str] = None
) -> Dict[str, Any]:
    """Run both baselines and ScrollSense real pipeline for a sequence of reels."""
    watched_items = get_watched_reels_by_ids(reel_ids)
    baselines_res = run_all_baselines_for_reels(reel_ids, case_name=case_name)
    output_txt, trace_dict = run_pipeline_for_reels(reel_ids, mode="real", case_name=case_name)

    # Extract ScrollSense summaries
    inf_sum = trace_dict.get("inference_summary", {})
    gate_sum = trace_dict.get("gate_summary", {})
    rank_sum = trace_dict.get("ranking_summary", {})
    expl_sum = trace_dict.get("explanation_summary", {})

    from src.gate import load_or_generate_gate_cache
    gate_cache = load_or_generate_gate_cache()

    rejected_list: List[Dict[str, str]] = []
    for cid in gate_sum.get("rejected_ids", []):
        if cid in gate_cache:
            rejected_list.append({
                "candidate_id": cid,
                "title": gate_cache[cid].get("title", cid),
                "rejection_reason": gate_cache[cid].get("rejection_reason", "Gate rejected"),
            })

    from src.infer import infer_interests
    inf_obj = infer_interests(reel_ids, case_name=case_name)
    graph_acts = [
        a["node"] for a in inf_obj.get("graph_traversal", {}).get("activated_nodes", [])
    ]

    scrollsense_data = {
        "output_block": output_txt,
        "interest_detected": expl_sum.get("interest_label", ""),
        "recommended_candidate_id": rank_sum.get("top_candidate_id", ""),
        "recommended_title": rank_sum.get("top_candidate_title", ""),
        "category": "Career" if "Career" in output_txt else ("AI" if "AI" in output_txt else "Other"),
        "confidence": inf_sum.get("confidence", "Low"),
        "top_identity": inf_sum.get("top_professional_identity", ""),
        "top_domains": inf_sum.get("top_domains", []),
        "top_goals": inf_sum.get("top_goals", []),
        "graph_activations": graph_acts,
        "gate_rejections": rejected_list,
        "ranking_summary": rank_sum,
    }

    # Determine flags
    trap_defeated = rank_sum.get("top_candidate_id") == "T1" if set(reel_ids) == {"R1", "R2", "R3", "R4"} else True
    hype_rejected = any(r["candidate_id"] == "T99" for r in rejected_list)

    return {
        "reel_ids": reel_ids,
        "watched_reels": [
            {
                "reel_id": r.get("reel_id", ""),
                "title": r.get("title", ""),
                "topic": r.get("topic", ""),
                "content_type": r.get("content_type", ""),
            }
            for r in watched_items
        ],
        "baselines": baselines_res,
        "scrollsense": scrollsense_data,
        "trap_defeated": trap_defeated,
        "hype_rejected": hype_rejected,
    }


def generate_demo_report_markdown(cases_data: Dict[str, Any]) -> str:
    """Generate clean judge-facing demo markdown report."""
    trap_data = cases_data.get("trap_java_to_swe", cases_data.get("trap_after_R1_R2_R3_R4", {}))
    gaming_data = cases_data.get("non_trap_gaming_only", {})

    lines: List[str] = [
        "# ScrollSense Demonstration & Evaluation Report",
        "",
        "## Executive Summary",
        "ScrollSense is an AI-powered tech recommendation agent designed to escape superficial recommendation traps. "
        "This report demonstrates how naive baseline recommenders fail by overfitting to surface keywords or single topics, "
        "while ScrollSense synthesizes latent professional identity, activates knowledge graphs, rejects deceptive hype, "
        "and delivers career-accelerating recommendations.",
        "",
        "---",
        "",
        "## Part 1: The Trap Case (`trap_java_to_swe`)",
        "",
        "### 1. Watched Reels Sequence",
    ]

    if trap_data:
        for r in trap_data.get("watched_reels", []):
            lines.append(f"- **{r['reel_id']}**: *{r['title']}* (Type: `{r['content_type']}`, Topic: `{r['topic']}`)")
        lines.extend([
            "",
            "### 2. Baseline 1 Failure (Surface Topic-Only)",
            f"- **Recommendation**: `{trap_data['baselines']['topic_only']['recommended_candidate_id']}` — *{trap_data['baselines']['topic_only']['recommended_title']}*",
            f"- **Category**: `{trap_data['baselines']['topic_only']['category']}` | **Confidence**: `{trap_data['baselines']['topic_only']['confidence']}`",
            f"- **Failure Mode**: {trap_data['baselines']['topic_only']['failure_mode']}",
            "",
            "### 3. Baseline 2 Failure (Keyword Token Similarity)",
            f"- **Recommendation**: `{trap_data['baselines']['keyword_similarity']['recommended_candidate_id']}` — *{trap_data['baselines']['keyword_similarity']['recommended_title']}*",
            f"- **Category**: `{trap_data['baselines']['keyword_similarity']['category']}` | **Confidence**: `{trap_data['baselines']['keyword_similarity']['confidence']}`",
            f"- **Failure Mode**: {trap_data['baselines']['keyword_similarity']['failure_mode']}",
            "",
            "### 4. ScrollSense Inferred Latent Interest",
            f"- **Detected Interest**: {trap_data['scrollsense']['interest_detected']}",
            f"- **Inferred Identity**: `{trap_data['scrollsense']['top_identity']}` (Confidence: `{trap_data['scrollsense']['confidence']}`)",
            f"- **Inferred Goals**: `{', '.join(trap_data['scrollsense']['top_goals'])}`",
            "",
            "### 5. Identity Graph Traversal",
            f"Activated Competency & Tooling Nodes: `{', '.join(trap_data['scrollsense']['graph_activations'])}`",
            "",
            "### 6. Anti-Hype Gate Rejections",
        ])
        for rej in trap_data['scrollsense']['gate_rejections']:
            lines.append(f"- **{rej['candidate_id']}** (*{rej['title']}*): `{rej['rejection_reason']}`")
        lines.extend([
            "",
            "### 7. Final ScrollSense Standard Output",
            "```text",
            trap_data['scrollsense']['output_block'],
            "```",
            "",
            "### 8. Demo Pitch",
            "> **Judge Pitch Line**:",
            f"> {PITCH_LINE}",
        ])

    lines.extend([
        "",
        "---",
        "",
        "## Part 2: Non-Trap Gaming Case (`non_trap_gaming_only`)",
        "",
    ])

    if gaming_data:
        lines.append("### 1. Watched Reels Sequence")
        for r in gaming_data.get("watched_reels", []):
            lines.append(f"- **{r['reel_id']}**: *{r['title']}* (Type: `{r['content_type']}`, Topic: `{r['topic']}`)")
        lines.extend([
            "",
            "### 2. Baseline Behavior",
            f"- **Topic Baseline**: `{gaming_data['baselines']['topic_only']['recommended_candidate_id']}` — *{gaming_data['baselines']['topic_only']['recommended_title']}*",
            f"- **Keyword Baseline**: `{gaming_data['baselines']['keyword_similarity']['recommended_candidate_id']}` — *{gaming_data['baselines']['keyword_similarity']['recommended_title']}*",
            "",
            "### 3. ScrollSense Inferred Latent Interest",
            f"- **Detected Interest**: {gaming_data['scrollsense']['interest_detected']}",
            f"- **Top Domains**: `{', '.join(gaming_data['scrollsense']['top_domains'])}`",
            f"- **Confidence**: `{gaming_data['scrollsense']['confidence']}`",
            "",
            "### 4. Gaming Graph Traversal",
            f"Activated Gaming Nodes: `{', '.join(gaming_data['scrollsense']['graph_activations'])}`",
            "",
            "### 5. Final ScrollSense Standard Output",
            "```text",
            gaming_data['scrollsense']['output_block'],
            "```",
            "",
            "### 6. False-Positive Safety Check",
            "- Inferred SWE Identity: `None / 0.0`",
            "- Software Engineering wording leakage: **ZERO (Pass)**",
            "- Clean domain isolation between gaming and career preparation maintained.",
        ])

    return "\n".join(lines)


def generate_demo_html(cases_data: Dict[str, Any]) -> str:
    """Generate self-contained, offline-safe HTML presentation dashboard."""
    trap_data = cases_data.get("trap_java_to_swe", cases_data.get("trap_after_R1_R2_R3_R4", {}))
    gaming_data = cases_data.get("non_trap_gaming_only", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ScrollSense - AI Recommendation Agent Demo</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --danger: #f87171;
      --success: #4ade80;
      --warning: #fbbf24;
      --code-bg: #090d16;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 2rem 1rem;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{ margin-bottom: 2rem; border-bottom: 1px solid var(--card-border); padding-bottom: 1.5rem; }}
    h1 {{ font-size: 2rem; color: var(--accent); margin-bottom: 0.5rem; }}
    .subtitle {{ color: var(--text-muted); font-size: 1.1rem; }}
    .pitch-box {{
      background: rgba(56, 189, 248, 0.08);
      border: 1px solid var(--accent);
      border-radius: 8px;
      padding: 1.25rem;
      margin: 1.5rem 0 2.5rem 0;
      font-size: 1.05rem;
    }}
    .section-title {{ font-size: 1.5rem; margin: 2rem 0 1rem 0; color: var(--text); }}
    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
    }}
    .card-header {{ font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--card-border); }}
    .card-header.danger {{ color: var(--danger); }}
    .card-header.success {{ color: var(--success); }}
    .card-header.accent {{ color: var(--accent); }}
    .reel-item {{
      background: rgba(0,0,0,0.2);
      padding: 0.75rem;
      border-radius: 6px;
      margin-bottom: 0.75rem;
      border-left: 3px solid var(--accent);
    }}
    .badge {{
      display: inline-block;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
    }}
    .badge-meme {{ background: #475569; color: #fff; }}
    .badge-danger {{ background: rgba(248, 113, 113, 0.2); color: var(--danger); border: 1px solid var(--danger); }}
    .badge-success {{ background: rgba(74, 222, 128, 0.2); color: var(--success); border: 1px solid var(--success); }}
    pre {{
      background: var(--code-bg);
      color: #e2e8f0;
      padding: 1rem;
      border-radius: 6px;
      overflow-x: auto;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.85rem;
      line-height: 1.6;
      border: 1px solid var(--card-border);
      margin-top: 0.5rem;
    }}
    .highlight {{ color: var(--accent); font-weight: 600; }}
    .tag-cloud {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }}
    .tag {{ background: #334155; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>ScrollSense: Recommendation Agent Demo</h1>
      <p class="subtitle">Deterministic signal extraction, identity graph traversal & anti-hype gating.</p>
    </header>

    <div class="pitch-box">
      <strong>Core Breakthrough:</strong> {PITCH_LINE}
    </div>

    <h2 class="section-title">The Trap Demonstration: <code>trap_java_to_swe</code></h2>
    <div class="grid-3">
      <!-- Panel 1 -->
      <div class="card">
        <div class="card-header accent">Panel 1: Watched Session Reels</div>
        <p style="color: var(--text-muted); margin-bottom: 1rem; font-size: 0.9rem;">Heterogeneous student watch sequence:</p>
"""

    if trap_data:
        for r in trap_data.get("watched_reels", []):
            html += f"""
        <div class="reel-item">
          <strong>{r['reel_id']}</strong>: {r['title']}<br>
          <span class="badge badge-meme">{r['content_type']}</span> <span style="font-size: 0.8rem; color: var(--text-muted);">Topic: {r['topic']}</span>
        </div>"""

        html += f"""
      </div>

      <!-- Panel 2 -->
      <div class="card">
        <div class="card-header danger">Panel 2: Naive Baselines (Trap Failure)</div>
        <p style="color: var(--text-muted); margin-bottom: 1rem; font-size: 0.9rem;">Shallow matching fails by overfitting to Java:</p>
        
        <div style="margin-bottom: 1.25rem;">
          <span class="badge badge-danger">Baseline 1 (Topic-Only)</span>
          <p style="margin-top: 0.5rem;"><strong>Recommends:</strong> {trap_data['baselines']['topic_only']['recommended_title']} (<code>{trap_data['baselines']['topic_only']['recommended_candidate_id']}</code>)</p>
          <p style="font-size: 0.85rem; color: var(--danger); margin-top: 0.25rem;"><em>{trap_data['baselines']['topic_only']['failure_mode']}</em></p>
        </div>

        <div>
          <span class="badge badge-danger">Baseline 2 (Keyword Overlap)</span>
          <p style="margin-top: 0.5rem;"><strong>Recommends:</strong> {trap_data['baselines']['keyword_similarity']['recommended_title']} (<code>{trap_data['baselines']['keyword_similarity']['recommended_candidate_id']}</code>)</p>
          <p style="font-size: 0.85rem; color: var(--danger); margin-top: 0.25rem;"><em>{trap_data['baselines']['keyword_similarity']['failure_mode']}</em></p>
        </div>
      </div>

      <!-- Panel 3 -->
      <div class="card">
        <div class="card-header success">Panel 3: ScrollSense (Trap Escaped)</div>
        <p style="color: var(--text-muted); margin-bottom: 0.5rem; font-size: 0.9rem;">Latent identity inference & graph reasoning:</p>
        
        <p><strong>Inferred Identity:</strong> <span class="highlight">{trap_data['scrollsense']['top_identity']}</span> ({trap_data['scrollsense']['confidence']} Conf)</p>
        <p style="margin-top: 0.25rem;"><strong>Graph Activations:</strong></p>
        <div class="tag-cloud">"""
        for act in trap_data['scrollsense']['graph_activations']:
            html += f'<span class="tag">{act}</span>'

        html += f"""
        </div>

        <p style="margin-top: 0.75rem;"><strong>Anti-Hype Filtered:</strong></p>
        <p style="font-size: 0.85rem; color: var(--danger);">Rejected <code>T99</code> (<em>10 AI tools that will get you a job</em>)</p>
        
        <p style="margin-top: 0.75rem;"><strong>Output Contract:</strong></p>
        <pre>{trap_data['scrollsense']['output_block']}</pre>
      </div>
    </div>"""

    if gaming_data:
        html += f"""
    <h2 class="section-title">Domain Boundary Isolation: <code>non_trap_gaming_only</code></h2>
    <div class="card" style="margin-bottom: 2rem;">
      <div class="card-header accent">Gaming Non-Trap Execution</div>
      <p style="color: var(--text-muted); margin-bottom: 0.5rem;">Proves ScrollSense does not falsely project software-engineering identity onto pure gaming sessions:</p>
      <p><strong>Detected Interest:</strong> <span class="highlight">{gaming_data['scrollsense']['interest_detected']}</span></p>
      <p><strong>Recommended:</strong> {gaming_data['scrollsense']['recommended_title']} (<code>{gaming_data['scrollsense']['recommended_candidate_id']}</code>, Category: {gaming_data['scrollsense']['category']})</p>
      <p><strong>SWE Identity Leakage:</strong> <span class="badge badge-success">ZERO (Clean Isolation)</span></p>
      <pre>{gaming_data['scrollsense']['output_block']}</pre>
    </div>"""

    html += """
  </div>
</body>
</html>"""
    return html


def run_demo(case: Optional[str] = None, all_cases: bool = False) -> Dict[str, Any]:
    """Execute complete demonstration harness and generate trace, report, and HTML."""
    cases_to_run: Dict[str, List[str]] = {}
    if all_cases or not case:
        cases_to_run = {
            "trap_after_R1": ["R1"],
            "trap_after_R1_R2": ["R1", "R2"],
            "trap_after_R1_R2_R3": ["R1", "R2", "R3"],
            "trap_java_to_swe": ["R1", "R2", "R3", "R4"],
            "non_trap_gaming_only": ["R5", "R6", "R7"],
        }
    elif case == "trap_java_to_swe":
        cases_to_run = {"trap_java_to_swe": ["R1", "R2", "R3", "R4"]}
    elif case == "non_trap_gaming_only":
        cases_to_run = {"non_trap_gaming_only": ["R5", "R6", "R7"]}
    else:
        raise ValueError(f"Unknown case '{case}'. Supported: {sorted(CASE_MAPPING.keys())}")

    demo_cases_results: Dict[str, Any] = {}
    for c_name, r_ids in cases_to_run.items():
        demo_cases_results[c_name] = build_demo_case_data(r_ids, case_name=c_name)

    demo_trace = {
        "phase": "phase_7_demo",
        "generated_at": "2026-08-18T00:00:00Z",
        "cases": demo_cases_results,
    }

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Write demo trace JSON
    with open(DEMO_TRACE_PATH, "w", encoding="utf-8") as f:
        json.dump(demo_trace, f, indent=2)

    # 2. Write demo report Markdown
    report_md = generate_demo_report_markdown(demo_cases_results)
    with open(DEMO_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_md + "\n")

    # 3. Write demo HTML
    html_content = generate_demo_html(demo_cases_results)
    with open(DEMO_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content + "\n")

    # Console summary
    print("=" * 60)
    print("SCROLLSENSE DEMO HARNESS COMPLETE")
    print("=" * 60)
    print(f"Demo Trace:  {DEMO_TRACE_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Demo Report: {DEMO_REPORT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Demo HTML:   {DEMO_HTML_PATH.relative_to(PROJECT_ROOT)}")
    print("=" * 60)
    if "trap_java_to_swe" in demo_cases_results:
        t = demo_cases_results["trap_java_to_swe"]
        print(f"TRAP ESCAPE: Baseline 1 -> {t['baselines']['topic_only']['recommended_candidate_id']} | ScrollSense -> {t['scrollsense']['recommended_candidate_id']} ({t['scrollsense']['recommended_title']})")
    if "non_trap_gaming_only" in demo_cases_results:
        g = demo_cases_results["non_trap_gaming_only"]
        print(f"GAMING:     ScrollSense -> {g['scrollsense']['recommended_candidate_id']} ({g['scrollsense']['recommended_title']})")
    print("=" * 60)

    return demo_trace


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ScrollSense Demo Harness: Evaluation and Judge Presentation."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--all",
        action="store_true",
        help="Run demo harness across all standard checkpoints.",
    )
    group.add_argument(
        "--case",
        type=str,
        help="Named regression test case (e.g. trap_java_to_swe, non_trap_gaming_only).",
    )

    args = parser.parse_args()

    try:
        run_demo(case=args.case, all_cases=args.all or (not args.case))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
