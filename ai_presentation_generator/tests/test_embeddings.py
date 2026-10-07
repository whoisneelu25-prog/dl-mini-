import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model import EmbeddingEngine, get_optimal_device


@pytest.fixture(scope="module")
def embedding_engine():
    return EmbeddingEngine()


def test_embedding_dimension(embedding_engine):
    emb = embedding_engine.encode("Artificial Intelligence in Healthcare")
    assert isinstance(emb, np.ndarray)
    assert emb.shape == (384,)


def test_batch_embedding_dimensions(embedding_engine):
    texts = [
        "Medical diagnosis using convolutional neural networks",
        "Clinical trials and patient monitoring systems",
        "Transformer-based electronic health records analysis",
    ]
    embs = embedding_engine.encode(texts)
    assert isinstance(embs, np.ndarray)
    assert embs.shape == (3, 384)


def test_cosine_similarity_identical(embedding_engine):
    text = "AI assisted radiology and medical imaging"
    v1 = embedding_engine.encode(text)
    v2 = embedding_engine.encode(text)
    sim = embedding_engine.similarity(v1, v2)
    assert pytest.approx(sim, abs=1e-3) == 1.0


def test_cosine_similarity_related_vs_unrelated(embedding_engine):
    v_ai_health = embedding_engine.encode("Artificial intelligence in clinical patient diagnosis")
    v_med_diag = embedding_engine.encode("Machine learning automated healthcare diagnosis")
    v_finance = embedding_engine.encode("High frequency algorithmic cryptocurrency trading")

    sim_related = embedding_engine.similarity(v_ai_health, v_med_diag)
    sim_unrelated = embedding_engine.similarity(v_ai_health, v_finance)

    assert sim_related > sim_unrelated
    assert sim_unrelated < 0.65


def test_batch_similarity_calculation(embedding_engine):
    query = embedding_engine.encode("Deep learning neural networks")
    targets = embedding_engine.encode([
        "Convolutional and recurrent neural architectures",
        "Ancient Egyptian agricultural techniques",
    ])
    sims = embedding_engine.batch_similarity(query, targets)
    assert len(sims) == 2
    assert sims[0] > sims[1]


def test_optimal_device_detection():
    device = get_optimal_device()
    assert device in {"mps", "cuda", "cpu"}
