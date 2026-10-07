"""
Deep Learning and NLP Models Module for AI Presentation Generator.

Implements:
1. EmbeddingEngine: sentence-transformers/all-MiniLM-L6-v2 (384-dimensional embeddings, cosine similarity)
2. TransformerEngine: google/flan-t5-base (Sequence-to-sequence inference with beam search)
"""

import hashlib
import logging
import os
import re
from typing import List, Optional, Union

import numpy as np
import torch

logger = logging.getLogger(__name__)


def get_optimal_device() -> str:
    """Detect available execution hardware: MPS (Apple Silicon), CUDA (NVIDIA), or CPU."""
    override = os.environ.get("DEVICE", "").lower()
    if override in {"cpu", "cuda", "mps"}:
        return override

    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


class EmbeddingEngine:
    """
    Sentence-BERT semantic embedding engine using all-MiniLM-L6-v2.
    Produces 384-dimensional dense vectors for semantic similarity and redundancy analysis.
    """

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    DIMENSION = 384

    def __init__(self, model_name: str = MODEL_NAME, device: Optional[str] = None):
        self.model_name = model_name
        self.device = device or get_optimal_device()
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SentenceTransformer model %s on %s...", self.model_name, self.device)
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info("SentenceTransformer loaded successfully.")
        except Exception as e:
            logger.warning("Failed to load SentenceTransformer (%s). Activating deterministic 384D fallback: %s", self.model_name, e)
            self.model = None

    def _fallback_embedding(self, text: str) -> np.ndarray:
        """Deterministic 384-dimensional fallback representation based on MD5 + character n-grams."""
        vec = np.zeros(self.DIMENSION, dtype=np.float32)
        words = re.findall(r"\w+", text.lower())
        for i, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.DIMENSION
            weight = 1.0 / (1.0 + 0.1 * i)
            vec[idx] += weight
            # Spread across dimension neighbors
            vec[(idx + 7) % self.DIMENSION] += 0.5 * weight
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            vec[0] = 1.0
        return vec

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Encodes a string or list of strings into 384-dimensional dense embeddings.
        Returns numpy array of shape (N, 384) or (384,).
        """
        is_single = isinstance(texts, str)
        text_list = [texts] if is_single else list(texts)

        if not text_list:
            empty = np.zeros((0, self.DIMENSION), dtype=np.float32)
            return empty[0] if is_single else empty

        if self.model is not None:
            try:
                embeddings = self.model.encode(
                    text_list,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )
                if is_single and len(embeddings.shape) == 2 and embeddings.shape[0] == 1:
                    return embeddings[0]
                return embeddings
            except Exception as e:
                logger.warning("Error during SBERT encoding: %s. Using fallback.", e)

        # Fallback path
        fallback_vecs = [self._fallback_embedding(t) for t in text_list]
        arr = np.array(fallback_vecs, dtype=np.float32)
        return arr[0] if is_single else arr

    @staticmethod
    def similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        """Computes cosine similarity between two 1D vectors."""
        v1 = np.asarray(v1, dtype=np.float32).flatten()
        v2 = np.asarray(v2, dtype=np.float32).flatten()
        dot = float(np.dot(v1, v2))
        norm1 = float(np.linalg.norm(v1))
        norm2 = float(np.linalg.norm(v2))
        if norm1 <= 1e-9 or norm2 <= 1e-9:
            return 0.0
        sim = dot / (norm1 * norm2)
        return float(np.clip(sim, -1.0, 1.0))

    @staticmethod
    def batch_similarity(v_query: np.ndarray, v_targets: np.ndarray) -> np.ndarray:
        """Computes cosine similarity of one query vector against multiple target vectors."""
        v_query = np.asarray(v_query, dtype=np.float32).reshape(1, -1)
        v_targets = np.asarray(v_targets, dtype=np.float32)
        if len(v_targets.shape) == 1:
            v_targets = v_targets.reshape(1, -1)

        norm_q = np.linalg.norm(v_query, axis=1, keepdims=True) + 1e-9
        norm_t = np.linalg.norm(v_targets, axis=1, keepdims=True) + 1e-9
        normalized_q = v_query / norm_q
        normalized_t = v_targets / norm_t
        sims = np.dot(normalized_q, normalized_t.T)[0]
        return np.clip(sims, -1.0, 1.0)


class TransformerEngine:
    """
    Inference engine for google/flan-t5-base.
    Sequence-to-sequence generation configured with beam search, no-repeat n-grams, and early stopping.
    """

    MODEL_NAME = "google/flan-t5-base"

    def __init__(self, model_name: str = MODEL_NAME, device: Optional[str] = None):
        self.model_name = model_name
        self.device = device or get_optimal_device()
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            logger.info("Loading FLAN-T5 model %s on %s...", self.model_name, self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("FLAN-T5 loaded successfully on %s.", self.device)
        except Exception as e:
            logger.warning("Failed to load FLAN-T5 model %s (%s). Operating in fallback mode.", self.model_name, e)
            self.tokenizer = None
            self.model = None

    def generate_text(
        self,
        prompt: str,
        max_length: int = 128,
        num_beams: int = 3,
        no_repeat_ngram_size: int = 2,
        early_stopping: bool = True,
        min_length: int = 10,
    ) -> str:
        """Execute sequence-to-sequence beam search generation."""
        if self.model is not None and self.tokenizer is not None:
            try:
                inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_length=max_length,
                        min_length=min_length,
                        num_beams=num_beams,
                        no_repeat_ngram_size=no_repeat_ngram_size,
                        early_stopping=early_stopping,
                    )
                generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
                return generated
            except Exception as e:
                logger.warning("Generation error with FLAN-T5: %s", e)

        return self._heuristic_fallback_generation(prompt)

    def _heuristic_fallback_generation(self, prompt: str) -> str:
        """Deterministic NLP generation fallback when network or weights are unavailable."""
        topic_match = re.search(r"Topic:\s*([^\n]+)", prompt)
        title_match = re.search(r"Slide Title:\s*([^\n]+)", prompt)
        topic = topic_match.group(1).strip() if topic_match else "Core Subject"
        title = title_match.group(1).strip() if title_match else "Overview"

        if "case study" in prompt.lower():
            return f"Implementation of {topic} in enterprise systems demonstrating measurable efficiency gains and reduced latency."
        if "speaker note" in prompt.lower():
            return f"Walk the audience through {title}, detailing the practical significance and connection to {topic}."
        if "alternative bullet" in prompt.lower():
            return f"Examine foundational benchmarks and empirical evaluations supporting {topic} deployment."
        return f"Key principles and modern paradigms underlying {title} within {topic}."

    def generate_bullets(
        self,
        topic: str,
        objective: str,
        audience: str,
        difficulty: str,
        presentation_type: str,
        slide_title: str,
        slide_purpose: str,
        count: int = 4,
    ) -> List[str]:
        """
        Generates 3-5 concise, informative bullet points for a slide using FLAN-T5.
        Uses structured prompts with topic, objective, audience, difficulty, and slide purpose.
        """
        bullets: List[str] = []

        sub_aspects = [
            "Core Definition & Scope",
            "Key Mechanism & Operational Workflow",
            "Practical Benefit & System Impact",
            "Industry Best Practice & Future Direction",
            "Real-World Consideration & Trade-offs",
        ]

        for i in range(min(count, len(sub_aspects))):
            aspect = sub_aspects[i]
            prompt = (
                f"Topic: {topic}\n"
                f"Objective: {objective}\n"
                f"Audience: {audience}\n"
                f"Difficulty: {difficulty}\n"
                f"Presentation Type: {presentation_type}\n"
                f"Slide Title: {slide_title}\n"
                f"Slide Purpose: {slide_purpose}\n"
                f"Focus: {aspect}\n"
                f"Task: Write one concise, informative technical presentation bullet point (15-25 words) explaining {aspect} for {slide_title}."
            )

            raw = self.generate_text(prompt, max_length=64, num_beams=3, no_repeat_ngram_size=2, min_length=8)
            cleaned_bullet = self._clean_bullet_point(raw, slide_title, topic, aspect)
            if cleaned_bullet and cleaned_bullet not in bullets:
                bullets.append(cleaned_bullet)

        # Ensure we meet minimum 3 bullets
        fallback_templates = [
            f"Fundamental architectural principles and concepts driving {slide_title.lower()}.",
            f"Key operational workflows and data pipelines utilized in modern {topic.lower()} implementations.",
            f"Critical evaluation metrics, system advantages, and practical considerations for {audience.lower()}.",
            f"Emerging developments, future trajectory, and open challenges in {slide_title.lower()}."
        ]
        idx = 0
        while len(bullets) < 3 and idx < len(fallback_templates):
            candidate = fallback_templates[idx]
            if candidate not in bullets:
                bullets.append(candidate)
            idx += 1

        return bullets[:count]

    def _clean_bullet_point(self, raw: str, title: str, topic: str, aspect: str) -> str:
        """Cleans and polishes generated bullet text into presentation-ready format."""
        if not raw:
            return f"Key insights into {title} and practical implications for {topic}."

        # Remove leading markers like '•', '-', '1.', 'Bullet point:'
        cleaned = re.sub(r"^[\s•\-\*\d\.\)\:]+", "", raw).strip()
        cleaned = re.sub(r"^(Bullet Point|Point|Focus|Slide):\s*", "", cleaned, flags=re.IGNORECASE).strip()

        # If too short, expand into meaningful statement
        if len(cleaned.split()) < 4:
            cleaned = f"{cleaned.capitalize()}: Primary mechanism enabling {aspect.lower()} in {topic}."

        # Capitalize first letter and ensure ending period
        cleaned = cleaned[0].upper() + cleaned[1:] if len(cleaned) > 1 else cleaned.upper()
        if not cleaned.endswith((".", "!", "?")):
            cleaned += "."

        return cleaned

    def generate_case_study(self, topic: str, slide_title: str, domain: str) -> str:
        """Generates a practical, domain-specific case study highlight for the slide."""
        prompt = (
            f"Topic: {topic}\n"
            f"Domain: {domain}\n"
            f"Slide Title: {slide_title}\n"
            f"Task: Describe a real-world case study or practical application (1-2 sentences) demonstrating {slide_title} in {domain}."
        )
        raw = self.generate_text(prompt, max_length=90, num_beams=3, no_repeat_ngram_size=2, min_length=12)
        cleaned = re.sub(r"^[\s•\-\*\d\.\)\:]+", "", raw).strip()
        if len(cleaned.split()) < 5:
            cleaned = f"Real-world deployment of {topic} demonstrating significant operational accuracy and automated workflow integration in {domain}."
        if not cleaned.endswith("."):
            cleaned += "."
        return cleaned

    def generate_speaker_notes(
        self,
        topic: str,
        slide_title: str,
        bullets: List[str],
        audience: str,
        time_minutes: float,
    ) -> str:
        """Generates contextual speaker notes guiding the presenter on pacing and talking points."""
        bullet_summary = " ".join(bullets[:2]) if bullets else "core principles"
        prompt = (
            f"Topic: {topic}\n"
            f"Slide Title: {slide_title}\n"
            f"Audience: {audience}\n"
            f"Time Allocation: {time_minutes:.1f} minutes\n"
            f"Bullets Summary: {bullet_summary}\n"
            f"Task: Write concise speaker notes advising the presenter on what to emphasize for {audience}."
        )
        raw = self.generate_text(prompt, max_length=110, num_beams=3, no_repeat_ngram_size=2, min_length=15)
        cleaned = re.sub(r"^[\s•\-\*\d\.\)\:]+", "", raw).strip()
        if len(cleaned.split()) < 6:
            cleaned = (
                f"Allocate approximately {time_minutes:.1f} minutes to walk through {slide_title.lower()}. "
                f"Highlight the practical relevance for {audience.lower()} and invite brief clarifying questions."
            )
        if not cleaned.endswith("."):
            cleaned += "."
        return cleaned

    def generate_alternative_bullet(
        self,
        topic: str,
        slide_title: str,
        existing_bullets: List[str],
        redundant_bullet: str,
    ) -> str:
        """Generates a distinct alternative bullet point when semantic redundancy is detected."""
        prompt = (
            f"Topic: {topic}\n"
            f"Slide Title: {slide_title}\n"
            f"Previous point (redundant): {redundant_bullet}\n"
            f"Task: Write a fresh, distinct bullet point highlighting a complementary technical aspect or performance benchmark."
        )
        raw = self.generate_text(prompt, max_length=64, num_beams=3, no_repeat_ngram_size=2, min_length=8)
        cleaned = self._clean_bullet_point(raw, slide_title, topic, "Alternative Technical Dimension")
        return cleaned
