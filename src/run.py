"""CLI Entrypoint for ScrollSense Recommendation Agent."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.config import DEFAULT_RESULT_PATH, DEFAULT_TRACE_PATH
from src.stub_pipeline import run_stub_pipeline


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
    parser.add_argument(
        "--out",
        type=str,
        default=str(DEFAULT_RESULT_PATH),
        help="Path to write the formatted plain-text result block.",
    )
    parser.add_argument(
        "--trace",
        type=str,
        default=str(DEFAULT_TRACE_PATH),
        help="Path to write the structured execution trace JSON.",
    )

    args = parser.parse_args()

    try:
        formatted_block, _ = run_stub_pipeline(
            reels=args.reels,
            case=args.case,
            out_path=args.out,
            trace_path=args.trace,
        )
        print(formatted_block)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
