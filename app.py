"""
app.py — Streamlit Chat UI for AarthaSandhan (अर्थसन्धान).
Claude-style chat interface with Mr. Wagle persona.
Supports Dark and Light mode toggle.
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(__file__))

from src.retrieve import retrieve
from src.prompt import build_prompt
from src.answer import get_answer

# ── Load environment ──────────────────────────────────────────────────────────
load_dotenv()


def get_api_key() -> str | None:
    """Get Groq API key from st.secrets, .env, or environment."""
    try:
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass
    return os.environ.get("GROQ_API_KEY")


# ── Mr. Wagle's welcome message ──────────────────────────────────────────────
WELCOME_MESSAGE = (
    "नमस्ते! म Mr. Wagle हुँ। आर्थिक वर्ष २०८३/८४ को राष्ट्रिय बजेटबारे "
    "जे सोध्नु छ सोध्नुस् — शिक्षा, स्वास्थ्य, पूर्वाधार, कर, वा अरू कुनै विषय। "
    "म सरल भाषामा बुझाउँछु।"
)

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AarthaSandhan — Mr. Wagle सँग बजेट बुझौं",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Theme state ───────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ── Theme colors ──────────────────────────────────────────────────────────────
LIGHT = {
    "bg": "#ffffff",
    "text": "#1a1a2e",
    "text_secondary": "#8b8fa3",
    "border": "#f0f0f0",
    "bubble_assistant": "#f7f7f8",
    "bubble_user_bg": "#1a1a2e",
    "bubble_user_text": "#ffffff",
    "source_bg": "#f5f5fa",
    "source_border": "#e5e5ea",
    "source_text": "#3a3a4a",
    "badge_bg": "#1a1a2e",
    "badge_text": "#ffffff",
    "dot_color": "#b0b3c6",
    "toggle_icon": "🌙",
}
DARK = {
    "bg": "#0d1117",
    "text": "#e6edf3",
    "text_secondary": "#7d8590",
    "border": "#21262d",
    "bubble_assistant": "#161b22",
    "bubble_user_bg": "#1f6feb",
    "bubble_user_text": "#ffffff",
    "source_bg": "#161b22",
    "source_border": "#30363d",
    "source_text": "#c9d1d9",
    "badge_bg": "#1f6feb",
    "badge_text": "#ffffff",
    "dot_color": "#484f58",
    "toggle_icon": "☀️",
}

t = DARK if st.session_state.dark_mode else LIGHT

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global ── */
    .stApp {{
        font-family: 'Inter', sans-serif;
        background: {t["bg"]} !important;
        color: {t["text"]} !important;
    }}
    .block-container {{
        max-width: 780px !important;
        padding-top: 0.5rem !important;
        padding-bottom: 5rem !important;
    }}

    /* ── Header row ── */
    .header-row {{
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem 0 0.5rem;
        border-bottom: 1px solid {t["border"]};
        margin-bottom: 1rem;
        position: relative;
    }}
    .header-center {{
        text-align: center;
    }}
    .header-center h1 {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {t["text"]};
        margin: 0 0 0.15rem;
        letter-spacing: -0.02em;
    }}
    .header-center .subtitle {{
        color: {t["text_secondary"]};
        font-size: 0.85rem;
        font-weight: 400;
    }}

    /* ── Theme toggle button ── */
    .theme-toggle {{
        position: absolute;
        right: 0;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        font-size: 1.3rem;
        background: {t["bubble_assistant"]};
        border: 1px solid {t["border"]};
        border-radius: 50%;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        text-decoration: none;
    }}
    .theme-toggle:hover {{
        transform: translateY(-50%) scale(1.1);
        border-color: {t["text_secondary"]};
    }}

    /* ── Chat messages ── */
    .stChatMessage {{
        background: transparent !important;
    }}
    [data-testid="stChatMessageContent"] {{
        background: {t["bubble_assistant"]} !important;
        color: {t["text"]} !important;
        border-radius: 16px !important;
    }}
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li,
    [data-testid="stChatMessageContent"] h1,
    [data-testid="stChatMessageContent"] h2,
    [data-testid="stChatMessageContent"] h3 {{
        color: {t["text"]} !important;
    }}

    /* ── Source pills ── */
    .sources-container {{
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid {t["border"]};
    }}
    .sources-label {{
        font-size: 0.72rem;
        color: {t["text_secondary"]};
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }}
    .source-pills-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
    }}
    .source-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: {t["source_bg"]};
        border: 1px solid {t["source_border"]};
        border-radius: 8px;
        padding: 0.3rem 0.65rem;
        font-size: 0.76rem;
        color: {t["source_text"]};
        transition: all 0.15s ease;
    }}
    .source-pill:hover {{
        border-color: {t["text_secondary"]};
    }}
    .page-badge {{
        background: {t["badge_bg"]};
        color: {t["badge_text"]};
        border-radius: 4px;
        padding: 1px 5px;
        font-size: 0.68rem;
        font-weight: 600;
    }}
    .score-badge {{
        color: {t["text_secondary"]};
        font-size: 0.68rem;
    }}

    /* ── Typing dots ── */
    .typing-dots {{
        display: flex;
        gap: 5px;
        padding: 0.3rem 0;
    }}
    .typing-dots span {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: {t["dot_color"]};
        animation: bounce 1.4s infinite;
    }}
    .typing-dots span:nth-child(2) {{ animation-delay: 0.2s; }}
    .typing-dots span:nth-child(3) {{ animation-delay: 0.4s; }}
    @keyframes bounce {{
        0%, 60%, 100% {{ opacity: 0.3; transform: translateY(0); }}
        30% {{ opacity: 1; transform: translateY(-5px); }}
    }}

    /* ── Chat input ── */
    .stChatInput > div {{
        border-color: {t["border"]} !important;
    }}
    .stChatInput textarea {{
        color: {t["text"]} !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* ── Hide Streamlit chrome ── */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
</style>
""", unsafe_allow_html=True)

