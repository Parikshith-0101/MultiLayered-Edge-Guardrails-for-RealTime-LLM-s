import streamlit as st
import requests
import time

# Point this to the Docker container port
API_URL = "http://127.0.0.1:8000/api/v1/chat"

st.set_page_config(page_title="AI Assistant", page_icon="🛡️", layout="wide")

# ── INIT COUNTERS EARLY (before sidebar reads them) ───────────────────────────
if "total_messages" not in st.session_state:
    st.session_state.total_messages = 0
if "threats_blocked" not in st.session_state:
    st.session_state.threats_blocked = 0
if "threats_allowed" not in st.session_state:
    st.session_state.threats_allowed = 0


# ── SIDEBAR (defined first so bot_type is available for hero) ─────────────────
with st.sidebar:
    # Brand header
    st.markdown("""
<div style="padding:0.4rem 0 1.2rem; border-bottom:1px solid rgba(255,255,255,0.12); margin-bottom:1.2rem;">
    <div style="font-size:1.5rem; margin-bottom:2px;">🛡️</div>
    <div style="font-weight:700; font-size:1rem; letter-spacing:-0.3px;">Edge Guardrails</div>
    <div style="font-size:0.75rem; opacity:0.5; margin-top:1px;">Dual-Rail AI Security Gateway</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("**⚙️ Bot Persona**")
    bot_type = st.selectbox("Select Bot Persona:", ["Cafe", "Hospital"]).lower()

    st.markdown("---")
    st.markdown(
        "<div class='audit-header'><h3>🔍 Under the Hood</h3>"
        "<p>Real-time Security Pipeline Audit</p></div>",
        unsafe_allow_html=True
    )
    audit_placeholder = st.empty()

    st.markdown("---")
    st.markdown("**📊 Session Stats**")
    sidebar_stats_placeholder = st.empty()

    st.markdown("---")
    st.markdown("**🛡️ Active Security Rails**")
    st.success("✅ Deterministic (Regex/PII)")
    st.success("✅ Semantic (Local 1B Engine)")

    st.markdown("---")

    is_dark_mode = st.toggle("🌙 Dark Mode", value=True)
    st.markdown("---")

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_status = None
        st.session_state.total_messages = 0
        st.session_state.threats_blocked = 0
        st.session_state.threats_allowed = 0
        st.rerun()

# ── THEME & CSS INJECTION ──────────────────────────────────────────────────────
theme_bg = "#131314" if is_dark_mode else "#FFFFFF"
sidebar_bg = "#1E1F20" if is_dark_mode else "#F0F4F9"
card_bg = "#1E1F20" if is_dark_mode else "#F0F4F9"
text_color = "#E3E3E3" if is_dark_mode else "#1F1F1F"
border_color = "#333537" if is_dark_mode else "#E0E0E0"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, p, span, h1, h2, h3, h4, h5, h6, div, label, li {{
        font-family: 'Google Sans', 'Inter', sans-serif;
    }}
    
    /* Let Streamlit keep its icon fonts */
    .material-symbols-rounded, .material-icons, [class*="icon"] {{
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }}

    #MainMenu  {{ visibility: hidden; }}
    footer     {{ visibility: hidden; }}
    header     {{ background: transparent !important; }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 850px;
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {border_color}; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #555; }}

    .main-title {{
        text-align: center;
        font-weight: 500;
        font-size: 2.2rem;
        color: {text_color};
        margin-bottom: 0.2rem;
    }}
    .sub-title {{
        text-align: center;
        color: #888;
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }}
    .audit-header {{
        padding-left: 1rem;
        border-left: 4px solid #4285F4;
        background: {card_bg};
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
    }}
    .audit-header h3 {{ margin: 0 0 0.2rem; font-size: 1.05rem; font-weight: 500; }}
    .audit-header p  {{ margin: 0; font-size: 0.85rem; color: #888; }}

    /* Metric Cards Styling */
    [data-testid="stMetric"], [data-testid="metric-container"] {{
        background: {card_bg};
        border: 1px solid {border_color};
        padding: 1rem 1.2rem;
        border-radius: 12px;
        box-shadow: none;
    }}
    
    /* Global Theme */
    .stApp, [data-testid="stAppViewContainer"] {{ 
        background: {theme_bg} !important; 
        color: {text_color} !important;
    }}

    /* Fix the huge block behind the chat input */
    [data-testid="stBottomBlockContainer"], .stAppBottomBlockContainer, .stBottom, [data-testid="stBottom"] {{
        background: {theme_bg} !important;
        background-color: {theme_bg} !important;
        background-image: none !important;
        border-top: none !important;
    }}

    /* Force text colors to match our theme */
    p, h1, h2, h3, h4, h5, h6, textarea, label, [data-testid="stMetricValue"] {{
        color: {text_color} !important;
    }}
    
    [data-testid="stSidebar"] {{ 
        background: {sidebar_bg} !important; 
        border-right: 1px solid {border_color}; 
    }}
    
    /* --- CHAT MESSAGE STYLING --- */
    
    /* Ensure chat container and text breaks correctly */
    [data-testid="stChatMessage"] {{
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 0.5rem 0 !important;
        animation: none !important;
    }}
    
    /* Fix Overflow: apply styling to the inner content area and its children */
    [data-testid="stChatMessageContent"], 
    [data-testid="stChatMessageContent"] > div,
    [data-testid="stChatMessageContent"] .stMarkdown,
    [data-testid="stChatMessageContent"] p {{
        max-width: 100% !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: pre-wrap !important;
        overflow-x: hidden !important;
    }}

    /* Assistant Message (Clean, transparent, standard text) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
        background: transparent !important;
    }}
    
    /* User Message (Dark bubble with gradient border) */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {{
        background: linear-gradient(#1E1F22, #1E1F22) padding-box,
                    linear-gradient(90deg, #4285f4, #ea4335, #fbbc05) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 20px !important;
        color: #E3E3E3 !important;
        padding: 1rem 1.2rem !important;
        margin: 0.5rem 0;
    }}
    
    /* Remove avatars borders */
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {{
        box-shadow: none !important;
        border: none !important;
        background: transparent !important;
    }}

    /* Gemini-Style Chat Input */
    [data-testid="stChatInput"] {{
        max-width: 800px !important;
        width: 100% !important;
        margin: 0 auto !important;
        border-radius: 28px !important;
        border: 1px solid {border_color} !important;
        background: {card_bg} !important;
        box-shadow: none !important;
        animation: none !important;
    }}
    
    [data-testid="stChatInput"]:focus-within {{
        border: 1px solid #4285F4 !important;
        background: {theme_bg} !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
    }}

    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div {{
        border: none !important;
        background: transparent !important;
        background-color: transparent !important;
    }}
    
    [data-testid="stChatInput"] textarea, .stChatInputTextArea {{
        background: transparent !important;
        background-color: transparent !important;
        color: {text_color} !important;
        font-family: 'Google Sans', 'Inter', sans-serif !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── HERO HEADER ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; padding: 2rem 0 1.5rem;">
    <h1 class="main-title">AI Assistant</h1>
    <p class="sub-title">Persona: <b>{bot_type.title()}</b></p>
</div>
""", unsafe_allow_html=True)

