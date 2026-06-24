import streamlit as st
import requests

# Point this to the Docker container port
API_URL = "http://127.0.0.1:8000/api/v1/chat"

st.set_page_config(page_title="Edge Guardrails Gateway", page_icon="🛡️")

st.title("🛡️ Edge Guardrails Gateway")
st.markdown("Test the dual-rail security engine against live Cloud AI.")

# Sidebar for Configuration
with st.sidebar:
    st.header("Bot Configuration")
    bot_type = st.selectbox("Select Bot Persona:", ["Cafe", "Hospital"]).lower()
    st.markdown("---")
    st.markdown("**Active Security Rails:**")
    st.markdown("✅ Deterministic (Regex/PII)")
    st.markdown("✅ Semantic (Local 1B Engine)")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
if user_input := st.chat_input("Type your message here..."):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call the API
    with st.spinner("Analyzing threat vectors..."):
        try:
            response = requests.post(API_URL, json={"bot_type": bot_type, "message": user_input})
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("bot_reply", "Error getting reply.")
                st.session_state.messages.append({"role": "assistant", "content": reply})
                with st.chat_message("assistant"):
                    st.markdown(reply)
            elif response.status_code == 403:
                error_detail = response.json().get('detail', 'Access Denied')
                block_msg = f"🚨 **BLOCKED BY GUARDRAILS** 🚨\n\n*Reason: {error_detail}*"
                st.session_state.messages.append({"role": "assistant", "content": block_msg})
                with st.chat_message("assistant"):
                    st.error(block_msg)
            else:
                st.error(f"Server Error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to the Guardrails API. Is Docker running?")