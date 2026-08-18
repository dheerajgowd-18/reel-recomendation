"""Local demo UI server for ScrollSense using FastAPI."""

from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Literal

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.baselines import get_watched_reels_by_ids, run_all_baselines_for_reels
from src.config import (
    LLM_API_KEY,
    LLM_MODEL,
    LLM_PROVIDER,
    OUTPUT_DIR,
)
from src.gate import load_or_generate_gate_cache
from src.infer import infer_interests
from src.pipeline import run_pipeline_for_reels

app = FastAPI(title="ScrollSense Demo Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """Inject strict security headers into all HTTP responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


STATIC_DIR = Path(__file__).resolve().parent / "static"
DEMO_TRACE_FILE = OUTPUT_DIR / "demo_trace.json"

ALLOWED_CASES = Literal[
    "trap_java_to_swe",
    "non_trap_gaming_only",
    "trap_after_R1",
    "trap_after_R1_R2",
    "trap_after_R1_R2_R3",
    "trap_after_R1_R2_R3_R4",
]


class RunRequest(BaseModel):
    model_config = {"extra": "forbid"}

    case: ALLOWED_CASES = Field(default="trap_java_to_swe", description="Named test case or checkpoint")
    extractor: Literal["deterministic", "ai", "hybrid"] = Field(default="hybrid", description="deterministic | ai | hybrid")
    explainer: Literal["deterministic", "ai", "hybrid"] = Field(default="hybrid", description="deterministic | ai | hybrid")
    llm_provider: Literal["cache", "mock", "gemini", "openai_compatible"] = Field(default="cache", description="cache | mock | gemini | openai_compatible")
    run_baselines: bool = Field(default=True, description="Whether to include naive baselines")


@app.get("/")
def serve_index() -> FileResponse:
    """Serve local HTML page."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.is_file():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_file)


@app.get("/api/health")
def api_health() -> Dict[str, Any]:
    """Health status and configuration check."""
    api_key_configured = bool(os.getenv("LLM_API_KEY", LLM_API_KEY).strip())
    llm_status = "live configured" if api_key_configured else "cache only"
    return {
        "status": "ok",
        "pipeline": "ready",
        "llm_model": LLM_MODEL,
        "llm_provider_default": os.getenv("LLM_PROVIDER", LLM_PROVIDER),
        "llm_status": llm_status,
        "api_key_configured": api_key_configured,
        "offline_ready": True,
    }


@app.get("/api/cases")
def api_cases() -> List[str]:
    """Return available regression and checkpoint test cases."""
    return [
        "trap_java_to_swe",
        "non_trap_gaming_only",
        "trap_after_R1",
        "trap_after_R1_R2",
        "trap_after_R1_R2_R3",
    ]


@app.get("/api/cached-demo")
def api_cached_demo() -> Dict[str, Any]:
    """Return precomputed demo artifacts for emergency demo fallback."""
    if DEMO_TRACE_FILE.is_file():
        try:
            with open(DEMO_TRACE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # In-memory fallback if file is missing on ephemeral disk
    from src.demo import run_demo
    return run_demo(all_cases=True)


@app.post("/api/run")
def api_run(req: RunRequest) -> Dict[str, Any]:
    """Execute pipeline and baselines for the requested case."""
    case_reels_map = {
        "trap_java_to_swe": ["R1", "R2", "R3", "R4"],
        "non_trap_gaming_only": ["R5", "R6", "R7"],
        "trap_after_R1": ["R1"],
        "trap_after_R1_R2": ["R1", "R2"],
        "trap_after_R1_R2_R3": ["R1", "R2", "R3"],
        "trap_after_R1_R2_R3_R4": ["R1", "R2", "R3", "R4"],
    }

    if req.case not in case_reels_map:
        raise HTTPException(status_code=400, detail=f"Unknown case: '{req.case}'. Allowed: {list(case_reels_map.keys())}")

    reel_ids = case_reels_map[req.case]
    watched_items = get_watched_reels_by_ids(reel_ids)

    # Provider security check
    api_key_configured = bool(os.getenv("LLM_API_KEY", LLM_API_KEY).strip())
    effective_provider = req.llm_provider
    if effective_provider == "openai_compatible" and not api_key_configured:
        effective_provider = "cache"

    # 1. Run baselines if requested
    baselines_data: Dict[str, Any] = {}
    if req.run_baselines:
        baselines_data = run_all_baselines_for_reels(reel_ids, case_name=req.case)

    # 2. Run real ScrollSense pipeline
    try:
        formatted_block, trace_dict = run_pipeline_for_reels(
            reel_ids,
            mode="real",
            case_name=req.case,
            extractor=req.extractor,
            explainer=req.explainer,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {exc}")

    # 3. Assemble gate rejection explanations
    gate_cache = load_or_generate_gate_cache()
    rejected_list: List[Dict[str, str]] = []
    for cid in trace_dict.get("gate_summary", {}).get("rejected_ids", []):
        if cid in gate_cache:
            rejected_list.append({
                "candidate_id": cid,
                "title": gate_cache[cid].get("title", cid),
                "rejection_reason": gate_cache[cid].get("rejection_reason", "Gate rejected"),
            })

    # 4. Extract activations
    inf_obj = infer_interests(reel_ids, case_name=req.case)
    graph_acts = [a["node"] for a in inf_obj.get("graph_traversal", {}).get("activated_nodes", [])]

    rank_sum = trace_dict.get("ranking_summary", {})
    inf_sum = trace_dict.get("inference_summary", {})
    expl_sum = trace_dict.get("explanation_summary", {})
    ai_meta = trace_dict.get("ai", {})

    scrollsense_data = {
        "output_block": formatted_block,
        "interest_detected": expl_sum.get("interest_label", ""),
        "recommended_candidate_id": rank_sum.get("top_candidate_id", ""),
        "recommended_title": rank_sum.get("top_candidate_title", ""),
        "category": "Career" if "Career" in formatted_block else ("AI" if "AI" in formatted_block else "Other"),
        "confidence": inf_sum.get("confidence", "Low"),
        "top_identity": inf_sum.get("top_professional_identity", ""),
        "top_goals": inf_sum.get("top_goals", []),
        "graph_activations": graph_acts,
        "gate_rejections": rejected_list,
        "ranking_summary": rank_sum,
        "ai": {
            "model": ai_meta.get("model", LLM_MODEL),
            "extractor": req.extractor,
            "explainer": req.explainer,
            "llm_provider": effective_provider,
            "llm_status": ai_meta.get("llm_status", "cached"),
            "fallback_used": ai_meta.get("fallback_used", False),
        },
    }

    return {
        "case": req.case,
        "watched_reels": [
            {
                "reel_id": r.get("reel_id", ""),
                "title": r.get("title", ""),
                "topic": r.get("topic", ""),
                "content_type": r.get("content_type", ""),
            }
            for r in watched_items
        ],
        "baselines": baselines_data,
        "scrollsense": scrollsense_data,
        "trace": trace_dict,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


# Mount static assets directory
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def main() -> None:
    """Run server with uvicorn."""
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting ScrollSense UI Server on http://{host}:{port}")
    uvicorn.run("ui.server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