# ── STATS BAR ──────────────────────────────────────────────────────────────────
main_stats_placeholder = st.empty()
st.markdown("---")

def update_metrics():
    with sidebar_stats_placeholder.container():
        col_a, col_b = st.columns(2)
        col_a.metric("🚨 Blocked",  st.session_state.get("threats_blocked", 0))
        col_b.metric("✅ Cleared",  st.session_state.get("threats_allowed", 0))
    with main_stats_placeholder.container():
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("💬 Messages Sent",   st.session_state.get("total_messages", 0))
        s2.metric("🚨 Threats Blocked", st.session_state.get("threats_blocked", 0))
        s3.metric("✅ Prompts Cleared", st.session_state.get("threats_allowed", 0))
        s4.metric("🤖 Active Persona",  bot_type.title())

# Initial draw
update_metrics()


# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "current_bot_type" not in st.session_state:
    st.session_state.current_bot_type = bot_type

if st.session_state.current_bot_type != bot_type:
    st.session_state.current_bot_type = bot_type
    st.session_state.messages = []
    st.session_state.last_status = None

if "messages" not in st.session_state or not st.session_state.messages:
    greeting = f"Hi there! I'm the **{bot_type.title()}** AI Assistant. How can I help you today?"
    st.session_state.messages = [{"role": "assistant", "content": greeting}]

# ── CHAT ───────────────────────────────────────────────────────────────────────
chat_container = st.container()
user_input = st.chat_input("Message the AI...")

with chat_container:
    for msg in st.session_state.messages:
        avatar = "✨" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("is_html", False):
                st.markdown(msg["content"], unsafe_allow_html=True)
            elif msg.get("is_error", False):
                st.error(msg["content"])
            else:
                st.markdown(msg["content"])

