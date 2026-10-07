import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model import EmbeddingEngine, TransformerEngine
from generator import ContentPlanner, SlideGenerator, ContentRefiner
from preprocessing import TopicAnalyzer


@pytest.fixture(scope="module")
def engines():
    emb = EmbeddingEngine()
    tf = TransformerEngine()
    return emb, tf


def test_transformer_generation_non_empty(engines):
    _, transformer = engines
    prompt = "Topic: AI in Healthcare\nSlide Title: Diagnosis\nTask: Write one bullet point."
    res = transformer.generate_text(prompt, max_length=64)
    assert res is not None
    assert len(res.strip()) > 0


def test_slide_generation_structure(engines):
    embedding, transformer = engines
    planner = ContentPlanner()
    generator = SlideGenerator(transformer, TopicAnalyzer())

    plan = planner.plan_structure(
        topic="Artificial Intelligence in Healthcare",
        num_slides=3,
        duration_mins=6,
    )
    slides = generator.generate_presentation(
        topic="Artificial Intelligence in Healthcare",
        objective="Explain AI transformation in diagnostics",
        audience="College Students",
        difficulty="Intermediate",
        presentation_type="Technical Seminar",
        planned_slides=plan,
    )

    assert len(slides) == 3
    for s in slides:
        assert "slide_number" in s
        assert "title" in s
        assert "purpose" in s
        assert "time_minutes" in s
        assert "bullets" in s
        assert "case_study" in s
        assert "speaker_notes" in s
        assert isinstance(s["bullets"], list)
        assert len(s["bullets"]) >= 3
        assert len(s["case_study"]) > 5
        assert len(s["speaker_notes"]) > 5


def test_content_refiner_redundancy_detection(engines):
    embedding, transformer = engines
    refiner = ContentRefiner(embedding, transformer, threshold=0.88)

    # Deliberately inject near-identical redundant bullets
    test_slides = [
        {
            "slide_number": 1,
            "title": "Clinical AI Diagnosis",
            "purpose": "Explain diagnostic AI algorithms",
            "time_minutes": 2.0,
            "bullets": [
                "Machine learning algorithms automate diagnostic radiology detection.",
                "Machine learning algorithms automate diagnostic radiology detection.", # identical duplicate
                "Deep convolutional neural networks assist clinical pathologists.",
            ],
            "case_study": "FDA-approved AI detection tool in hospital radiology.",
            "speaker_notes": "Walk through automated diagnostic detection and convolutional networks.",
        }
    ]

    result = refiner.refine_presentation(
        slides=test_slides,
        topic="Artificial Intelligence in Healthcare",
    )

    assert result["refinement_completed"] is True
    assert result["redundant_points_detected"] >= 1
    assert result["points_refined"] >= 1
    refined_bullets = result["slides"][0]["bullets"]
    assert len(refined_bullets) == 3
    # Check that duplicate was modified
    assert refined_bullets[0] != refined_bullets[1]
