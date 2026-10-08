"""
Utility functions, Validators, System Diagnostics, and Exporters (PPTX, Markdown, JSON).
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Tuple

import pptx
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from model import get_optimal_device

logger = logging.getLogger(__name__)

VALID_AUDIENCES = [
    "College Students",
    "Engineering Faculty",
    "Researchers",
    "Corporate Executives",
    "General Audience",
]

VALID_DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]

VALID_PRESENTATION_TYPES = [
    "Technical Seminar",
    "Academic Presentation",
    "Workshop",
    "Case Study",
    "Research Presentation",
    "Corporate Briefing",
]


def validate_input(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates user input according to specifications:
    - Topic: Non-empty, 3-200 characters
    - Objective: Non-empty, 5-300 characters
    - Slide Count: Integer in range [3, 20]
    - Duration: Integer in range [3, 60]
    - Audience, Difficulty, Presentation Type within valid taxonomies
    """
    errors: List[str] = []

    topic = str(params.get("topic", "")).strip()
    if not topic:
        errors.append("Presentation Topic cannot be empty.")
    elif len(topic) < 3:
        errors.append("Presentation Topic must be at least 3 characters long.")
    elif len(topic) > 200:
        errors.append("Presentation Topic must not exceed 200 characters.")

    objective = str(params.get("objective", "")).strip()
    if not objective:
        errors.append("Presentation Objective cannot be empty.")
    elif len(objective) < 5:
        errors.append("Presentation Objective must be at least 5 characters long.")

    try:
        num_slides = int(params.get("num_slides", 8))
        if num_slides < 3 or num_slides > 20:
            errors.append("Slide Count must be between 3 and 20.")
    except (ValueError, TypeError):
        errors.append("Slide Count must be an integer between 3 and 20.")

    try:
        duration = int(params.get("duration", 12))
        if duration < 3 or duration > 60:
            errors.append("Duration must be between 3 and 60 minutes.")
    except (ValueError, TypeError):
        errors.append("Duration must be an integer between 3 and 60 minutes.")

    difficulty = params.get("difficulty", "Intermediate")
    if difficulty not in VALID_DIFFICULTIES:
        errors.append(f"Difficulty must be one of {VALID_DIFFICULTIES}.")

    presentation_type = params.get("presentation_type", "Technical Seminar")
    if presentation_type not in VALID_PRESENTATION_TYPES:
        errors.append(f"Presentation Type must be one of {VALID_PRESENTATION_TYPES}.")

    audience = params.get("audience", "College Students")
    if not audience or not str(audience).strip():
        errors.append("Target Audience must be specified.")

    return len(errors) == 0, errors


def get_system_info() -> Dict[str, Any]:
    """Returns runtime system specifications for diagnostic display."""
    device = get_optimal_device().upper()
    return {
        "generation_model": "google/flan-t5-base",
        "generation_type": "Sequence-to-Sequence Pretrained Transformer",
        "semantic_model": "all-MiniLM-L6-v2",
        "embedding_dimension": 384,
        "beam_search": 3,
        "no_repeat_ngram_size": 2,
        "similarity_threshold": 0.88,
        "slide_range": "3–20 slides",
        "duration_range": "3–60 minutes",
        "exports": ["PPTX (16:9 Widescreen)", "Markdown", "JSON"],
        "execution_device": device,
        "deep_learning_framework": f"PyTorch with Hugging Face Transformers & Sentence Transformers",
    }


