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
    col_a, col_b = st.columns(2)
    col_a.metric("🚨 Blocked",  st.session_state.get("threats_blocked", 0))
    col_b.metric("✅ Cleared",  st.session_state.get("threats_allowed", 0))

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
theme_bg = "radial-gradient(circle at top center, #1e293b 0%, #020617 100%)" if is_dark_mode else "radial-gradient(circle at top center, #f8fafc 0%, #e2e8f0 100%)"
sidebar_bg = "rgba(2, 6, 23, 0.7)" if is_dark_mode else "rgba(248, 250, 252, 0.7)"
card_bg = "rgba(15, 23, 42, 0.6)" if is_dark_mode else "rgba(255, 255, 255, 0.9)"
text_color = "#f8fafc" if is_dark_mode else "#0f172a"
border_color = "rgba(56, 189, 248, 0.15)" if is_dark_mode else "rgba(148, 163, 184, 0.3)"
shadow_color = "rgba(56, 189, 248, 0.3)" if is_dark_mode else "rgba(148, 163, 184, 0.4)"
chat_bg = "rgba(30, 41, 59, 0.4)" if is_dark_mode else "rgba(255, 255, 255, 0.8)"
input_bg = "#1e1e1e" if is_dark_mode else "#ffffff"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');

    html, body, p, span, h1, h2, h3, h4, h5, h6, div, label {{
        font-family: 'Inter', sans-serif;
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
        padding-bottom: 2rem;
        max-width: 950px;
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {card_bg}; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {border_color}; }}

    @keyframes gradientBG {{
        0% {{background-position: 0% 50%;}}
        50% {{background-position: 100% 50%;}}
        100% {{background-position: 0% 50%;}}
    }}

    .main-title {{
        text-align: center;
        font-weight: 900;
        font-size: 3.2rem;
        background: linear-gradient(90deg, #00D2FF, #3A7BD5, #8A2387, #00D2FF);
        background-size: 300% 300%;
        animation: gradientBG 6s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
        text-shadow: 0px 4px 20px rgba(58,123,213,0.4);
    }}
    .sub-title {{
        text-align: center;
        color: #94A3B8;
        font-size: 1.1rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        margin-bottom: 3rem;
    }}
    .audit-header {{
        padding-left: 1rem;
        border-left: 4px solid #3A7BD5;
        background: rgba(58,123,213,0.1);
        padding: 0.8rem 1rem;
        border-radius: 0 10px 10px 0;
        margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        backdrop-filter: blur(5px);
    }}
    .audit-header h3 {{ margin: 0 0 0.2rem; font-size: 1.05rem; }}
    .audit-header p  {{ margin: 0; font-size: 0.85rem; color: #999; }}

    /* Metric Cards Styling */
    [data-testid="stMetric"], [data-testid="metric-container"] {{
        background: {card_bg};
        border: 1px solid {border_color};
        padding: 1rem 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    [data-testid="stMetric"]:hover, [data-testid="metric-container"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px {shadow_color};
        border: 1px solid rgba(56, 189, 248, 0.6);
    }}
    
    /* Global Theme */
    .stApp, [data-testid="stAppViewContainer"] {{ 
        background: {theme_bg} !important; 
        color: {text_color} !important;
    }}

    /* Fix the huge block behind the chat input */
    [data-testid="stBottomBlockContainer"], .stAppBottomBlockContainer, .stBottom, [data-testid="stBottom"] {{
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
    }}

    /* Force text colors to match our theme */
    p, h1, h2, h3, h4, h5, h6, textarea, label, [data-testid="stMetricValue"] {{
        color: {text_color} !important;
    }}
    
    [data-testid="stSidebar"] {{ 
        background: {sidebar_bg} !important; 
        border-right: 1px solid rgba(150,150,150,0.1); 
        backdrop-filter: blur(15px); 
    }}
    
    /* Chat Message Defaults & Animations */
    @keyframes slideUpFade {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    [data-testid="stChatMessage"] {{ 
        background: {chat_bg} !important;
        border: 1px solid rgba(150, 150, 150, 0.1);
        border-radius: 15px; 
        backdrop-filter: blur(8px);
        animation: slideUpFade 0.4s ease-out forwards;
    }}
    
    /* Avatar Glows & Hide default icon */
    [data-testid="stChatMessageAvatarUser"] {{
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
        border: 2px solid rgba(56, 189, 248, 0.8);
    }}
    [data-testid="stChatMessageAvatarAssistant"] {{
        box-shadow: 0 0 15px rgba(138, 35, 135, 0.4);
        border: 2px solid rgba(138, 35, 135, 0.8);
    }}

    /* Gemini-Style Animated Chat Input */
    @keyframes border-flow {{
        0% {{ background-position: 0% 50%; }}
        100% {{ background-position: 200% 50%; }}
    }}
    
    [data-testid="stChatInput"] {{
        max-width: 750px !important;
        width: 85% !important;
        margin: 0 auto !important;
        border-radius: 30px !important;
        border: 2px solid transparent !important;
        background: linear-gradient({input_bg}, {input_bg}) padding-box, 
                    linear-gradient(90deg, #4285f4, #ea4335, #fbbc05, #34a853, #4285f4) border-box !important;
        background-size: 200% 200% !important;
        animation: border-flow 4s linear infinite !important;
        box-shadow: 0 8px 30px rgba(66, 133, 244, 0.2) !important;
        overflow: hidden !important;
    }}
    
    [data-testid="stChatInput"]:focus-within {{
        box-shadow: 0 8px 32px rgba(66, 133, 244, 0.4) !important;
    }}

    /* Remove background and square borders from Streamlit inner elements to let the outer glow shine */
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div {{
        border: none !important;
        background: transparent !important;
        background-color: transparent !important;
        border-radius: 30px !important;
    }}
    
    [data-testid="stChatInput"] textarea, .stChatInputTextArea {{
        background: transparent !important;
        background-color: transparent !important;
        color: {text_color} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── HERO HEADER ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; padding: 2rem 0 1.5rem;">
    <div style="display:inline-block; background:rgba(121,40,202,0.15);
                border:1px solid rgba(121,40,202,0.4); border-radius:999px;
                padding:4px 16px; font-size:0.78rem; font-weight:600;
                color:#a78bfa; letter-spacing:0.8px; text-transform:uppercase;
                margin-bottom:1rem;">
        🛡️ &nbsp; Multi-Layer Security Active
    </div>
    <h1 class="main-title">AI Assistant</h1>
    <p class="sub-title">Secured by Dual-Rail Edge Guardrails &nbsp;·&nbsp; Persona: <b>{bot_type.title()}</b></p>
</div>
""", unsafe_allow_html=True)

# ── STATS BAR ──────────────────────────────────────────────────────────────────
s1, s2, s3, s4 = st.columns(4)
s1.metric("💬 Messages Sent",   st.session_state.get("total_messages", 0))
s2.metric("🚨 Threats Blocked", st.session_state.get("threats_blocked", 0))
s3.metric("✅ Prompts Cleared", st.session_state.get("threats_allowed", 0))
s4.metric("🤖 Active Persona",  bot_type.title())
st.markdown("---")


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