"""
PresentAI - Neural Presentation Engine
Enterprise Presentation Outline Generation Using Deep Learning and Natural Language Processing

Architecture:
User Input -> Input Validation -> Text Preprocessing -> Topic Analysis ->
Sentence-BERT Embedding -> Content Planning -> FLAN-T5 Generation ->
Slide Generation -> Semantic Content Refinement -> Export System (PPTX/MD/JSON)
"""

import io
import json
import os
import sys
import tempfile
import streamlit as st

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from model import EmbeddingEngine, TransformerEngine, get_optimal_device
from pipeline import PresentationPipeline
from utils import (
    VALID_AUDIENCES,
    VALID_DIFFICULTIES,
    VALID_PRESENTATION_TYPES,
    export_to_json,
    export_to_markdown,
    export_to_pptx,
    get_system_info,
    validate_input,
)

# Page configuration
st.set_page_config(
    page_title="PresentAI | Deep Learning Presentation Engine",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Enterprise SaaS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        color: #0f172a;
        letter-spacing: -0.02em;
    }
    
    .stApp {
        background-color: #f8fafc;
    }
    
    .hero-badge {
        display: inline-block;
        background: #eef2ff;
        color: #4f46e5;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 9999px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border: 1px solid rgba(79, 70, 229, 0.15);
        margin-bottom: 8px;
    }
    
    .stat-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        text-align: center;
    }
    
    .stat-card .label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    
    .stat-card .val {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    .stat-card .val.accent {
        color: #4f46e5;
    }
    
    .stat-card .val.success {
        color: #10b981;
    }
    
    .case-study-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #4f46e5;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 14px 0;
    }
    
    .notes-box {
        background: #fdfefe;
        border: 1px dashed #cbd5e1;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.88rem;
        color: #475569;
        margin-top: 14px;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# Model Caching via Streamlit Cache Resource
# ==============================================================================
@st.cache_resource(show_spinner="Loading Sentence-BERT embedding engine...")
def load_embedding_engine():
    return EmbeddingEngine()


@st.cache_resource(show_spinner="Loading google/flan-t5-base transformer model...")
def load_transformer_engine():
    return TransformerEngine()


@st.cache_resource(show_spinner="Initializing Neural Pipeline...")
def get_pipeline():
    emb = load_embedding_engine()
    tf = load_transformer_engine()
    return PresentationPipeline(embedding_engine=emb, transformer_engine=tf)


pipeline = get_pipeline()
sys_info = get_system_info()


# ==============================================================================
# Sidebar: System Specifications
# ==============================================================================
with st.sidebar:
    st.markdown('<div class="hero-badge">PresentAI Platform</div>', unsafe_allow_html=True)
    st.title("Neural Engine")
    st.caption("Pretrained Sequence-to-Sequence Generation & Semantic Vector Refinement")

    st.markdown("---")
    st.subheader("System Specifications")
    st.write(f"**Generation Model:** `google/flan-t5-base`")
    st.write(f"**Semantic Model:** `all-MiniLM-L6-v2`")
    st.write(f"**Vector Dimension:** `384 D`")
    st.write(f"**Beam Search:** `3 beams`")
    st.write(f"**Redundancy Threshold:** `0.88 Cosine`")
    st.write(f"**Supported Slides:** `3–20 slides`")
    st.write(f"**Supported Duration:** `3–60 minutes`")
    st.write(f"**Hardware Acceleration:** `{sys_info['execution_device']} GPU`")

    st.markdown("---")
    st.info("⚡ **Platform Note:** High-throughput inference accelerated natively on Apple Silicon MPS / GPU.")


# ==============================================================================
# Top Header Banner
# ==============================================================================
st.markdown('<div class="hero-badge">ENTERPRISE NEURAL PRESENTATION PLATFORM</div>', unsafe_allow_html=True)
st.title("PresentAI: Deep Learning Presentation Generator")
st.markdown("Turn any complex topic into a structured, audience-aligned presentation deck using **google/flan-t5-base**, **Sentence-BERT (384D)**, and **Semantic Content Refinement**.")
st.markdown("---")


# Tab Navigation
tabs = st.tabs([
    "🛠 Create Presentation",
    "🖥 Presentation Slide View",
    "🏛 Technology & Architecture",
    "⚡ Featured Presets & Demos",
])


# ==============================================================================
# TAB 1: CREATE PRESENTATION
# ==============================================================================
with tabs[0]:
    col_input, col_preview = st.columns([1.3, 1], gap="large")

    with col_input:
        st.subheader("Configure your presentation")
        st.caption("Configure parameters or choose a featured preset below.")

        c_p1, c_p2 = st.columns(2)
        with c_p1:
            if st.button("🩺 Preset 1: AI in Healthcare (8 Slides)", use_container_width=True):
                st.session_state["p_topic"] = "Artificial Intelligence in Healthcare"
                st.session_state["p_obj"] = "Explain how AI is transforming healthcare diagnosis and patient care"
                st.session_state["p_aud"] = "College Students"
                st.session_state["p_slides"] = 8
                st.session_state["p_dur"] = 12
        with c_p2:
            if st.button("🚗 Preset 2: Autonomous Driving (10 Slides)", use_container_width=True):
                st.session_state["p_topic"] = "Autonomous Driving and Computer Vision"
                st.session_state["p_obj"] = "Analyze deep neural perception, LiDAR sensor fusion, and real-time path planning in self-driving vehicles"
                st.session_state["p_aud"] = "Engineering Faculty"
                st.session_state["p_slides"] = 10
                st.session_state["p_dur"] = 15

        with st.form("presentation_form"):
            topic = st.text_input(
                "Presentation Topic *",
                value=st.session_state.get("p_topic", "Artificial Intelligence in Healthcare"),
                placeholder="e.g. Artificial Intelligence in Healthcare",
            )
            objective = st.text_area(
                "Presentation Objective *",
                value=st.session_state.get("p_obj", "Explain how AI is transforming healthcare diagnosis and patient care"),
                placeholder="What should your audience understand?",
                height=70,
            )

            col_aud, col_type = st.columns(2)
            with col_aud:
                aud_val = st.session_state.get("p_aud", "College Students")
                aud_idx = VALID_AUDIENCES.index(aud_val) if aud_val in VALID_AUDIENCES else 0
                audience = st.selectbox("Target Audience", VALID_AUDIENCES, index=aud_idx)
            with col_type:
                presentation_type = st.selectbox("Presentation Type", VALID_PRESENTATION_TYPES, index=0)

            difficulty = st.radio("Difficulty Level", VALID_DIFFICULTIES, index=1, horizontal=True)

            col_s, col_d = st.columns(2)
            with col_s:
                num_slides = st.slider("Number of Slides", min_value=3, max_value=20, value=st.session_state.get("p_slides", 8))
            with col_d:
                duration = st.slider("Duration (minutes)", min_value=3, max_value=60, value=st.session_state.get("p_dur", 12))

            submit_btn = st.form_submit_button("✨ Generate Presentation", use_container_width=True, type="primary")

    with col_preview:
        st.subheader("Presentation Preview")
        st.caption("Live configuration snapshot and deep learning status.")

        p_pace = round(duration / num_slides, 1)
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(15,23,42,0.05);">
            <div style="font-size: 0.75rem; font-weight: 700; color: #4f46e5; text-transform: uppercase; margin-bottom: 6px;">Live Target Outline</div>
            <h4 style="margin: 0 0 6px 0; color: #0f172a;">{topic or 'Presentation Topic'}</h4>
            <p style="font-size: 0.88rem; color: #475569; margin-bottom: 16px;">{objective or 'Presentation goals...'}</p>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center;">
                <div style="background: #f8fafc; padding: 8px; border-radius: 6px;"><div style="font-size: 0.65rem; color: #64748b;">SLIDES</div><strong>{num_slides}</strong></div>
                <div style="background: #f8fafc; padding: 8px; border-radius: 6px;"><div style="font-size: 0.65rem; color: #64748b;">DURATION</div><strong>{duration}m</strong></div>
                <div style="background: #f8fafc; padding: 8px; border-radius: 6px;"><div style="font-size: 0.65rem; color: #64748b;">PACE</div><strong>{p_pace}m</strong></div>
                <div style="background: #f8fafc; padding: 8px; border-radius: 6px;"><div style="font-size: 0.65rem; color: #64748b;">AUDIENCE</div><strong>{audience.split()[0]}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: #0f172a; color: #f8fafc; border-radius: 12px; padding: 20px;">
            <div style="font-size: 0.72rem; font-weight: 700; color: #818cf8; margin-bottom: 10px;">NEURAL PIPELINE RUNTIME</div>
            <div style="font-size: 0.82rem; margin-bottom: 6px;">Seq2Seq Model: <strong>google/flan-t5-base</strong></div>
            <div style="font-size: 0.82rem; margin-bottom: 6px;">Embedding Model: <strong>all-MiniLM-L6-v2 (384D)</strong></div>
            <div style="font-size: 0.82rem; margin-bottom: 6px;">Similarity Metric: <strong>Cosine &ge; 0.88</strong></div>
            <div style="font-size: 0.82rem;">Execution Hardware: <strong>{sys_info['execution_device']} Accelerated</strong></div>
        </div>
        """, unsafe_allow_html=True)

    # Handle Generation
    if submit_btn:
        params = {
            "topic": topic,
            "objective": objective,
            "audience": audience,
            "difficulty": difficulty,
            "presentation_type": presentation_type,
            "num_slides": num_slides,
            "duration": duration,
        }

        valid, errors = validate_input(params)
        if not valid:
            st.error("Validation failed:\n" + "\n".join(f"- {e}" for e in errors))
        else:
            st.markdown("---")
            progress_container = st.container()
            with progress_container:
                st.subheader("Synthesizing your presentation...")
                status_text = st.empty()
                progress_bar = st.progress(0.0)

                def st_progress_cb(stage, message, frac):
                    status_text.info(f"🔄 {message}")
                    progress_bar.progress(min(1.0, max(0.0, frac)))

                with st.spinner("Executing end-to-end Deep Learning & NLP generation pipeline..."):
                    try:
                        presentation = pipeline.run_pipeline(params, step_callback=st_progress_cb)
                        st.session_state["current_presentation"] = presentation
                        status_text.success("✓ Presentation generated and semantically refined successfully!")
                        progress_bar.progress(1.0)
                    except Exception as err:
                        st.error(f"Generation error: {err}")

    # Display Generated Presentation
    if "current_presentation" in st.session_state:
        pres = st.session_state["current_presentation"]
        st.markdown("---")
        st.header("Your presentation is ready")
        st.caption(f"Generated presentation outline for '{pres['topic']}'")

        # Top Statistics Ribbon
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="label">Detected Domain</div><div class="val">{pres.get("domain", "Tech")}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="label">Slides</div><div class="val">{pres["num_slides"]}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div class="label">Duration</div><div class="val">{pres["duration"]} min</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-card"><div class="label">Difficulty</div><div class="val">{pres["difficulty"]}</div></div>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'<div class="stat-card"><div class="label">Refinement</div><div class="val success">Completed</div></div>', unsafe_allow_html=True)
        with c6:
            st.markdown(f'<div class="stat-card"><div class="label">Redundant Fixed</div><div class="val accent">{pres.get("points_refined", 0)}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Export Buttons
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        with exp_col1:
            with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp_p:
                export_to_pptx(pres, tmp_p.name)
                with open(tmp_p.name, "rb") as f:
                    pptx_bytes = f.read()
            st.download_button(
                "📥 Download PowerPoint (.pptx)",
                data=pptx_bytes,
                file_name=f"Presentation_{pres['id']}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
            )

        with exp_col2:
            with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp_m:
                export_to_markdown(pres, tmp_m.name)
                with open(tmp_m.name, "r", encoding="utf-8") as f:
                    md_text = f.read()
            st.download_button(
                "📥 Download Markdown (.md)",
                data=md_text,
                file_name=f"Presentation_{pres['id']}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with exp_col3:
            json_str = json.dumps(pres, indent=2)
            st.download_button(
                "📥 Download JSON (.json)",
                data=json_str,
                file_name=f"Presentation_{pres['id']}.json",
                mime="application/json",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Slide Cards List
        for slide in pres["slides"]:
            s_num = slide["slide_number"]
            s_title = slide["title"]
            s_time = slide["time_minutes"]

            with st.expander(f"SLIDE {s_num:02d}: {s_title} (⏱ {s_time:.1f} min)", expanded=(s_num == 1)):
                st.markdown(f"**Purpose:** *{slide.get('purpose', '')}*")
                st.markdown("**Key Points:**")
                for bullet in slide.get("bullets", []):
                    st.markdown(f"- {bullet}")

                st.markdown(f"""
                <div class="case-study-box">
                    <strong style="color: #4f46e5; font-size: 0.76rem; text-transform: uppercase;">Case Study / Real-World Application</strong><br>
                    {slide.get('case_study', 'Real-world deployment.')}
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="notes-box">
                    <strong>Speaker Notes:</strong> {slide.get('speaker_notes', '')}
                </div>
                """, unsafe_allow_html=True)


# ==============================================================================
# TAB 2: SLIDE PRESENTATION DETAIL VIEW
# ==============================================================================
with tabs[1]:
    if "current_presentation" not in st.session_state:
        st.info("Please generate a presentation in the 'Create Presentation' tab first, or load one of the featured demos.")
    else:
        pres = st.session_state["current_presentation"]
        slides = pres["slides"]
        total_s = len(slides)

        slide_idx = st.slider("Select Slide", min_value=1, max_value=total_s, value=1) - 1
        curr_slide = slides[slide_idx]

        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 40px; box-shadow: 0 4px 16px rgba(15,23,42,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 0.8rem; font-weight: 700; color: #4f46e5;">SLIDE {curr_slide['slide_number']:02d} / {total_s:02d}</span>
                <span style="font-size: 0.85rem; font-weight: 600; color: #64748b;">⏱ {curr_slide['time_minutes']:.1f} min</span>
            </div>
            <h2 style="font-size: 2rem; margin-bottom: 6px; color: #0f172a;">{curr_slide['title']}</h2>
            <p style="font-style: italic; color: #64748b; margin-bottom: 24px;">Purpose: {curr_slide['purpose']}</p>
            <div style="display: grid; grid-template-columns: 1.4fr 1fr; gap: 24px; margin-bottom: 24px;">
                <div>
                    <h4 style="font-size: 0.78rem; font-weight: 700; color: #4f46e5; text-transform: uppercase; margin-bottom: 12px;">Key Bullet Points</h4>
                    <ul style="font-size: 1rem; line-height: 1.6; color: #1e293b; padding-left: 20px;">
                        {''.join(f'<li>{b}</li>' for b in curr_slide['bullets'])}
                    </ul>
                </div>
                <div>
                    <div class="case-study-box">
                        <strong style="color: #4f46e5; font-size: 0.74rem; text-transform: uppercase;">Real-World Case Study</strong><br>
                        <p style="margin-top: 6px; font-size: 0.92rem; color: #0f172a;">{curr_slide['case_study']}</p>
                    </div>
                </div>
            </div>
            <div class="notes-box">
                <strong>Speaker Notes:</strong> {curr_slide['speaker_notes']}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# TAB 3: SYSTEM ARCHITECTURE
# ==============================================================================
with tabs[2]:
    st.subheader("Deep Learning Platform Architecture")
    st.caption("End-to-end pipeline specifications and deep learning performance benchmarks.")

    st.markdown("""
    ```
    USER INPUT SPECIFICATION
        ↓
    INPUT VALIDATION (Bounds, slides 3-20, duration 3-60 min)
        ↓
    TEXT PREPROCESSING (Whitespace, tokenization, stopword filter, unigram/bigram candidate scoring)
        ↓
    TOPIC ANALYSIS (Rule-based taxonomy: Healthcare, Tech, Finance, Environment, Education)
        ↓
    SENTENCE-BERT EMBEDDING (all-MiniLM-L6-v2 -> 384-dimensional dense semantic vectors)
        ↓
    CONTENT PLANNER (Enforces exact requested slide count and balanced minutes-per-slide)
        ↓
    FLAN-T5 GENERATION (google/flan-t5-base with beam search=3, no-repeat n-grams=2)
        ↓
    SLIDE STRUCTURE GENERATION (Titles, 3-5 concise bullets, case studies, speaker notes)
        ↓
    SEMANTIC REFINEMENT (Sentence-BERT cosine similarity >= 0.88 redundancy reduction)
        ↓
    EXPORT SYSTEM (PPTX 16:9 widescreen, Markdown, JSON)
    ```
    """)

    st.markdown("### Technical Model Cards")
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.markdown("""
        **FLAN-T5 Generator**
        - Model: `google/flan-t5-base`
        - Type: Pretrained Seq2Seq Transformer
        - Task: Zero/few-shot prompt generation
        - Beam Search: 3 beams
        - No-repeat N-gram: 2
        """)
    with mc2:
        st.markdown("""
        **Sentence-BERT Embedding**
        - Model: `all-MiniLM-L6-v2`
        - Type: Siamese Dual-Encoder Network
        - Vector Dimension: 384
        - Metric: Cosine similarity
        - Normalized: True
        """)
    with mc3:
        st.markdown("""
        **Semantic Refiner**
        - Threshold: `Cosine >= 0.88`
        - Scope: Intra-slide & adjacent slides
        - Action: Replace redundant point
        - Metric Tracking: Yes
        """)

    st.markdown("---")
    st.success("✨ **Production Ready:** Generated decks can be exported as widescreen PPTX, Markdown, or JSON at any time.")


# ==============================================================================
# TAB 4: FEATURED PRESETS & DEMOS
# ==============================================================================
with tabs[3]:
    st.subheader("Featured Preset Demonstrations")
    st.markdown("Select either pre-defined presentation to load the deck instantly:")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.markdown("""
        ### 🩺 Demo 1: AI in Healthcare
        - **Topic:** Artificial Intelligence in Healthcare
        - **Slides:** 8 slides (12 minutes, 1.5 min/slide)
        - **Domain:** Clinical Healthcare & Biomedical
        - **Difficulty:** Intermediate | Technical Seminar
        """)
        if st.button("Load Healthcare Demo", type="primary", use_container_width=True):
            json_path = os.path.join(os.path.dirname(__file__), "outputs", "AI_Healthcare_Demo.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    st.session_state["current_presentation"] = json.load(f)
                st.success("Loaded Healthcare Demo! Switch to 'Create Presentation' or 'Presentation Slide View' to inspect.")
            else:
                st.error("Demo file not found.")

    with col_d2:
        st.markdown("""
        ### 🚗 Demo 2: Autonomous Driving
        - **Topic:** Autonomous Driving and Computer Vision
        - **Slides:** 10 slides (15 minutes, 1.5 min/slide)
        - **Domain:** Deep Learning / Computer Vision / Robotics
        - **Difficulty:** Advanced | Technical Seminar
        """)
        if st.button("Load Autonomous Driving Demo", type="primary", use_container_width=True):
            json_path = os.path.join(os.path.dirname(__file__), "outputs", "Autonomous_Driving_Demo.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    st.session_state["current_presentation"] = json.load(f)
                st.success("Loaded Autonomous Driving Demo! Switch to 'Create Presentation' or 'Presentation Slide View' to inspect.")
            else:
                st.error("Demo file not found.")