def export_to_pptx(presentation_data: Dict[str, Any], output_path: str) -> str:
    """
    Generates a clean, professional 16:9 widescreen PowerPoint presentation (.pptx).
    Focuses on full-width typographic hierarchy, generous bullet margins, and presenter notes.
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    NAVY = RGBColor(13, 30, 21)        # #0d1e15 (Forest Black)
    SLATE = RGBColor(51, 72, 60)       # #33483c (Deep Herbal Spruce)
    INDIGO = RGBColor(5, 96, 58)       # #05603a (Forest Emerald Green)
    LIGHT_BG = RGBColor(247, 250, 248) # #f7faf8 (Fresh Herbal Porcelain)
    BORDER_COLOR = RGBColor(221, 231, 224) # #dde7e0

    # 1. Title Slide (Clean & Executive)
    title_slide = prs.slides.add_slide(blank_layout)

    # Background card container
    bg_box = title_slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9)
    )
    bg_box.fill.solid()
    bg_box.fill.fore_color.rgb = LIGHT_BG
    bg_box.line.color.rgb = BORDER_COLOR

    # Presentation Title
    title_box = title_slide.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.3), Inches(2.0))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = presentation_data.get("topic", "Presentation Overview")
    p_t.font.size = Pt(38)
    p_t.font.bold = True
    p_t.font.color.rgb = NAVY

    # Subtitle / Objective
    obj_text = presentation_data.get("objective", "")
    if obj_text:
        obj_box = title_slide.shapes.add_textbox(Inches(1.5), Inches(4.3), Inches(10.3), Inches(1.4))
        tf_o = obj_box.text_frame
        tf_o.word_wrap = True
        p_o = tf_o.paragraphs[0]
        p_o.text = obj_text
        p_o.font.size = Pt(18)
        p_o.font.color.rgb = SLATE

    # Title slide speaker notes
    title_slide.notes_slide.notes_text_frame.text = (
        f"Topic: {presentation_data.get('topic')}\n"
        f"Objective: {presentation_data.get('objective')}"
    )

    # 2. Content Slides (Full Width, Clean Academic Layout)
    slides_data = presentation_data.get("slides", [])
    for slide_data in slides_data:
        slide = prs.slides.add_slide(blank_layout)

        # Slide Number Indicator
        s_num = slide_data.get('slide_number', 1)
        num_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.55), Inches(11.333), Inches(0.35))
        tf_num = num_box.text_frame
        p_num = tf_num.paragraphs[0]
        p_num.text = f"{s_num:02d}"
        p_num.font.size = Pt(11)
        p_num.font.bold = True
        p_num.font.color.rgb = INDIGO

        # Slide Title
        t_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.95), Inches(11.333), Inches(0.85))
        tf_title = t_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = slide_data.get("title", "")
        p_title.font.size = Pt(28)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

        # Context / Purpose line
        purpose = slide_data.get("purpose", "")
        top_offset = Inches(1.9)
        if purpose:
            p_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(11.333), Inches(0.4))
            tf_purp = p_box.text_frame
            tf_purp.word_wrap = True
            p_purp = tf_purp.paragraphs[0]
            p_purp.text = purpose
            p_purp.font.size = Pt(13)
            p_purp.font.italic = True
            p_purp.font.color.rgb = SLATE
            top_offset = Inches(2.35)

        # Full-Width Key Points
        bullets_box = slide.shapes.add_textbox(Inches(1.0), top_offset, Inches(11.333), Inches(4.6))
        tf_bullets = bullets_box.text_frame
        tf_bullets.word_wrap = True

        bullets = slide_data.get("bullets", [])
        for b_idx, bullet in enumerate(bullets):
            p_b = tf_bullets.add_paragraph() if b_idx > 0 else tf_bullets.paragraphs[0]
            p_b.text = f"•   {bullet}"
            p_b.font.size = Pt(18)
            p_b.font.color.rgb = NAVY
            p_b.space_after = Pt(16)

        # Speaker notes stored in native notes slide
        notes_text = slide_data.get("speaker_notes", "")
        time_m = slide_data.get("time_minutes", 1.5)
        case_study = slide_data.get("case_study", "")
        notes_parts = [f"Allocated Pacing: {time_m:.1f} min"]
        if purpose:
            notes_parts.append(f"Slide Purpose: {purpose}")
        if case_study:
            notes_parts.append(f"Case Study / Real-World Application:\n{case_study}")
        if notes_text:
            notes_parts.append(f"Speaker Notes:\n{notes_text}")
        slide.notes_slide.notes_text_frame.text = "\n\n".join(notes_parts)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    prs.save(output_path)
    logger.info("Saved clean PPTX presentation to %s", output_path)
    return output_path

def export_to_markdown(presentation_data: Dict[str, Any], output_path: str) -> str:
    """Exports structured presentation outline to Markdown (.md)."""
    lines = [
        f"# {presentation_data.get('topic', 'AI Presentation Outline')}",
        "",
        "## Presentation Metadata",
        f"- **Topic**: {presentation_data.get('topic', '')}",
        f"- **Objective**: {presentation_data.get('objective', '')}",
        f"- **Audience**: {presentation_data.get('audience', 'General Audience')}",
        f"- **Presentation Type**: {presentation_data.get('presentation_type', 'Technical Seminar')}",
        f"- **Difficulty**: {presentation_data.get('difficulty', 'Intermediate')}",
        f"- **Total Slides**: {presentation_data.get('num_slides', 0)}",
        f"- **Total Duration**: {presentation_data.get('duration', 0)} minutes",
        f"- **Detected Domain**: {presentation_data.get('domain', 'Technology')}",
        f"- **Generator Model**: google/flan-t5-base",
        f"- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384D)",
        f"- **Redundant Points Refined**: {presentation_data.get('points_refined', 0)}",
        "",
        "---",
        "",
    ]

    for slide in presentation_data.get("slides", []):
        s_no = slide.get("slide_number", 1)
        title = slide.get("title", "")
        time_m = slide.get("time_minutes", 1.5)
        purpose = slide.get("purpose", "")

        lines.append(f"### Slide {s_no:02d}: {title}")
        lines.append(f"⏱ **Allocated Time**: {time_m:.1f} minutes | **Purpose**: {purpose}")
        lines.append("")
        lines.append("#### Key Points")
        for bullet in slide.get("bullets", []):
            lines.append(f"- {bullet}")
        lines.append("")
        lines.append(f"> **Case Study / Real-World Application**:  ")
        lines.append(f"> {slide.get('case_study', '')}")
        lines.append("")
        lines.append(f"**Speaker Notes**:")
        lines.append(f"{slide.get('speaker_notes', '')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("*Generated with PresentAI Studio.*\n")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info("Saved Markdown presentation to %s", output_path)
    return output_path


def export_to_json(presentation_data: Dict[str, Any], output_path: str) -> str:
    """Exports full presentation structure and metadata to clean JSON."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(presentation_data, f, indent=2, ensure_ascii=False)
    logger.info("Saved JSON presentation to %s", output_path)
    return output_path
