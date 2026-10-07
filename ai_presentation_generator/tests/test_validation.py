import pytest
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import validate_input


def test_empty_topic():
    params = {
        "topic": "",
        "objective": "Explain deep learning",
        "num_slides": 8,
        "duration": 15,
    }
    valid, errors = validate_input(params)
    assert not valid
    assert any("Topic cannot be empty" in e for e in errors)


def test_short_topic():
    params = {
        "topic": "AI",
        "objective": "Explain deep learning fundamentals",
        "num_slides": 8,
        "duration": 15,
    }
    valid, errors = validate_input(params)
    assert not valid
    assert any("at least 3 characters" in e for e in errors)


def test_valid_topic():
    params = {
        "topic": "Artificial Intelligence in Healthcare",
        "objective": "Explain deep learning diagnosis",
        "num_slides": 8,
        "duration": 15,
    }
    valid, errors = validate_input(params)
    assert valid
    assert len(errors) == 0


def test_excessively_long_topic():
    params = {
        "topic": "A" * 250,
        "objective": "Explain deep learning diagnosis",
        "num_slides": 8,
        "duration": 15,
    }
    valid, errors = validate_input(params)
    assert not valid
    assert any("must not exceed 200 characters" in e for e in errors)


def test_empty_objective():
    params = {
        "topic": "Artificial Intelligence in Healthcare",
        "objective": "",
        "num_slides": 8,
        "duration": 15,
    }
    valid, errors = validate_input(params)
    assert not valid
    assert any("Objective cannot be empty" in e for e in errors)


def test_slide_count_below_minimum():
    params = {
        "topic": "Artificial Intelligence in Healthcare",
        "objective": "Explain deep learning diagnosis",
        "num_slides": 2,
        "duration": 15,
    }
    valid, errors = validate_input(params)
    assert not valid
    assert any("Slide Count must be between 3 and 20" in e for e in errors)


def test_slide_count_above_maximum():
    params = {
        "topic": "Artificial Intelligence in Healthcare",
        "objective": "Explain deep learning diagnosis",
        "num_slides": 25,
        "duration": 15,
    }
    valid, errors = validate_input(params)
    assert not valid
    assert any("Slide Count must be between 3 and 20" in e for e in errors)


@pytest.mark.parametrize("slide_count", [3, 8, 15, 20])
def test_valid_slide_counts(slide_count):
    params = {
        "topic": "Artificial Intelligence in Healthcare",
        "objective": "Explain deep learning diagnosis",
        "num_slides": slide_count,
        "duration": 15,
    }
    valid, errors = validate_input(params)
    assert valid
    assert len(errors) == 0


def test_duration_below_minimum():
    params = {
        "topic": "Artificial Intelligence in Healthcare",
        "objective": "Explain deep learning diagnosis",
        "num_slides": 8,
        "duration": 2,
    }
    valid, errors = validate_input(params)
    assert not valid
    assert any("Duration must be between 3 and 60 minutes" in e for e in errors)


def test_duration_above_maximum():
    params = {
        "topic": "Artificial Intelligence in Healthcare",
        "objective": "Explain deep learning diagnosis",
        "num_slides": 8,
        "duration": 75,
    }
    valid, errors = validate_input(params)
    assert not valid
    assert any("Duration must be between 3 and 60 minutes" in e for e in errors)


@pytest.mark.parametrize("duration", [3, 12, 30, 60])
def test_valid_durations(duration):
    params = {
        "topic": "Artificial Intelligence in Healthcare",
        "objective": "Explain deep learning diagnosis",
        "num_slides": 8,
        "duration": duration,
    }
    valid, errors = validate_input(params)
    assert valid
    assert len(errors) == 0


def test_invalid_difficulty():
    params = {
        "topic": "Artificial Intelligence in Healthcare",
        "objective": "Explain deep learning diagnosis",
        "num_slides": 8,
        "duration": 12,
        "difficulty": "MasterLevel",
    }
    valid, errors = validate_input(params)
    assert not valid
    assert any("Difficulty must be one of" in e for e in errors)
