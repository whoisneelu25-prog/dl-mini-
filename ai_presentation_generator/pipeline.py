"""
Unified AI Presentation Pipeline Orchestrator.

Integrates the end-to-end Deep Learning + NLP pipeline:
Input -> Validation -> Preprocessing -> Topic Analysis ->
Sentence-BERT Embedding -> Content Planning -> FLAN-T5 Generation ->
Semantic Refinement -> Presentation Assembly -> Export Ready.
"""

import datetime
import logging
import uuid
from typing import Any, Callable, Dict, Optional

from generator import ContentPlanner, ContentRefiner, SlideGenerator
from model import EmbeddingEngine, TransformerEngine
from preprocessing import TextPreprocessor, TopicAnalyzer
from utils import get_system_info, validate_input

logger = logging.getLogger(__name__)


class PresentationPipeline:
    """End-to-End Orchestrator for the Deep Learning + NLP presentation pipeline."""

    _instance = None

    def __init__(
        self,
        embedding_engine: Optional[EmbeddingEngine] = None,
        transformer_engine: Optional[TransformerEngine] = None,
    ):
        logger.info("Initializing PresentationPipeline...")
        self.preprocessor = TextPreprocessor()
        self.topic_analyzer = TopicAnalyzer()
        self.planner = ContentPlanner()

        # Models are loaded or passed (cached)
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.transformer_engine = transformer_engine or TransformerEngine()

        self.slide_generator = SlideGenerator(
            transformer_engine=self.transformer_engine,
            topic_analyzer=self.topic_analyzer,
        )
        self.refiner = ContentRefiner(
            embedding_engine=self.embedding_engine,
            transformer_engine=self.transformer_engine,
            threshold=0.88,
        )
        logger.info("PresentationPipeline initialized successfully.")

    @classmethod
    def get_singleton(cls):
        """Singleton accessor to prevent redundant model reloading."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def run_pipeline(
        self,
        params: Dict[str, Any],
        step_callback: Optional[Callable[[str, str, float], None]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the genuine 9-stage deep learning & NLP pipeline:
        1. Input Validation
        2. Text Preprocessing
        3. Topic Analysis & Depth Estimation
        4. Sentence-BERT Semantic Embeddings
        5. Content Planning (Exact Slide Count & Timing)
        6. FLAN-T5 Transformer Generation
        7. Slide Structure Generation
        8. Semantic Content Refinement (0.88 threshold)
        9. Presentation Packaging
        """
        # Stage 1: Input Validation
        if step_callback:
            step_callback("validation", "Validating presentation parameters...", 0.1)
        valid, errors = validate_input(params)
        if not valid:
            raise ValueError(f"Validation failed: {'; '.join(errors)}")

        topic = str(params["topic"]).strip()
        objective = str(params.get("objective", "")).strip()
        audience = str(params.get("audience", "College Students")).strip()
        difficulty = str(params.get("difficulty", "Intermediate")).strip()
        presentation_type = str(params.get("presentation_type", "Technical Seminar")).strip()
        num_slides = int(params.get("num_slides", 8))
        duration = int(params.get("duration", 12))

        # Stage 2: Text Preprocessing
        if step_callback:
            step_callback("preprocessing", "Performing whitespace normalization, tokenization, and keyphrase extraction...", 0.2)
        preprocessed = self.preprocessor.preprocess(topic)

        # Stage 3: Topic Analysis
        if step_callback:
            step_callback("topic_analysis", "Detecting domain taxonomy and estimating technical depth...", 0.3)
        domain = self.topic_analyzer.detect_domain(topic)
        depth_info = self.topic_analyzer.estimate_depth(difficulty, num_slides)

        # Stage 4: Sentence-BERT Semantic Embedding
        if step_callback:
            step_callback("embedding", "Computing 384-dimensional dense semantic embeddings using all-MiniLM-L6-v2...", 0.4)
        topic_embedding = self.embedding_engine.encode(topic)

        # Stage 5: Content Planning
        if step_callback:
            step_callback("planning", f"Planning logical academic progression for exactly {num_slides} slides ({duration} mins)...", 0.5)
        planned_slides = self.planner.plan_structure(
            topic=topic,
            num_slides=num_slides,
            duration_mins=duration,
            audience=audience,
            difficulty=difficulty,
            objective=objective,
            presentation_type=presentation_type,
        )

        # Stage 6 & 7: FLAN-T5 Transformer Generation & Slide Structure Generation
        if step_callback:
            step_callback("generation", f"Executing sequence-to-sequence beam search inference with google/flan-t5-base...", 0.6)

        def slide_gen_progress(curr, total, msg):
            if step_callback:
                frac = 0.6 + 0.25 * (curr / total)
                step_callback("generation", msg, frac)

        raw_slides = self.slide_generator.generate_presentation(
            topic=topic,
            objective=objective,
            audience=audience,
            difficulty=difficulty,
            presentation_type=presentation_type,
            planned_slides=planned_slides,
            progress_callback=slide_gen_progress,
        )

        # Stage 8: Semantic Content Refinement
        if step_callback:
            step_callback("refinement", "Analyzing semantic similarity matrix; detecting and refining redundancy >= 0.88...", 0.88)

        refinement_result = self.refiner.refine_presentation(
            slides=raw_slides,
            topic=topic,
        )
        final_slides = refinement_result["slides"]

        # Stage 9: Presentation Output Packaging
        if step_callback:
            step_callback("complete", "Packaging final presentation outline and export schemas...", 1.0)

        pres_id = f"pres_{uuid.uuid4().hex[:10]}"
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result = {
            "id": pres_id,
            "topic": topic,
            "objective": objective,
            "audience": audience,
            "difficulty": difficulty,
            "presentation_type": presentation_type,
            "num_slides": len(final_slides),
            "duration": duration,
            "domain": domain,
            "depth_info": depth_info,
            "preprocessed_features": {
                "token_count": preprocessed["token_count"],
                "keyphrases": preprocessed["keyphrases"],
                "cleaned_text": preprocessed["cleaned_text"],
            },
            "slides": final_slides,
            "redundant_points_detected": refinement_result["redundant_points_detected"],
            "points_refined": refinement_result["points_refined"],
            "similarity_threshold": refinement_result["threshold"],
            "refinement_completed": True,
            "refinement_log": refinement_result["refinement_log"],
            "created_at": now_str,
            "system_info": get_system_info(),
        }

        return result
