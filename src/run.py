"""CLI Entrypoint for ScrollSense Recommendation Agent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CASE_MAPPING, DEFAULT_PIPELINE_TRACE_PATH, DEFAULT_RESULT_PATH
from src.pipeline import run_all_checkpoint_pipelines, run_pipeline_for_case, run_pipeline_for_reels


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ScrollSense: AI-powered tech reel recommendation agent."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--reels",
        type=str,
        help="Comma-separated list of watched Reel IDs (e.g. R1,R2,R3,R4).",
    )
    group.add_argument(
        "--case",
        type=str,
        help="Named regression test case (e.g. trap_java_to_swe, non_trap_gaming_only).",
    )
    group.add_argument(
        "--all-checkpoints",
        action="store_true",
        help="Execute recommendation pipeline across all standard checkpoints.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["real", "stub", "auto"],
        default="auto",
        help="Pipeline execution mode (default: auto).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=str(DEFAULT_RESULT_PATH),
        help="Path to write the formatted plain-text result block.",
    )
    parser.add_argument(
        "--trace",
        type=str,
        default=str(DEFAULT_PIPELINE_TRACE_PATH),
        help="Path to write the structured execution trace JSON.",
    )

    args = parser.parse_args()

    out_file = Path(args.out)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    trace_file = Path(args.trace)
    trace_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        if args.all_checkpoints:
            all_res = run_all_checkpoint_pipelines(mode=args.mode)
            for k, data in all_res.items():
                print(f"=== CHECKPOINT: {k} ===")
                print(data["output_text"])
                print()
            with open(trace_file, "w", encoding="utf-8") as f:
                json.dump(all_res, f, indent=2)
        elif args.case:
            formatted_block, trace_dict = run_pipeline_for_case(
                args.case, mode=args.mode
            )
            print(formatted_block)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(formatted_block + "\n")
            with open(trace_file, "w", encoding="utf-8") as f:
                json.dump(trace_dict, f, indent=2)
        elif args.reels:
            reels = [r.strip() for r in args.reels.split(",") if r.strip()]
            formatted_block, trace_dict = run_pipeline_for_reels(
                reels, mode=args.mode
            )
            print(formatted_block)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(formatted_block + "\n")
            with open(trace_file, "w", encoding="utf-8") as f:
                json.dump(trace_dict, f, indent=2)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
