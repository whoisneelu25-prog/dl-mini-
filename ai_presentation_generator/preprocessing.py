"""
Text Preprocessing and Topic Analysis Module for AI Presentation Generator.

This module implements:
1. TextPreprocessor: Whitespace normalization, punctuation handling,
   tokenization, stopword filtering, unigram/bigram extraction, keyphrase identification.
2. TopicAnalyzer: Rule-based domain taxonomy identification and presentation
   depth estimation as specified in the project report.
"""

import re
from collections import Counter
from typing import Dict, List, Set, Tuple


STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves", "presentation", "slide", "slides",
    "topic", "talk", "overview", "intro", "introduction"
}


class TextPreprocessor:
    """Preprocesses input topic and objective text for NLP pipelines."""

    def __init__(self, stopwords: Set[str] = None):
        self.stopwords = stopwords if stopwords is not None else STOPWORDS

    def clean_text(self, text: str) -> str:
        """
        Normalize whitespace, handle punctuation, strip non-printable characters.
        Preserves alphanumerics, hyphens, and basic punctuation.
        """
        if not text:
            return ""
        # Remove non-printable / control characters
        text = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", text)
        # Normalize multiple spaces, tabs, and newlines to a single space
        text = re.sub(r"\s+", " ", text)
        # Strip trailing and leading whitespace
        text = text.strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize cleaned text into lowercase word tokens.
        Preserves contractions and hyphenated compound terms.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []
        tokens = re.findall(r"\b[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*(?:'[a-z]+)?\b", cleaned.lower())
        return tokens

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stop words and very short tokens."""
        return [tok for tok in tokens if tok not in self.stopwords and len(tok) > 1]

    def extract_unigrams(self, tokens: List[str]) -> List[str]:
        """Extract valid unigrams from filtered tokens."""
        return [t for t in tokens if len(t) > 2]

    def extract_bigrams(self, tokens: List[str]) -> List[str]:
        """Extract meaningful two-word sequences (bigrams) from tokens."""
        bigrams = []
        for i in range(len(tokens) - 1):
            w1, w2 = tokens[i], tokens[i + 1]
            if w1 not in self.stopwords and w2 not in self.stopwords:
                bigrams.append(f"{w1} {w2}")
        return bigrams

    def extract_keyphrases(self, text: str, max_phrases: int = 5) -> List[str]:
        """
        Extract prominent keyphrases (unigrams and bigrams) ranked by frequency and length.
        """
        tokens = self.tokenize(text)
        filtered_tokens = self.remove_stopwords(tokens)

        if not filtered_tokens:
            return []

        # Count unigrams
        unigrams = self.extract_unigrams(filtered_tokens)
        unigram_counts = Counter(unigrams)

        # Count bigrams from raw tokens (checking boundaries)
        raw_bigrams = []
        for i in range(len(tokens) - 1):
            w1, w2 = tokens[i], tokens[i + 1]
            if w1 not in self.stopwords and w2 not in self.stopwords:
                raw_bigrams.append(f"{w1} {w2}")
        bigram_counts = Counter(raw_bigrams)

        # Score candidates: bigrams given a boost for specificity
        scored_candidates: Dict[str, float] = {}
        for bg, cnt in bigram_counts.items():
            scored_candidates[bg] = cnt * 2.5

        for ug, cnt in unigram_counts.items():
            # Only add unigram if not already fully dominated by a top bigram
            scored_candidates[ug] = cnt * 1.0

        sorted_phrases = sorted(
            scored_candidates.items(),
            key=lambda x: (x[1], len(x[0])),
            reverse=True
        )

        return [phrase for phrase, _ in sorted_phrases[:max_phrases]]

    def preprocess(self, text: str) -> Dict[str, any]:
        """Full pipeline returning structured linguistic features."""
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        filtered = self.remove_stopwords(tokens)
        bigrams = self.extract_bigrams(filtered)
        keyphrases = self.extract_keyphrases(cleaned, max_phrases=6)

        return {
            "cleaned_text": cleaned,
            "tokens": tokens,
            "filtered_tokens": filtered,
            "token_count": len(tokens),
            "unigrams": filtered,
            "bigrams": bigrams,
            "keyphrases": keyphrases,
        }


class TopicAnalyzer:
    """
    Topic Analysis using a rule-based taxonomy and heuristic depth estimation.
    As documented in the mini-project report, this is a rule-based keyword taxonomy,
    not a trained classification model.
    """

    DOMAIN_TAXONOMY: Dict[str, List[str]] = {
        "Healthcare": [
            "health", "healthcare", "medical", "medicine", "doctor", "patient",
            "hospital", "diagnosis", "disease", "clinical", "surgery", "drug",
            "biomedical", "pharma", "radiology", "pathology", "treatment",
            "therapy", "genomics", "nursing", "mri", "ct-scan", "oncology"
        ],
        "Deep Learning / Technology": [
            "ai", "artificial intelligence", "deep learning", "machine learning",
            "neural", "network", "transformer", "bert", "gpt", "t5", "nlp",
            "computer vision", "robotics", "cloud", "software", "algorithm",
            "data science", "cybersecurity", "iot", "blockchain", "computing",
            "database", "api", "automation", "python", "programming"
        ],
        "Finance": [
            "finance", "financial", "bank", "banking", "stock", "market",
            "investment", "trading", "crypto", "cryptocurrency", "bitcoin",
            "portfolio", "monetary", "economy", "economic", "fintech",
            "revenue", "valuation", "credit", "asset", "inflation", "wealth"
        ],
        "Environmental Science": [
            "environment", "environmental", "climate", "sustainability",
            "sustainable", "renewable", "solar", "wind", "ecology", "ecological",
            "carbon", "green", "biodiversity", "pollution", "conservation",
            "energy", "ecosystem", "global warming", "recycle", "waste"
        ],
        "Education": [
            "education", "educational", "learning", "teaching", "pedagogy",
            "student", "classroom", "school", "university", "curriculum",
            "academic", "lecture", "faculty", "tutoring", "elearning",
            "stem", "assessment", "exam", "college", "pedagogical"
        ],
    }

    def detect_domain(self, topic: str) -> str:
        """
        Classifies topic into one of the supported domains using keyword taxonomy matching.
        """
        if not topic:
            return "General / Interdisciplinary"

        normalized = topic.lower()
        domain_scores: Dict[str, int] = {domain: 0 for domain in self.DOMAIN_TAXONOMY}

        for domain, keywords in self.DOMAIN_TAXONOMY.items():
            for kw in keywords:
                # Exact phrase boundary match
                pattern = r"\b" + re.escape(kw) + r"\b"
                matches = len(re.findall(pattern, normalized))
                domain_scores[domain] += matches

        # Pick top score if > 0
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        top_domain, top_score = sorted_domains[0]

        if top_score > 0:
            return top_domain
        return "General / Interdisciplinary"

    def estimate_depth(self, difficulty: str, num_slides: int) -> Dict[str, any]:
        """
        Estimates presentation depth, pacing, and target slide density.
        """
        difficulty_clean = (difficulty or "Intermediate").capitalize()
        if difficulty_clean not in {"Beginner", "Intermediate", "Advanced"}:
            difficulty_clean = "Intermediate"

        specs = {
            "Beginner": {
                "technical_depth": "Foundational / Intuitive",
                "recommended_bullets": 3,
                "detail_level": "High-level concepts, analogies, and real-world impact.",
                "complexity_weight": 1.0,
            },
            "Intermediate": {
                "technical_depth": "Balanced Applied",
                "recommended_bullets": 4,
                "detail_level": "Architectural principles, workflows, and implementation aspects.",
                "complexity_weight": 1.5,
            },
            "Advanced": {
                "technical_depth": "Deep Technical & Mathematical",
                "recommended_bullets": 4,
                "detail_level": "Algorithmic mechanisms, trade-offs, formal evaluation, and research limitations.",
                "complexity_weight": 2.0,
            },
        }

        config = specs[difficulty_clean].copy()
        config["difficulty"] = difficulty_clean
        config["num_slides"] = num_slides
        config["pacing_profile"] = "Evenly distributed across outline modules."
        return config
