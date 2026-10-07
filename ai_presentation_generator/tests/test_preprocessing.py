import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from preprocessing import TextPreprocessor, TopicAnalyzer


@pytest.fixture
def preprocessor():
    return TextPreprocessor()


@pytest.fixture
def analyzer():
    return TopicAnalyzer()


def test_whitespace_normalization(preprocessor):
    raw = "   Artificial    Intelligence   \n\n in \t Healthcare   "
    cleaned = preprocessor.clean_text(raw)
    assert cleaned == "Artificial Intelligence in Healthcare"


def test_control_character_handling(preprocessor):
    raw = "Neural Networks\x00 in\x1f Radiology\x7f"
    cleaned = preprocessor.clean_text(raw)
    assert "\x00" not in cleaned
    assert "\x1f" not in cleaned
    assert "Neural Networks in Radiology" == cleaned


def test_tokenization(preprocessor):
    text = "Explain state-of-the-art transformer-based deep learning."
    tokens = preprocessor.tokenize(text)
    assert "transformer-based" in tokens or "deep" in tokens
    assert "learning" in tokens
    assert all(t.islower() for t in tokens)


def test_stopword_filtering(preprocessor):
    tokens = ["the", "artificial", "intelligence", "in", "and", "modern", "healthcare"]
    filtered = preprocessor.remove_stopwords(tokens)
    assert "the" not in filtered
    assert "in" not in filtered
    assert "and" not in filtered
    assert "artificial" in filtered
    assert "intelligence" in filtered
    assert "healthcare" in filtered


def test_bigram_extraction(preprocessor):
    tokens = ["deep", "learning", "clinical", "diagnosis"]
    bigrams = preprocessor.extract_bigrams(tokens)
    assert "deep learning" in bigrams
    assert "learning clinical" in bigrams
    assert "clinical diagnosis" in bigrams


def test_keyphrase_extraction(preprocessor):
    text = "Artificial intelligence and deep learning revolutionizing modern clinical healthcare and medical diagnosis."
    phrases = preprocessor.extract_keyphrases(text, max_phrases=4)
    assert len(phrases) > 0
    # Should capture significant domain phrases
    joined = " ".join(phrases)
    assert "deep learning" in joined or "healthcare" in joined or "diagnosis" in joined


@pytest.mark.parametrize(
    "topic,expected_domain",
    [
        ("Artificial Intelligence in Healthcare", "Healthcare"),
        ("Clinical Decision Support with Medical Imaging", "Healthcare"),
        ("Transformer Architectures in Deep Learning", "Deep Learning / Technology"),
        ("Cybersecurity and Cloud Computing Infrastructure", "Deep Learning / Technology"),
        ("Algorithmic Trading and Crypto Asset Valuation", "Finance"),
        ("Sustainable Renewable Energy and Climate Change", "Environmental Science"),
        ("Pedagogical Methods and Classroom Curriculum Assessment", "Education"),
        ("Quantum Astrobiology of Exoplanets", "General / Interdisciplinary"),
    ],
)
def test_topic_domain_classification(analyzer, topic, expected_domain):
    detected = analyzer.detect_domain(topic)
    assert detected == expected_domain


def test_estimate_depth(analyzer):
    beg = analyzer.estimate_depth("Beginner", 5)
    assert beg["recommended_bullets"] == 3
    assert beg["technical_depth"] == "Foundational / Intuitive"

    adv = analyzer.estimate_depth("Advanced", 10)
    assert adv["recommended_bullets"] == 4
    assert adv["complexity_weight"] == 2.0
