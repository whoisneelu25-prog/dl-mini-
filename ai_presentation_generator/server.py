"""
FastAPI Backend Server for AI Presentation Generator.

Provides REST API endpoints connecting the modern web frontend
to the deep learning and NLP generation pipeline.
"""

import os
import sys
import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pipeline import PresentationPipeline
from utils import export_to_pptx, export_to_markdown, export_to_json, get_system_info, validate_input

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("server")

app = FastAPI(
    title="AI Presentation Generator API",
    description="Sequence-to-Sequence Outline Generation using FLAN-T5 & Sentence-BERT",
    version="1.1.0",
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Output directory for presentation files
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory session store
presentations_cache: Dict[str, Dict[str, Any]] = {}


class GenerateRequest(BaseModel):
    topic: str = Field(..., description="Presentation Topic")
    objective: str = Field(..., description="Presentation Objective")
    audience: str = Field("College Students", description="Target Audience")
    difficulty: str = Field("Intermediate", description="Difficulty Level")
    presentation_type: str = Field("Technical Seminar", description="Presentation Type")
    num_slides: int = Field(8, ge=3, le=20, description="Slide Count (3-20)")
    duration: int = Field(12, ge=3, le=60, description="Duration in minutes (3-60)")


class RegenerateSlideRequest(BaseModel):
    presentation_id: str
    slide_number: int


class RefineRequest(BaseModel):
    presentation_id: str


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Presentation Generator",
        "system": get_system_info(),
    }


@app.get("/system-info")
def system_info():
    return get_system_info()


@app.post("/generate")
def generate_presentation(payload: GenerateRequest):
    data = payload.model_dump()
    if not data.get("objective") or len(str(data["objective"]).strip()) < 5:
        data["objective"] = f"Comprehensive presentation and practical overview of {data.get('topic', 'the topic')}."
    valid, errors = validate_input(data)
    if not valid:
        raise HTTPException(status_code=400, detail={"errors": errors})

    try:
        pipeline = PresentationPipeline.get_singleton()
        presentation = pipeline.run_pipeline(data)
        presentations_cache[presentation["id"]] = presentation
        return presentation
    except Exception as e:
        logger.exception("Pipeline generation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/presentation/{pres_id}")
def get_presentation(pres_id: str):
    if pres_id not in presentations_cache:
        raise HTTPException(status_code=404, detail="Presentation not found")
    return presentations_cache[pres_id]


@app.post("/regenerate-slide")
def regenerate_slide(payload: RegenerateSlideRequest):
    pres = presentations_cache.get(payload.presentation_id)
    if not pres:
        raise HTTPException(status_code=404, detail="Presentation not found")

    target_slide = None
    target_idx = -1
    for i, s in enumerate(pres["slides"]):
        if s["slide_number"] == payload.slide_number:
            target_slide = s
            target_idx = i
            break

    if target_slide is None:
        raise HTTPException(status_code=404, detail=f"Slide {payload.slide_number} not found")

    pipeline = PresentationPipeline.get_singleton()
    new_bullets = pipeline.transformer_engine.generate_bullets(
        topic=pres["topic"],
        objective=pres.get("objective", ""),
        audience=pres.get("audience", "College Students"),
        difficulty=pres.get("difficulty", "Intermediate"),
        presentation_type=pres.get("presentation_type", "Technical Seminar"),
        slide_title=target_slide["title"],
        slide_purpose=target_slide["purpose"],
        count=len(target_slide["bullets"]) or 4,
    )
    new_case = pipeline.transformer_engine.generate_case_study(
        topic=pres["topic"],
        slide_title=target_slide["title"],
        domain=pres.get("domain", "Technology"),
    )
    new_notes = pipeline.transformer_engine.generate_speaker_notes(
        topic=pres["topic"],
        slide_title=target_slide["title"],
        bullets=new_bullets,
        audience=pres.get("audience", "College Students"),
        time_minutes=target_slide["time_minutes"],
    )

    pres["slides"][target_idx]["bullets"] = new_bullets
    pres["slides"][target_idx]["case_study"] = new_case
    pres["slides"][target_idx]["speaker_notes"] = new_notes

    return pres["slides"][target_idx]


@app.post("/refine")
def refine_presentation(payload: RefineRequest):
    pres = presentations_cache.get(payload.presentation_id)
    if not pres:
        raise HTTPException(status_code=404, detail="Presentation not found")

    pipeline = PresentationPipeline.get_singleton()
    refine_result = pipeline.refiner.refine_presentation(pres["slides"], pres["topic"])
    pres["slides"] = refine_result["slides"]
    pres["redundant_points_detected"] += refine_result["redundant_points_detected"]
    pres["points_refined"] += refine_result["points_refined"]
    return pres


def _resolve_presentation(payload: Dict[str, Any]) -> Dict[str, Any]:
    pres_id = payload.get("id")
    if "slides" in payload and payload.get("slides"):
        if pres_id:
            presentations_cache[pres_id] = payload
        return payload
    if pres_id and pres_id in presentations_cache:
        return presentations_cache[pres_id]
    return {}


@app.post("/export/pptx")
def export_pptx_endpoint(payload: Dict[str, Any]):
    pres = _resolve_presentation(payload)
    if not pres or "slides" not in pres:
        raise HTTPException(status_code=400, detail="Invalid presentation data")

    file_name = f"presentation_{pres.get('id', 'export')}.pptx"
    out_path = os.path.join(OUTPUT_DIR, file_name)
    export_to_pptx(pres, out_path)
    return FileResponse(out_path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", filename=file_name)


@app.post("/export/markdown")
def export_markdown_endpoint(payload: Dict[str, Any]):
    pres = _resolve_presentation(payload)
    if not pres or "slides" not in pres:
        raise HTTPException(status_code=400, detail="Invalid presentation data")

    file_name = f"presentation_{pres.get('id', 'export')}.md"
    out_path = os.path.join(OUTPUT_DIR, file_name)
    export_to_markdown(pres, out_path)
    return FileResponse(out_path, media_type="text/markdown", filename=file_name)


@app.post("/export/json")
def export_json_endpoint(payload: Dict[str, Any]):
    pres = _resolve_presentation(payload)
    if not pres or "slides" not in pres:
        raise HTTPException(status_code=400, detail="Invalid presentation data")

    file_name = f"presentation_{pres.get('id', 'export')}.json"
    out_path = os.path.join(OUTPUT_DIR, file_name)
    export_to_json(pres, out_path)
    return FileResponse(out_path, media_type="application/json", filename=file_name)


# Mount static frontend directory
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
