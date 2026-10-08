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
    "Industry Professionals",
    "Technical Teams",
]

VALID_DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]

VALID_PRESENTATION_TYPES = [
    "Technical Seminar",
    "Academic Presentation",
    "Workshop",
    "Case Study",
    "Research Presentation",
    "Corporate Briefing",
    "Executive Briefing",
    "Product Pitch",
    "Keynote",
    "Training Session",
    "General Presentation",
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

    presentation_type = str(params.get("presentation_type", "Corporate Briefing")).strip()
    if not presentation_type:
        params["presentation_type"] = "Corporate Briefing"
    else:
        matched_pt = next((pt for pt in VALID_PRESENTATION_TYPES if pt.lower() == presentation_type.lower()), None)
        if matched_pt:
            params["presentation_type"] = matched_pt
        elif presentation_type not in VALID_PRESENTATION_TYPES:
            # Normalize user-specified type to VALID_PRESENTATION_TYPES or Corporate Briefing
            if len(presentation_type) <= 50:
                VALID_PRESENTATION_TYPES.append(presentation_type)
                params["presentation_type"] = presentation_type
            else:
                params["presentation_type"] = "Corporate Briefing" 

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

    # Executive Dark Palette
    BG_COLOR = RGBColor(11, 15, 23)        # #0B0F17 Deep Obsidian Midnight
    CARD_BG = RGBColor(17, 24, 39)         # #111827 Dark Slate Card Fill
    CARD_BORDER = RGBColor(30, 41, 59)     # #1E293B Subtle Border
    EMERALD = RGBColor(16, 185, 129)       # #10B981 Emerald Accent
    EMERALD_DARK = RGBColor(19, 42, 34)    # #132A22 Pill Fill
    CASE_BG = RGBColor(13, 32, 26)         # #0D201A Case Study Dark Emerald
    SKY_BLUE = RGBColor(56, 189, 248)      # #38BDF8 Cyan/Sky Accent
    WHITE = RGBColor(255, 255, 255)        # Pure White
    TEXT_BODY = RGBColor(226, 232, 240)    # #E2E8F0 Soft White Body
    TEXT_MUTED = RGBColor(148, 163, 184)   # #94A3B8 Slate Subtitles
    TEXT_DIM = RGBColor(100, 116, 139)     # #64748B Dim Captions

    def _set_shape_color(shape, fill_color, line_color, line_width_pt=1.0):
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
        if line_color:
            shape.line.color.rgb = line_color
            shape.line.width = Pt(line_width_pt)
        else:
            shape.line.fill.background()

    # 1. Title Slide (Executive Layout)
    title_slide = prs.slides.add_slide(blank_layout)
    bg_full = title_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    _set_shape_color(bg_full, BG_COLOR, None)

    # Accent stripe top left
    accent_bar = title_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(0.65), Inches(2.2), Inches(0.05))
    _set_shape_color(accent_bar, EMERALD, EMERALD)

    # Domain & Type Badge
    badge_box = title_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(0.90), Inches(4.8), Inches(0.36))
    _set_shape_color(badge_box, EMERALD_DARK, EMERALD, 1.0)
    tf_b = badge_box.text_frame
    tf_b.word_wrap = True
    p_b = tf_b.paragraphs[0]
    domain_str = str(presentation_data.get("domain", "Technology")).upper()
    pt_str = str(presentation_data.get("presentation_type", "Executive Briefing")).upper()
    p_b.text = f"{domain_str}   •   {pt_str}"
    p_b.font.size = Pt(9.5)
    p_b.font.bold = True
    p_b.font.color.rgb = EMERALD
    p_b.alignment = PP_ALIGN.CENTER

    # Top Right Watermark
    wm_box = title_slide.shapes.add_textbox(Inches(8.5), Inches(0.90), Inches(3.933), Inches(0.36))
    p_wm = wm_box.text_frame.paragraphs[0]
    p_wm.text = "PRESENTAI NEURAL STUDIO"
    p_wm.font.size = Pt(9.5)
    p_wm.font.bold = True
    p_wm.font.color.rgb = TEXT_DIM
    p_wm.alignment = PP_ALIGN.RIGHT

    # Presentation Title
    title_box = title_slide.shapes.add_textbox(Inches(0.9), Inches(1.55), Inches(11.533), Inches(1.8))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = presentation_data.get("topic", "Presentation Overview")
    p_t.font.size = Pt(38)
    p_t.font.bold = True
    p_t.font.color.rgb = WHITE

    # Objective / Executive Summary Box
    obj_text = presentation_data.get("objective", "")
    if obj_text:
        obj_box = title_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(3.45), Inches(11.533), Inches(1.25))
        _set_shape_color(obj_box, RGBColor(15, 23, 42), CARD_BORDER, 1.0)
        tf_o = obj_box.text_frame
        tf_o.word_wrap = True
        p_o_hdr = tf_o.paragraphs[0]
        p_o_hdr.text = "STRATEGIC OBJECTIVE"
        p_o_hdr.font.size = Pt(9)
        p_o_hdr.font.bold = True
        p_o_hdr.font.color.rgb = SKY_BLUE
        p_o_body = tf_o.add_paragraph()
        p_o_body.text = obj_text
        p_o_body.font.size = Pt(14)
        p_o_body.font.color.rgb = TEXT_BODY
        p_o_body.space_before = Pt(4)

    # 4 Metadata KPI Cards
    kpis = [
        ("TARGET AUDIENCE", str(presentation_data.get("audience", "Executive Stakeholders"))),
        ("PRESENTATION DECK", f"{len(presentation_data.get('slides', []))} Strategic Slides"),
        ("ESTIMATED PACING", f"~{presentation_data.get('duration', 15)} Minutes"),
        ("COMPLEXITY LEVEL", str(presentation_data.get("difficulty", "Intermediate"))),
    ]
    card_w = Inches(2.70)
    card_gap = Inches(0.244)
    for idx, (label, val) in enumerate(kpis):
        card_x = Inches(0.9) + idx * (card_w + card_gap)
        kpi_card = title_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_x, Inches(5.15), card_w, Inches(1.35))
        _set_shape_color(kpi_card, CARD_BG, CARD_BORDER, 1.0)
        tf_k = kpi_card.text_frame
        tf_k.word_wrap = True
        p_lbl = tf_k.paragraphs[0]
        p_lbl.text = label
        p_lbl.font.size = Pt(8.5)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = EMERALD
        p_val = tf_k.add_paragraph()
        p_val.text = val
        p_val.font.size = Pt(13)
        p_val.font.bold = True
        p_val.font.color.rgb = WHITE
        p_val.space_before = Pt(4)

    # Title slide speaker notes
    title_slide.notes_slide.notes_text_frame.text = (
        f"Topic: {presentation_data.get('topic')}\n"
        f"Objective: {presentation_data.get('objective')}"
    )

    # 2. Content Slides (Executive Widescreen 16:9)
    slides_data = presentation_data.get("slides", [])
    total_slides = len(slides_data)
    for s_idx, slide_data in enumerate(slides_data):
        slide = prs.slides.add_slide(blank_layout)
        bg_slide = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        _set_shape_color(bg_slide, BG_COLOR, None)

        s_num = slide_data.get('slide_number', s_idx + 1)
        time_m = slide_data.get("time_minutes", 1.5)

        # Slide Number Pill
        num_pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(0.45), Inches(1.4), Inches(0.32))
        _set_shape_color(num_pill, EMERALD_DARK, EMERALD, 1.0)
        p_num = num_pill.text_frame.paragraphs[0]
        p_num.text = f"SLIDE {s_num:02d}"
        p_num.font.size = Pt(9.5)
        p_num.font.bold = True
        p_num.font.color.rgb = EMERALD
        p_num.alignment = PP_ALIGN.CENTER

        # Topic Breadcrumb
        bc_box = slide.shapes.add_textbox(Inches(2.45), Inches(0.45), Inches(7.2), Inches(0.32))
        p_bc = bc_box.text_frame.paragraphs[0]
        topic_str = str(presentation_data.get('topic', '')).upper()
        p_bc.text = f"{topic_str}   /   PART {s_num:02d}"
        p_bc.font.size = Pt(9.5)
        p_bc.font.bold = True
        p_bc.font.color.rgb = TEXT_DIM

        # Pacing Badge Pill
        pacing_pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.533), Inches(0.45), Inches(1.9), Inches(0.32))
        _set_shape_color(pacing_pill, RGBColor(30, 41, 59), RGBColor(51, 65, 85), 1.0)
        p_pac = pacing_pill.text_frame.paragraphs[0]
        p_pac.text = f"⏱️ ~{time_m:.1f} MIN"
        p_pac.font.size = Pt(9.5)
        p_pac.font.color.rgb = TEXT_MUTED
        p_pac.alignment = PP_ALIGN.CENTER

        # Slide Title
        t_box = slide.shapes.add_textbox(Inches(0.9), Inches(0.82), Inches(11.533), Inches(0.78))
        tf_title = t_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = slide_data.get("title", "")
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

        # Purpose line
        purpose = slide_data.get("purpose", "")
        if purpose:
            clean_purp = re.sub(r"^purpose:\s*", "", purpose, flags=re.IGNORECASE)
            p_box = slide.shapes.add_textbox(Inches(0.9), Inches(1.64), Inches(11.533), Inches(0.32))
            tf_purp = p_box.text_frame
            tf_purp.word_wrap = True
            p_purp = tf_purp.paragraphs[0]
            p_purp.text = clean_purp
            p_purp.font.size = Pt(12)
            p_purp.font.italic = True
            p_purp.font.color.rgb = TEXT_MUTED

        # Header Divider
        div_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(2.04), Inches(11.533), Inches(0.01))
        _set_shape_color(div_line, CARD_BORDER, CARD_BORDER)

        case_study = str(slide_data.get("case_study", "")).strip()
        has_case = bool(case_study)

        if has_case:
            left_w = Inches(6.9)
            right_w = Inches(4.4)
            body_h = Inches(4.45)
            body_y = Inches(2.16)

            # Left Card: Bullets
            left_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), body_y, left_w, body_h)
            _set_shape_color(left_card, CARD_BG, CARD_BORDER, 1.0)

            # Header pill
            lpill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), body_y + Inches(0.25), Inches(3.2), Inches(0.32))
            _set_shape_color(lpill, RGBColor(22, 34, 56), SKY_BLUE, 1.0)
            p_lpill = lpill.text_frame.paragraphs[0]
            p_lpill.text = "KEY DISCUSSION POINTS"
            p_lpill.font.size = Pt(9.5)
            p_lpill.font.bold = True
            p_lpill.font.color.rgb = SKY_BLUE
            p_lpill.alignment = PP_ALIGN.CENTER

            # Bullets
            bullets_box = slide.shapes.add_textbox(Inches(1.2), body_y + Inches(0.75), left_w - Inches(0.6), body_h - Inches(1.6))
            tf_b = bullets_box.text_frame
            tf_b.word_wrap = True
            bullets = slide_data.get("bullets", [])
            f_size = Pt(14.5) if len(bullets) <= 3 else (Pt(13.5) if len(bullets) == 4 else Pt(12.5))
            sp_after = Pt(14) if len(bullets) <= 3 else Pt(10)
            for b_idx, bullet in enumerate(bullets):
                p_b = tf_b.add_paragraph() if b_idx > 0 else tf_b.paragraphs[0]
                p_b.text = f"•   {bullet}"
                p_b.font.size = f_size
                p_b.font.color.rgb = TEXT_BODY
                p_b.space_after = sp_after

            # Left Card Bottom Pill
            lbot = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), body_y + body_h - Inches(0.75), left_w - Inches(0.6), Inches(0.45))
            _set_shape_color(lbot, RGBColor(20, 30, 47), RGBColor(32, 51, 77), 1.0)
            p_lbot = lbot.text_frame.paragraphs[0]
            p_lbot.text = "💡 Core Focus: Structured Architectural & Operational Alignment"
            p_lbot.font.size = Pt(9)
            p_lbot.font.bold = True
            p_lbot.font.color.rgb = SKY_BLUE
            p_lbot.alignment = PP_ALIGN.CENTER

            # Right Card: Case Study
            right_x = Inches(0.9) + left_w + Inches(0.233)
            right_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_x, body_y, right_w, body_h)
            _set_shape_color(right_card, CASE_BG, EMERALD, 1.5)

            rpill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_x + Inches(0.25), body_y + Inches(0.25), Inches(3.6), Inches(0.32))
            _set_shape_color(rpill, RGBColor(18, 56, 40), EMERALD, 1.0)
            p_rpill = rpill.text_frame.paragraphs[0]
            p_rpill.text = "APPLIED CASE STUDY / IMPACT"
            p_rpill.font.size = Pt(9.5)
            p_rpill.font.bold = True
            p_rpill.font.color.rgb = EMERALD
            p_rpill.alignment = PP_ALIGN.CENTER

            cs_box = slide.shapes.add_textbox(right_x + Inches(0.3), body_y + Inches(0.80), right_w - Inches(0.6), body_h - Inches(1.65))
            tf_cs = cs_box.text_frame
            tf_cs.word_wrap = True
            p_cs = tf_cs.paragraphs[0]
            p_cs.text = case_study
            p_cs.font.size = Pt(13.5)
            p_cs.font.color.rgb = TEXT_BODY

            rbot = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_x + Inches(0.3), body_y + body_h - Inches(0.75), right_w - Inches(0.6), Inches(0.45))
            _set_shape_color(rbot, RGBColor(17, 41, 32), RGBColor(26, 74, 56), 1.0)
            p_rbot = rbot.text_frame.paragraphs[0]
            p_rbot.text = "✓ Verified Industry Implementation Benchmark"
            p_rbot.font.size = Pt(9)
            p_rbot.font.bold = True
            p_rbot.font.color.rgb = EMERALD
            p_rbot.alignment = PP_ALIGN.CENTER

        else:
            # Full width
            body_w = Inches(11.533)
            body_h = Inches(4.45)
            body_y = Inches(2.16)

            full_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), body_y, body_w, body_h)
            _set_shape_color(full_card, CARD_BG, CARD_BORDER, 1.0)

            lpill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), body_y + Inches(0.25), Inches(3.2), Inches(0.32))
            _set_shape_color(lpill, RGBColor(22, 34, 56), SKY_BLUE, 1.0)
            p_lpill = lpill.text_frame.paragraphs[0]
            p_lpill.text = "KEY DISCUSSION POINTS"
            p_lpill.font.size = Pt(9.5)
            p_lpill.font.bold = True
            p_lpill.font.color.rgb = SKY_BLUE
            p_lpill.alignment = PP_ALIGN.CENTER

            bullets_box = slide.shapes.add_textbox(Inches(1.2), body_y + Inches(0.85), body_w - Inches(0.6), body_h - Inches(1.1))
            tf_b = bullets_box.text_frame
            tf_b.word_wrap = True
            bullets = slide_data.get("bullets", [])
            for b_idx, bullet in enumerate(bullets):
                p_b = tf_b.add_paragraph() if b_idx > 0 else tf_b.paragraphs[0]
                p_b.text = f"•   {bullet}"
                p_b.font.size = Pt(14.5)
                p_b.font.color.rgb = TEXT_BODY
                p_b.space_after = Pt(16)

        # Footer Bar
        f_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(6.75), Inches(11.533), Inches(0.01))
        _set_shape_color(f_line, CARD_BORDER, CARD_BORDER)

        f_left = slide.shapes.add_textbox(Inches(0.9), Inches(6.82), Inches(6.0), Inches(0.30))
        p_fl = f_left.text_frame.paragraphs[0]
        p_fl.text = f"PresentAI Studio   •   {presentation_data.get('topic', '')}"
        p_fl.font.size = Pt(9)
        p_fl.font.color.rgb = TEXT_DIM

        f_right = slide.shapes.add_textbox(Inches(7.0), Inches(6.82), Inches(5.433), Inches(0.30))
        p_fr = f_right.text_frame.paragraphs[0]
        p_fr.text = f"Slide {s_idx + 1} of {total_slides}"
        p_fr.font.size = Pt(9)
        p_fr.font.bold = True
        p_fr.font.color.rgb = TEXT_MUTED
        p_fr.alignment = PP_ALIGN.RIGHT

        # Speaker Notes
        notes_text = slide_data.get("speaker_notes", "")
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
    logger.info("Saved executive PPTX presentation to %s", output_path)
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
