"""
Content Planning, Slide Generation, and Semantic Refinement Module.

Implements:
1. ContentPlanner: Exact slide count planning (3-20 slides) with logical academic progression.
2. SlideGenerator: Deep learning generation with google/flan-t5-base.
3. ContentRefiner: Sentence-BERT (0.88 cosine similarity) redundancy detection and replacement.
"""

import copy
import logging
from typing import Callable, Dict, List, Optional

import numpy as np

from model import EmbeddingEngine, TransformerEngine
from preprocessing import TextPreprocessor, TopicAnalyzer

logger = logging.getLogger(__name__)


class ContentPlanner:
    """Plans academic presentation structure guaranteeing exact slide count and time allocation."""

    CANONICAL_SECTIONS: List[Dict[str, str]] = [
        {"type": "intro", "name": "Introduction & Overview", "purpose": "Introduce topic, motivation, and fundamental significance."},
        {"type": "background", "name": "Evolution & Background", "purpose": "Examine historical context and key milestones leading to modern paradigms."},
        {"type": "problem", "name": "Problem Statement & Challenges", "purpose": "Define key technical bottlenecks, operational pain points, and objectives."},
        {"type": "concepts", "name": "Core Theoretical Concepts", "purpose": "Elucidate foundational principles, taxonomy, and definitions."},
        {"type": "architecture", "name": "System Architecture & Framework", "purpose": "Break down end-to-end architecture, modules, and pipeline components."},
        {"type": "methodology", "name": "Methodologies & Algorithms", "purpose": "Explain core algorithmic techniques, workflows, and processing pipelines."},
        {"type": "technical", "name": "Technical Details & Data Pipeline", "purpose": "Detail data representation, transformation, and computational mechanisms."},
        {"type": "applications", "name": "Real-World Applications", "purpose": "Showcase prominent applied use-cases and industry implementations."},
        {"type": "case_study", "name": "Case Study & Empirical Analysis", "purpose": "Analyze real-world experimental results, system deployments, or metrics."},
        {"type": "comparison", "name": "Comparative Analysis & Benchmarks", "purpose": "Benchmark performance against conventional approaches and baseline systems."},
        {"type": "benefits", "name": "Advantages & System Benefits", "purpose": "Summarize efficiency, accuracy, scalability, and practical value additions."},
        {"type": "limitations", "name": "Challenges & Practical Limitations", "purpose": "Critically analyze current constraints, ethical considerations, and bottlenecks."},
        {"type": "results", "name": "Key Findings & Practical Outcomes", "purpose": "Present quantitative findings, operational impacts, and verified conclusions."},
        {"type": "future", "name": "Future Horizons & Emerging Trends", "purpose": "Explore upcoming research directions, next-generation paradigms, and expansion."},
        {"type": "conclusion", "name": "Conclusion & Strategic Summary", "purpose": "Synthesize core insights, final takeaways, and concluding remarks."},
    ]

    def plan_structure(
        self,
        topic: str,
        num_slides: int,
        duration_mins: int,
        audience: str = "College Students",
        difficulty: str = "Intermediate",
        objective: str = "",
        presentation_type: str = "Technical Seminar",
    ) -> List[Dict[str, any]]:
        """
        Plans the slide outline ensuring EXACT requested slide count (3-20)
        and balanced duration allocation summing exactly to duration_mins.
        """
        # Validate count bounds
        slides_count = max(3, min(20, int(num_slides)))
        total_duration = max(3, min(60, int(duration_mins)))

        # Time per slide: base allocation
        base_time = round(total_duration / slides_count, 1)

        # Select modules according to slide count
        selected_modules = self._select_modules(slides_count, presentation_type)

        planned_slides: List[Dict[str, any]] = []
        for i, mod in enumerate(selected_modules):
            slide_no = i + 1

            # Format title incorporating the topic naturally
            if slide_no == 1:
                title = f"Introduction to {topic}"
            elif slide_no == slides_count:
                title = f"Conclusion & Future Outlook of {topic}"
            else:
                title = f"{mod['name']} in {topic}" if "in" not in mod["name"] else f"{mod['name']}"

            planned_slides.append({
                "slide_number": slide_no,
                "title": title,
                "section_type": mod["type"],
                "purpose": mod["purpose"],
                "time_minutes": base_time,
                "audience": audience,
                "difficulty": difficulty,
            })

        # Ensure exact duration sum by adjusting final slide slightly if needed
        current_sum = sum(s["time_minutes"] for s in planned_slides)
        diff = round(total_duration - current_sum, 1)
        if abs(diff) > 0:
            planned_slides[-1]["time_minutes"] = round(planned_slides[-1]["time_minutes"] + diff, 1)

        return planned_slides

    def _select_modules(self, count: int, presentation_type: str) -> List[Dict[str, str]]:
        """Selects exactly `count` modules maintaining academic narrative arc."""
        intro = self.CANONICAL_SECTIONS[0]
        conclusion = self.CANONICAL_SECTIONS[-1]

        if count == 3:
            middle = [self.CANONICAL_SECTIONS[7]]  # Applications
            return [intro] + middle + [conclusion]

        if count == 4:
            middle = [self.CANONICAL_SECTIONS[1], self.CANONICAL_SECTIONS[7]]
            return [intro] + middle + [conclusion]

        if count == 8:
            # Canonical 8-slide progression
            chosen_indices = [0, 1, 4, 5, 7, 10, 13, 14]
            return [self.CANONICAL_SECTIONS[idx] for idx in chosen_indices]

        # General case for 5 to 20 slides
        intermediate_pool = self.CANONICAL_SECTIONS[1:-1]
        needed_intermediates = count - 2

        if needed_intermediates <= len(intermediate_pool):
            step = len(intermediate_pool) / float(needed_intermediates)
            selected = [intermediate_pool[int(i * step)] for i in range(needed_intermediates)]
        else:
            # Expand beyond pool length by adding specialized academic subtopics
            selected = list(intermediate_pool)
            extra_needed = needed_intermediates - len(intermediate_pool)
            extensions = [
                {"type": "infra", "name": "Hardware & Deployment Infrastructure", "purpose": "Analyze compute requirements, latency optimization, and deployment engines."},
                {"type": "ethics", "name": "Ethical Considerations & Safety Governance", "purpose": "Address data privacy, regulatory compliance, bias mitigation, and safety standards."},
                {"type": "evaluation", "name": "Empirical Benchmarking & Validation", "purpose": "Demonstrate experimental methodology, confusion matrices, and test accuracy metrics."},
                {"type": "case_study_2", "name": "Enterprise Case Study & Production Lessons", "purpose": "Review enterprise case study highlighting operational learnings and pitfalls."},
                {"type": "scalability", "name": "System Scalability & Edge Deployment", "purpose": "Explore scale-out architecture, edge intelligence, and distributed synchronization."},
                {"type": "roadmap", "name": "Strategic Implementation Roadmap", "purpose": "Provide phased implementation guidelines, timeline estimates, and risk management."},
                {"type": "summary", "name": "Comprehensive Domain Synthesis", "purpose": "Synthesize multi-dimensional insights across technical, operational, and organizational axes."},
            ]
            for ext in extensions[:extra_needed]:
                selected.append(ext)

        return [intro] + selected[:needed_intermediates] + [conclusion]


