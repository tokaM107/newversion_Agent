import streamlit as st
import sys, os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.graph.nodes.analyze import analyze_node
from app.graph.nodes.geocode import geocode_node
from app.graph.nodes.decision import check_completeness, check_answer_scope, ask_user_node
from app.graph.nodes.route import route_node
from app.graph.nodes.response import filter_response_node, full_response_node


# ── Pipeline ──────────────────────────────────────────────
def run_pipeline(query: str) -> str:
    state = {"query": query}

    state = analyze_node(state)
    state = geocode_node(state)

    completeness = check_completeness(state)
    if completeness == "ask_user":
        state = ask_user_node(state)
        return state.get("final_answer", "محتاج معلومات أكتر.")

    state = route_node(state)
    if state.get("error"):
        return state.get("final_answer", "حصل مشكلة. جرّب تاني.")

    scope = check_answer_scope(state)
    if scope == "partial":
        state = filter_response_node(state)
    else:
        state = full_response_node(state)

    return state.get("final_answer", "مفيش نتائج.")


# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Al-Osta",
    page_icon="🚌",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Theme toggle (dark / light) ──────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

dark = st.session_state.dark_mode

if dark:
    bg = "#0e1117"
    chat_bg = "#1a1d23"
    user_bg = "#2b313e"
    bot_bg = "#1e2530"
    text_color = "#e0e0e0"
    input_bg = "#1a1d23"
    border = "#333"
    accent = "#4fc3f7"
else:
    bg = "#ffffff"
    chat_bg = "#f7f7f8"
    user_bg = "#e3f2fd"
    bot_bg = "#f0f0f0"
    text_color = "#1a1a1a"
    input_bg = "#ffffff"
    border = "#ddd"
    accent = "#1976d2"

# ── Global CSS ────────────────────────────────────────────
st.markdown(f"""
<style>
    /* Hide default streamlit elements */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
        max-width: 800px;
    }}

    /* Page background */
    .stApp {{
        background-color: {bg};
    }}

    /* Title */
    .app-title {{
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: {accent};
        padding: 0.5rem 0 0.2rem 0;
        letter-spacing: 1px;
    }}
    .app-subtitle {{
        text-align: center;
        font-size: 0.9rem;
        color: {text_color}99;
        margin-bottom: 1rem;
    }}

    /* Chat messages */
    .chat-container {{
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
        padding: 0.5rem 0;
    }}
    .msg-row {{
        display: flex;
        gap: 0.6rem;
        align-items: flex-start;
    }}
    .msg-row.user {{
        flex-direction: row-reverse;
    }}
    .msg-avatar {{
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
        margin-top: 2px;
    }}
    .msg-bubble {{
        padding: 0.75rem 1rem;
        border-radius: 16px;
        max-width: 80%;
        line-height: 1.6;
        font-size: 0.95rem;
        white-space: pre-wrap;
        word-wrap: break-word;
        direction: rtl;
        text-align: right;
    }}
    .msg-bubble.user {{
        background: {user_bg};
        color: {text_color};
        border-bottom-right-radius: 4px;
    }}
    .msg-bubble.bot {{
        background: {bot_bg};
        color: {text_color};
        border-bottom-left-radius: 4px;
        border: 1px solid {border};
    }}

    /* Theme toggle button */
    .theme-toggle {{
        position: fixed;
        top: 12px;
        right: 16px;
        z-index: 999;
    }}

    /* Spinner */
    .stSpinner > div {{
        border-color: {accent} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── Theme toggle button ──────────────────────────────────
col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    icon = "☀️" if dark else "🌙"
    st.button(icon, on_click=toggle_theme, help="Toggle dark/light mode")

# ── Title ─────────────────────────────────────────────────
st.markdown('<div class="app-title">🚌 Al-Osta</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">دليلك للمواصلات في إسكندرية</div>', unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat messages
chat_html = '<div class="chat-container">'
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"].replace("\n", "<br>")
    if role == "user":
        chat_html += f'''
        <div class="msg-row user">
            <div class="msg-avatar" style="background:{user_bg};">👤</div>
            <div class="msg-bubble user">{content}</div>
        </div>'''
    else:
        chat_html += f'''
        <div class="msg-row">
            <div class="msg-avatar" style="background:{accent}22;">🚌</div>
            <div class="msg-bubble bot">{content}</div>
        </div>'''
chat_html += '</div>'

st.markdown(chat_html, unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────
user_input = st.chat_input("اكتب سؤالك هنا... مثلاً: عايز اروح محطة مصر من سيدي بشر")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Run pipeline
    with st.spinner("🔍 بدوّر على أحسن طريق..."):
        answer = run_pipeline(user_input)

    # Add bot response
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Rerun to render
    st.rerun()