# ── SUBMIT HANDLER ─────────────────────────────────────────────────────────────
if user_input:
    st.session_state.total_messages += 1
    update_metrics()
    st.session_state.messages.append({"role": "user", "content": user_input})
    with chat_container:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

    with audit_placeholder.container():
        with st.status("Intercepting Request (Track A)...", expanded=True) as status:
            time.sleep(0.3)
            st.write("✅ Text Normalized")
            time.sleep(0.3)
            st.write("✅ PII & Keyword Scrubber")
            time.sleep(0.3)
            st.write("⏳ Semantic Engine (Llama Guard Evaluation)...")

            with chat_container:
                with st.chat_message("assistant", avatar="✨"):
                    message_placeholder = st.empty()
                    with st.spinner("Analyzing threat vectors..."):
                        try:
                            response = requests.post(
                                API_URL,
                                json={"bot_type": bot_type, "message": user_input}
                            )
                            st.session_state.last_status = response.status_code

                            if response.status_code == 200:
                                reply = response.json().get("bot_reply", "Error getting reply.")
                                message_placeholder.markdown(reply)
                                st.session_state.messages.append({"role": "assistant", "content": reply})
                                st.session_state.threats_allowed += 1
                                update_metrics()

                            elif response.status_code == 403:
                                error_detail = response.json().get("detail", "Access Denied")

                                if any(k in error_detail for k in ["PII", "Keyword", "Regex"]) \
                                        or "deterministic" in error_detail.lower():
                                    phase_detected = "Deterministic Engine (Fast-Fail)"
                                else:
                                    phase_detected = "Semantic Engine (Llama Guard)"

                                block_msg = f"""
<div style="background-color:rgba(255,75,75,0.08);border-left:4px solid #ef4444;
            border-radius:10px;padding:14px 16px;margin:4px 0;">
    <h4 style="margin:0 0 8px;color:#ef4444;">🚨 Threat Intercepted by Guardrails</h4>
    <b>Intercepted At Phase:</b> {phase_detected}<br/>
    <b>Reason:</b> {error_detail}<br/><br/>
    <span style="font-size:0.8rem;color:#888;">⚡ Request terminated before reaching Cloud LLM.</span>
</div>"""
                                message_placeholder.markdown(block_msg, unsafe_allow_html=True)
                                st.session_state.messages.append(
                                    {"role": "assistant", "content": block_msg, "is_html": True}
                                )
                                st.session_state.last_error = error_detail
                                st.session_state.threats_blocked += 1
                                update_metrics()
                            else:
                                err = f"Server Error: {response.status_code}"
                                message_placeholder.error(err)
                                st.session_state.messages.append(
                                    {"role": "assistant", "content": err, "is_error": True}
                                )

                        except requests.exceptions.ConnectionError:
                            st.session_state.last_status = 500
                            err = "❌ Cannot connect to the Guardrails API. Is Docker running?"
                            message_placeholder.error(err)
                            st.session_state.messages.append(
                                {"role": "assistant", "content": err, "is_error": True}
                            )

            if st.session_state.last_status == 200:
                status.update(label="Prompt Cleared (Track A) ✅", state="complete")
                st.write("✅ Semantic Check Passed (Llama Guard)")
                st.success("Safe prompt forwarded to Track B (Cloud LLM API)")
            elif st.session_state.last_status == 403:
                status.update(label="Threat Intercepted (Track A) 🚨", state="error")
                reason = st.session_state.get("last_error", "Unknown")
                if any(k in reason for k in ["PII", "Keyword", "Regex"]) \
                        or "deterministic" in reason.lower():
                    st.error(f"🚨 Blocked by Deterministic Engine: {reason}")
                else:
                    st.error(f"🚨 Blocked by Semantic Engine (Llama Guard): {reason}")
                st.error("Request safely blocked before reaching Cloud LLM")
            else:
                status.update(label="Connection Failed ❌", state="error")
                st.error("Failed to connect to the Guardrails Gateway.")

# ── PERSISTENT AUDIT LOG ───────────────────────────────────────────────────────
elif "last_status" in st.session_state and st.session_state.last_status:
    with audit_placeholder.container():
        if st.session_state.last_status == 200:
            with st.status("Prompt Cleared (Track A) ✅", expanded=True, state="complete"):
                st.write("✅ Text Normalized")
                st.write("✅ PII & Keyword Scrubber")
                st.write("✅ Semantic Check Passed (Llama Guard)")
                st.success("Safe prompt forwarded to Track B (Cloud LLM API)")
        elif st.session_state.last_status == 403:
            with st.status("Threat Intercepted (Track A) 🚨", expanded=True, state="error"):
                st.write("✅ Text Normalized")
                st.write("✅ PII & Keyword Scrubber")
                reason = st.session_state.get("last_error", "Unknown")
                if any(k in reason for k in ["PII", "Keyword", "Regex"]) \
                        or "deterministic" in reason.lower():
                    st.error(f"🚨 Blocked by Deterministic Engine: {reason}")
                else:
                    st.error(f"🚨 Blocked by Semantic Engine (Llama Guard): {reason}")
                st.error("Request safely blocked before reaching Cloud LLM")
        else:
            with st.status("Connection Failed ❌", expanded=True, state="error"):
                st.error("Failed to connect to the Guardrails Gateway.")
else:
    with audit_placeholder.container():
        st.info("💬 Send a message to watch the security pipeline in real-time.")