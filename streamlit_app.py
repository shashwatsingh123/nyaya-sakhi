import streamlit as st
import requests
import os

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Nyaya Sakhi", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# This URL must be set in Streamlit Cloud Secrets!
# Format: https://your-ngrok-url.ngrok-free.app
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# ══════════════════════════════════════════════════════════════════════════════
# STYLING
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Add a subtle purple tint to match the original Gradio theme */
    .stApp {
        background-color: #FAFAFC;
    }
    .main-header {
        color: #6B46C1;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/200px-Emblem_of_India.svg.png", width=100)
    st.header("🚨 Emergency Helplines")
    st.markdown("""
    | Service | Number |
    |---|---|
    | **Women Helpline** | **181** |
    | **Police** | **100** |
    | **CHILDLINE** | **1098** |
    | **Cyber Crime** | **1930** |
    | **Legal Aid (NALSA)** | **15100** |
    """)
    st.divider()
    st.caption("⚠️ **Disclaimer:** Nyaya Sakhi provides legal information based on the Bharatiya Nyaya Sanhita, not official legal representation. In emergencies, call the police immediately.")
    
    st.divider()
    st.caption("Powered by locally hosted AI model and Vector DB via Ngrok Tunnel.")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CHAT INTERFACE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="main-header">⚖️ Nyaya Sakhi</h1>', unsafe_allow_html=True)
st.markdown("### AI Legal Advisor for Women in India")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Namaste! I am Nyaya Sakhi. Describe your legal concern in any Indian language, and I will find the relevant laws and guide you."}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="⚖️" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask a legal question... (e.g., 'My husband beats me, what can I do?')"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Call API
    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Searching the Bharatiya Nyaya Sanhita..."):
            try:
                # Ensure the URL doesn't have double slashes
                url = f"{API_URL.rstrip('/')}/ask"
                response = requests.post(url, json={"message": prompt}, timeout=120)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("response", "")
                    sources = data.get("sources", [])
                    
                    # Display Answer
                    st.markdown(answer)
                    
                    # Display Sources cleanly in an expander
                    if sources:
                        with st.expander("📚 View Legal Sources Cited"):
                            for s in sources:
                                st.write(f"- **{s['title']}** (Page {s['page']})")
                                st.caption(f"Match relevance: {s['relevance']}")
                    
                    # Add to history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Server returned an error: {response.status_code}")
                    st.error("Please ensure the local API server and Ngrok are running.")
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Could not connect to the local API server.")
                st.info("The host's laptop might be turned off, or the Ngrok tunnel has expired.")
            except requests.exceptions.Timeout:
                st.error("⏳ The request timed out. The local LLM might be taking too long to answer.")
            except Exception as e:
                st.error(f"⚠️ An unexpected error occurred: {str(e)}")