class SlideGenerator:
    """Generates complete presentation slides using FLAN-T5 transformer inference."""

    def __init__(
        self,
        transformer_engine: TransformerEngine,
        topic_analyzer: Optional[TopicAnalyzer] = None,
    ):
        self.transformer = transformer_engine
        self.analyzer = topic_analyzer or TopicAnalyzer()

    def generate_presentation(
        self,
        topic: str,
        objective: str,
        audience: str,
        difficulty: str,
        presentation_type: str,
        planned_slides: List[Dict[str, any]],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[Dict[str, any]]:
        """
        Executes sequence-to-sequence generation for all slides.
        Notifies progress_callback for real stepper synchronization.
        """
        domain = self.analyzer.detect_domain(topic)
        total_slides = len(planned_slides)
        generated_slides: List[Dict[str, any]] = []

        for idx, slide_plan in enumerate(planned_slides):
            slide_no = slide_plan["slide_number"]
            title = slide_plan["title"]
            purpose = slide_plan["purpose"]
            time_allocated = slide_plan["time_minutes"]

            if progress_callback:
                progress_callback(slide_no, total_slides, f"FLAN-T5 is generating slide {slide_no} of {total_slides}: {title}")

            # 1. Generate 3-5 concise bullet points
            bullets = self.transformer.generate_bullets(
                topic=topic,
                objective=objective,
                audience=audience,
                difficulty=difficulty,
                presentation_type=presentation_type,
                slide_title=title,
                slide_purpose=purpose,
                count=4,
            )

            # 2. Generate contextual case study / practical highlight
            case_study = self.transformer.generate_case_study(
                topic=topic,
                slide_title=title,
                domain=domain,
            )

            # 3. Generate speaker notes
            speaker_notes = self.transformer.generate_speaker_notes(
                topic=topic,
                slide_title=title,
                bullets=bullets,
                audience=audience,
                time_minutes=time_allocated,
            )

            slide_record = {
                "slide_number": slide_no,
                "title": title,
                "purpose": purpose,
                "time_minutes": time_allocated,
                "bullets": bullets,
                "case_study": case_study,
                "speaker_notes": speaker_notes,
            }
            generated_slides.append(slide_record)

        return generated_slides


class ContentRefiner:
    """
    Semantic refinement engine utilizing Sentence-BERT embeddings.
    Detects semantic redundancy using a cosine similarity threshold of 0.88.
    Refines redundant points with FLAN-T5.
    """

    SIMILARITY_THRESHOLD: float = 0.88

    def __init__(
        self,
        embedding_engine: EmbeddingEngine,
        transformer_engine: TransformerEngine,
        threshold: float = SIMILARITY_THRESHOLD,
    ):
        self.embedding = embedding_engine
        self.transformer = transformer_engine
        self.threshold = threshold

    def refine_presentation(
        self,
        slides: List[Dict[str, any]],
        topic: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, any]:
        """
        Scans all bullet points within each slide and across adjacent slides.
        When cosine similarity >= 0.88 is detected, replaces with an alternative point.
        """
        refined_slides = copy.deepcopy(slides)
        redundant_points_detected = 0
        points_refined = 0
        refinement_log: List[Dict[str, any]] = []

        if progress_callback:
            progress_callback(f"Computing 384D Sentence-BERT embeddings for semantic refinement (threshold {self.threshold})...")

        previous_bullets: List[str] = []

        for slide_idx, slide in enumerate(refined_slides):
            bullets = slide["bullets"]
            if not bullets:
                continue

            # Encode bullets for current slide
            bullet_vecs = self.embedding.encode(bullets)
            n_bullets = len(bullets)

            # Check intra-slide redundancy
            for i in range(n_bullets):
                for j in range(i + 1, n_bullets):
                    sim = self.embedding.similarity(bullet_vecs[i], bullet_vecs[j])
                    if sim >= self.threshold:
                        redundant_points_detected += 1
                        old_point = bullets[j]
                        new_point = self.transformer.generate_alternative_bullet(
                            topic=topic,
                            slide_title=slide["title"],
                            existing_bullets=bullets,
                            redundant_bullet=old_point,
                        )
                        bullets[j] = new_point
                        points_refined += 1
                        refinement_log.append({
                            "slide_number": slide["slide_number"],
                            "type": "intra-slide",
                            "similarity": round(float(sim), 4),
                            "original": old_point,
                            "refined": new_point,
                        })

            # Check inter-slide redundancy against previous slide
            if previous_bullets:
                prev_vecs = self.embedding.encode(previous_bullets)
                curr_vecs = self.embedding.encode(bullets)

                for curr_idx, curr_vec in enumerate(curr_vecs):
                    sims = self.embedding.batch_similarity(curr_vec, prev_vecs)
                    max_sim_idx = int(np.argmax(sims))
                    max_sim = float(sims[max_sim_idx])

                    if max_sim >= self.threshold:
                        redundant_points_detected += 1
                        old_point = bullets[curr_idx]
                        new_point = self.transformer.generate_alternative_bullet(
                            topic=topic,
                            slide_title=slide["title"],
                            existing_bullets=bullets + previous_bullets,
                            redundant_bullet=old_point,
                        )
                        bullets[curr_idx] = new_point
                        points_refined += 1
                        refinement_log.append({
                            "slide_number": slide["slide_number"],
                            "type": "inter-slide",
                            "similarity": round(max_sim, 4),
                            "original": old_point,
                            "refined": new_point,
                        })

            previous_bullets = list(bullets)

        return {
            "slides": refined_slides,
            "redundant_points_detected": redundant_points_detected,
            "points_refined": points_refined,
            "threshold": self.threshold,
            "refinement_completed": True,
            "refinement_log": refinement_log,
        }
