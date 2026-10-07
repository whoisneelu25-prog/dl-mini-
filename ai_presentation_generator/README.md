# AI Presentation Generator
### AI-Powered Presentation Outline Generation Using Deep Learning and Natural Language Processing

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2%2B-orange.svg)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/Transformers-FLAN--T5--base-green.svg)](https://huggingface.co/google/flan-t5-base)
[![Sentence-Transformers](https://img.shields.io/badge/Sentence--Transformers-all--MiniLM--L6--v2-yellow.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Tests Passing](https://img.shields.io/badge/pytest-58%20passed-brightgreen.svg)]()

A genuine, production-grade Deep Learning and NLP platform developed for **Enterprise Deep Learning B.Tech Artificial Intelligence & Data Science NLP**. The system generates structured, audience-aware academic and technical presentation outlines using pretrained sequence-to-sequence transformers, 384-dimensional dense semantic embeddings, and semantic redundancy refinement.

---

## 📑 Table of Contents
1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Objectives](#objectives)
4. [System Architecture & Pipeline](#system-architecture--pipeline)
5. [Key Deep Learning & NLP Models](#key-deep-learning--nlp-models)
6. [Feature Set](#feature-set)
7. [Project Structure](#project-structure)
8. [Installation & Setup](#installation--setup)
9. [Running the Application](#running-the-application)
   - [Option A: Modern Web SaaS Application (FastAPI + Stitch UI)](#option-a-modern-web-saas-application)
   - [Option B: Streamlit Application](#option-b-streamlit-application)
10. [Running the Test Suite](#running-the-test-suite)
11. [Canonical Demonstration (Featured Demonstration)](#canonical-demonstration-evaluation-demo)
12. [Multi-Format Export System](#multi-format-export-system)
13. [Limitations & Future Enhancements](#limitations--future-enhancements)
14. [Technical Deep Dive FAQ](#evaluation-voce-technical-guide)

---

## 1. Project Overview

Presentation design in academia and industry requires synthesizing multifaceted technical concepts into coherent narrative structures. Conventional presentation tools offer static visual templates without domain-aware content planning, while generic large language models frequently generate verbose, redundant paragraphs unsuitable for slides.

The **AI Presentation Generator** implements an end-to-end NLP and sequence-to-sequence deep learning pipeline that transforms high-level presentation parameters (topic, objective, target audience, slide count, duration, difficulty, presentation type) into presentation-ready decks with strict slide count guarantees, balanced time pacing, structured bullets, applied case studies, and speaker notes.

---

## 2. Problem Statement

Manual preparation of technical slide decks suffers from:
1. **Structural Inconsistency:** Disorganized transitions between problem formulation, methodology, and empirical results.
2. **Time Budgeting Failures:** Unbalanced slide depth leading to overruns during conference or seminar presentations.
3. **Semantic Redundancy:** Repetitive bullet points reiterating identical semantic arguments across adjacent slides.
4. **Cognitive Overhead:** High friction in translating complex research into concise bulleted takeaways.

---

## 3. Objectives

- **Exact Slide Count Planning:** Dynamically plan exactly $N$ slides ($3 \le N \le 20$) with a coherent academic narrative arc (Introduction $\to$ Background $\to$ Architecture $\to$ Methodology $\to$ Applications $\to$ Conclusion).
- **Automated Pacing Allocation:** Distribute presentation time ($3 \le T \le 60$ minutes) proportionally across slides.
- **Deep Learning Text Generation:** Employ `google/flan-t5-base` with beam search inference (`num_beams=3`, `no_repeat_ngram_size=2`) to generate 3–5 concise bullets, applied case studies, and speaker notes.
- **Semantic Redundancy Refinement:** Utilize `sentence-transformers/all-MiniLM-L6-v2` dense 384-dimensional embeddings with a cosine similarity threshold of $0.88$ to detect and refine repetitive bullets.
- **Multi-Format Export:** Produce genuine 16:9 widescreen PowerPoint (`.pptx`) decks with embedded notes, GitHub-flavored Markdown (`.md`), and machine-readable JSON (`.json`).

---

## 4. System Architecture & Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                           │
│ (Topic, Objective, Audience, Slides: 3-20, Duration: 3-60m) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     INPUT VALIDATION                        │
│   (Type checking, length verification, parameter bounds)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    TEXT PREPROCESSING                       │
│  (Whitespace normalization, tokenization, stopword filter,  │
│             unigram & bigram candidate scoring)             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             TOPIC ANALYSIS & DEPTH ESTIMATION               │
│ (Domain taxonomy: Healthcare, Tech, Finance, Env, Education)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              SENTENCE-BERT SEMANTIC EMBEDDING               │
│  (all-MiniLM-L6-v2 generates 384-dimensional dense vectors) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      CONTENT PLANNER                        │
│   (Exact slide count enforcement, minutes-per-slide budget, │
│                 academic progression mapping)               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              FLAN-T5 TRANSFORMER GENERATION                 │
│(google/flan-t5-base seq2seq inference, beams=3, no_repeat=2)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 SLIDE STRUCTURE SYNTHESIS                   │
│   (Title, 3-5 concise bullets, case studies, speaker notes) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                SEMANTIC CONTENT REFINEMENT                  │
│ (SBERT pairwise cosine similarity >= 0.88 redundancy filter;│
│           FLAN-T5 alternative generation tracking)          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     MULTI-FORMAT EXPORT                     │
│      (python-pptx 16:9 widescreen, Markdown .md, JSON)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Key Deep Learning & NLP Models

| Component | Model / Specification | Purpose | Parameters / Hyperparameters |
| :--- | :--- | :--- | :--- |
| **Seq2Seq Generator** | `google/flan-t5-base` | Text generation for bullets, case studies, speaker notes | Pretrained (248M params), `num_beams=3`, `no_repeat_ngram_size=2`, `early_stopping=True` |
| **Semantic Embedding** | `sentence-transformers/all-MiniLM-L6-v2` | Dense vector representations of bullets and topics | Pretrained Siamese BERT (22M params), 384 dimensions, cosine distance metric |
| **Refinement Filter** | Cosine Similarity $\ge 0.88$ | Automated redundancy detection | Threshold: 0.88, intra-slide & inter-slide analysis |
| **Hardware Device** | Apple Silicon MPS / CUDA / CPU | Tensor compute acceleration | Auto-detected at runtime via `torch.backends.mps` / `torch.cuda` |

> **Note on Training:** As explicitly noted in the project report, `google/flan-t5-base` and `all-MiniLM-L6-v2` are **pretrained models** used for inference and zero/few-shot prompt execution, not trained from scratch.

---

## 6. Feature Set

- **Exact Slide Count Guarantee:** Request 3, 8, 15, or 20 slides, and the system delivers that exact count.
- **Pacing Budgeting:** Computes balanced pacing ($t = \text{duration} / \text{slides}$) ensuring total presentation time matches requested duration.
- **Concise Presentation Bullets:** Generates 3–5 high-signal bullet points per slide (15–25 words each) rather than dense paragraphs.
- **Domain-Specific Case Studies:** Generates real-world clinical, algorithmic, or enterprise case studies for every slide.
- **Contextual Speaker Notes:** Produces presenter guidance with pacing notes and talking points for each slide.
- **Redundancy Reduction Metric:** Tracks the exact number of redundant points detected and refined.
- **Interactive Presentation View:** Inspect slides sequentially with previous/next controls, inline content editing, and per-slide regeneration.
- **Multi-Format Export:** Downloads genuine 16:9 `.pptx` decks, clean GitHub Markdown, and structured JSON.
- **Persistent Presentation History:** Saves outlines in local storage with search, category filtering, and re-export capabilities.

---

## 7. Project Structure

```
ai_presentation_generator/
├── app.py                     # Streamlit application workflow & caching
├── server.py                  # FastAPI REST backend server
├── pipeline.py                # Unified end-to-end generation orchestrator
├── preprocessing.py           # TextPreprocessor & TopicAnalyzer taxonomy
├── model.py                   # EmbeddingEngine (SBERT) & TransformerEngine (FLAN-T5)
├── generator.py               # ContentPlanner, SlideGenerator, ContentRefiner
├── utils.py                   # Validation, PPTX, Markdown, JSON exporters
├── requirements.txt           # Project dependencies
├── README.md                  # Comprehensive documentation
├── .env.example               # Environment variables template
│
├── frontend/                  # Google Stitch-inspired Modern Web Application
│   ├── index.html             # 8-Screen SaaS Single Page Application
│   ├── style.css              # Stitch Design System (Modern AI SaaS)
│   └── app.js                 # Frontend SPA controller & API connector
│
├── tests/                     # Real pytest test suite (58 tests)
│   ├── test_validation.py     # Parameter validation bounds tests
│   ├── test_preprocessing.py  # Text cleaning & taxonomy classification tests
│   ├── test_embeddings.py     # 384D SBERT & cosine similarity tests
│   ├── test_planner.py        # Exact count & duration allocation tests
│   ├── test_generation.py     # FLAN-T5 inference & refinement tests
│   └── test_exports.py        # PPTX, Markdown & JSON export tests
│
└── outputs/                   # Generated presentations storage
```

---

## 8. Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12 (Python 3.11 recommended)
- macOS (Apple Silicon MPS), Linux (CUDA or CPU), or Windows

### Step 1: Clone or Navigate to Directory
```bash
cd "ai_presentation_generator"
```

### Step 2: Create and Activate Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 9. Running the Application

### Option A: Modern Web SaaS Application (FastAPI + Stitch UI)
This runs the full modern AI SaaS product matching Google Stitch design specifications (Screens 1 to 8):
```bash
python server.py
```
Open your browser to: **`http://localhost:8000`**

### Option B: Streamlit Application
For academic demonstration using the original Streamlit workflow:
```bash
streamlit run app.py
```
Open your browser to: **`http://localhost:8501`**

---

## 10. Running the Test Suite

Execute the comprehensive 58-test suite:
```bash
pytest tests/ -v
```
All 58 tests verify:
- Input validation (empty, short, out-of-range slides/duration)
- Text preprocessing (whitespace, tokenization, stopword filtering, bigrams)
- Topic domain classification (Healthcare, Tech, Finance, Environment, Education)
- Sentence-BERT 384D embedding dimensions and cosine similarities
- Exact slide count guarantee (3, 4, 8, 12, 15, 20 slides)
- Duration allocation summing to requested presentation duration
- FLAN-T5 seq2seq inference and bullet structuring
- Semantic redundancy detection at cosine $\ge 0.88$
- Valid 16:9 PPTX, Markdown, and JSON generation

---

## 11. Canonical Demonstration (Featured Demonstration)

Use the following parameters to demonstrate the system:

- **Presentation Topic:** `Artificial Intelligence in Healthcare`
- **Presentation Objective:** `Explain how AI is transforming healthcare diagnosis and patient care`
- **Target Audience:** `College Students`
- **Number of Slides:** `8`
- **Presentation Duration:** `12 minutes`
- **Difficulty Level:** `Intermediate`
- **Presentation Type:** `Technical Seminar`

### Expected 8-Slide Outline:
1. **Introduction to Artificial Intelligence in Healthcare** (1.5 min)
2. **Evolution and Background of Healthcare AI** (1.5 min)
3. **Core AI Technologies Used in Clinical Medicine** (1.5 min)
4. **AI-Based Medical Diagnosis and Pathology** (1.5 min)
5. **Real-World Healthcare Applications** (1.5 min)
6. **System Benefits and Critical Implementation Challenges** (1.5 min)
7. **Future Horizons and Emerging AI Paradigms** (1.5 min)
8. **Conclusion and Strategic Summary** (1.5 min)

---

## 12. Multi-Format Export System

1. **PowerPoint (`.pptx`):**
   - 16:9 widescreen format (13.333" $\times$ 7.5").
   - Title slide with metadata pill badges.
   - Content slides with slide number badge, allocated time badge (`⏱ 1.5 min`), structured bullet points, styled **Case Study callout container**, and embedded speaker notes.
2. **Markdown (`.md`):**
   - GitHub-flavored Markdown with complete frontmatter metadata, timing indicators, blockquoted case studies, and speaker notes.
3. **JSON (`.json`):**
   - Machine-readable presentation object hierarchy with full slide attributes.

---

## 13. Limitations & Future Enhancements

### Current Limitations:
- **Pretrained Inference:** Models generate plausible text based on pretrained weights; factual verification by domain experts is required prior to delivery.
- **Rule-Based Topic Classifier:** Topic taxonomy uses keyword boundary matching across five major domains rather than a fine-tuned classifier.
- **Single Presentation Language:** Generation is optimized for English prompts.

### Future Enhancements:
- Multi-modal image generation and auto-insertion of relevant diagrams onto slides.
- Retrieval-Augmented Generation (RAG) using PubMed and arXiv papers for verified academic citations.
- Direct export to Google Slides and PDF formats.

---

## 14. Technical Deep Dive FAQ

### Q1: What models are used in this project?
**Answer:** We utilize two complementary deep learning models:
1. `google/flan-t5-base` (248M parameters): A pretrained sequence-to-sequence transformer fine-tuned on instruction datasets, configured with beam search (`num_beams=3`, `no_repeat_ngram_size=2`) for structured text generation.
2. `sentence-transformers/all-MiniLM-L6-v2` (22M parameters): A pretrained Siamese dual-encoder neural network that projects text into a 384-dimensional dense semantic vector space.

### Q2: How does the semantic redundancy refinement work?
**Answer:** The system computes 384-dimensional dense embeddings for all generated bullet points using Sentence-BERT. It evaluates pairwise cosine similarity between points on each slide as well as across adjacent slides. When two points exhibit a cosine similarity $\ge 0.88$, the system flags semantic redundancy and prompts FLAN-T5 to generate a distinct technical perspective.

### Q3: How is the exact slide count guaranteed?
**Answer:** The `ContentPlanner` class maps the requested slide count (between 3 and 20) to a canonical academic progression. Slide 1 is fixed as Introduction/Overview, the final slide is fixed as Conclusion/Summary, and intermediate slides are dynamically selected from an academic curriculum pool.

### Q4: Why is beam search used instead of greedy decoding?
**Answer:** Greedy decoding picks only the single most probable token at each step ($argmax$), often leading to repetitive or sub-optimal sequences. Beam search ($num\_beams=3$) maintains the top 3 candidate hypotheses at each step, yielding significantly higher quality, coherent, and diverse presentation text.

---

## 📄 License & Academic Attribution
Developed as an academic mini-project for **Enterprise Deep Learning B.Tech Artificial Intelligence & Data Science NLP**. Free to use for research and educational demonstrations.
