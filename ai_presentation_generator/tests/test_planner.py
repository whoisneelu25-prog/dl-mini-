import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generator import ContentPlanner


@pytest.fixture
def planner():
    return ContentPlanner()


@pytest.mark.parametrize("requested_count", [3, 4, 8, 12, 15, 20])
def test_exact_slide_count_guarantee(planner, requested_count):
    plan = planner.plan_structure(
        topic="Artificial Intelligence in Healthcare",
        num_slides=requested_count,
        duration_mins=15,
    )
    assert len(plan) == requested_count
    # Check 1-indexed sequential ordering
    for i, slide in enumerate(plan):
        assert slide["slide_number"] == i + 1


def test_first_and_final_slide_conventions(planner):
    plan = planner.plan_structure(
        topic="Artificial Intelligence in Healthcare",
        num_slides=8,
        duration_mins=12,
    )
    assert "Introduction" in plan[0]["title"]
    assert "Conclusion" in plan[-1]["title"]
    assert plan[0]["section_type"] == "intro"
    assert plan[-1]["section_type"] == "conclusion"


@pytest.mark.parametrize("duration,num_slides", [(12, 8), (30, 15), (45, 20), (5, 3)])
def test_duration_allocation_sum(planner, duration, num_slides):
    plan = planner.plan_structure(
        topic="Deep Learning in Medical Imaging",
        num_slides=num_slides,
        duration_mins=duration,
    )
    total_time = sum(s["time_minutes"] for s in plan)
    assert pytest.approx(total_time, abs=0.2) == duration


def test_intermediate_academic_progression(planner):
    plan = planner.plan_structure(
        topic="Artificial Intelligence in Healthcare",
        num_slides=8,
        duration_mins=12,
    )
    section_types = [s["section_type"] for s in plan]
    # Check logical flow: intro -> background/architecture/methodology/applications -> conclusion
    assert section_types[0] == "intro"
    assert section_types[-1] == "conclusion"
    assert "applications" in section_types or "concepts" in section_types