# ── Header with theme toggle ─────────────────────────────────────────────────
header_col1, header_col2 = st.columns([6, 1])
with header_col1:
    st.markdown(f"""
    <div style="text-align:center; padding:1rem 0 0.5rem; border-bottom:1px solid {t['border']}; margin-bottom:1rem;">
        <h1 style="font-size:1.5rem; font-weight:700; color:{t['text']}; margin:0 0 0.15rem; letter-spacing:-0.02em;">🏛️ AarthaSandhan</h1>
        <div style="color:{t['text_secondary']}; font-size:0.85rem;">Mr. Wagle सँग बजेट बुझौं</div>
    </div>
    """, unsafe_allow_html=True)
with header_col2:
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    if st.button(t["toggle_icon"], key="theme_toggle", help="Toggle Dark/Light Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE,
            "sources": [],
        }
    ]


def render_sources(sources: list[dict]):
    """Render source pills below a message."""
    if not sources:
        return
    pills_html = ""
    for s in sources:
        title = s.get("section_title", "—")
        if len(title) > 50:
            title = title[:50] + "…"
        page = s.get("page_number", "?")
        score = s.get("score", 0)
        score_pct = f"{score * 100:.0f}%"
        pills_html += (
            f'<div class="source-pill">'
            f'📄 {title} '
            f'<span class="page-badge">p.{page}</span> '
            f'<span class="score-badge">{score_pct}</span>'
            f'</div>'
        )
    st.markdown(f"""
    <div class="sources-container">
        <div class="sources-label">📚 स्रोतहरू / Sources</div>
        <div class="source-pills-row">{pills_html}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Render chat history ──────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🏛️" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])
        if msg.get("sources"):
            render_sources(msg["sources"])

# ── Chat input ────────────────────────────────────────────────────────────────
query = st.chat_input("बजेटबारे सोध्नुस्...")

if query:
    # Add and display user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Check API key
    api_key = get_api_key()
    if not api_key:
        error_msg = (
            "⚠️ GROQ_API_KEY सेट गरिएको छैन। "
            "कृपया `.env` फाइलमा वा Streamlit secrets मा सेट गर्नुहोस्।"
        )
        with st.chat_message("assistant", avatar="🏛️"):
            st.markdown(error_msg)
        st.session_state.messages.append({
            "role": "assistant", "content": error_msg, "sources": [],
        })
        st.stop()

    # Show typing indicator while processing
    with st.chat_message("assistant", avatar="🏛️"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown(
            '<div class="typing-dots"><span></span><span></span><span></span></div>',
            unsafe_allow_html=True,
        )

        try:
            # Step 1: Retrieve relevant chunks
            chunks = retrieve(query, top_k=3)

            if not chunks:
                answer_text = (
                    "माफ गर्नुहोस्, यो प्रश्नसँग सम्बन्धित जानकारी बजेट दस्तावेजमा "
                    "फेला परेन। कृपया अर्को तरिकाले सोध्नुस्।"
                )
                sources = []
            else:
                # Step 2: Build prompt
                messages = build_prompt(query, chunks)

                # Step 3: Get answer from Groq
                answer_text = get_answer(messages, api_key=api_key)
                sources = [
                    {
                        "section_title": c["section_title"],
                        "page_number": c["page_number"],
                        "score": c["score"],
                    }
                    for c in chunks
                ]

        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg or "413" in error_msg or "tokens" in error_msg.lower():
                answer_text = (
                    "⚠️ अहिले API को सीमा पुगेको छ। "
                    "कृपया केही सेकेन्ड पछि फेरि प्रयास गर्नुहोस्।"
                )
            else:
                answer_text = f"❌ त्रुटि भयो: {error_msg}"
            sources = []

        # Clear typing dots, show answer
        typing_placeholder.empty()
        st.markdown(answer_text)
        render_sources(sources)

    # Save to session
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer_text,
        "sources": sources,
    })
