import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from pypdf import PdfReader

# Page setup
st.set_page_config(page_title="PDF AI Assistant", page_icon="📄", layout="wide")

# Load env
load_dotefile = load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") 

if not api_key:
    st.error("❌ GOOGLE_API_KEY not found in.env file")
    st.stop()

# OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Poppins', sans-serif;
    color: #2d3748;
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(102, 126, 234, 0.3);
    padding-top: 2rem;
}

.main-title {
    text-align: center;
    font-size: 48px;
    font-weight: 700;
    background: linear-gradient(90deg, #ffffff, #e0e7ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 15px;
    margin-bottom: 5px;
    letter-spacing: -1px;
}

.sub-title {
    text-align: center;
    font-size: 16px;
    color: #e0e7ff;
    margin-bottom: 30px;
    font-weight: 400;
}

.stChatMessage {
    background: white;
    border-radius: 18px;
    padding: 18px 20px;
    margin: 12px 0;
    color: #2d3748;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border-left: 4px solid #667eea;
}

.stChatInputContainer {
    background: white;
    border-radius: 30px;
    border: 2px solid #667eea;
    padding: 5px 15px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
}

div[data-testid="stMetric"] {
    background: white;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}

div[data-testid="stMetricValue"] {
    color: #667eea;
    font-weight: 700;
    font-size: 26px;
}

div[data-testid="stMetricLabel"] {
    color: #718096;
    font-weight: 600;
    font-size: 14px;
}

.stButton > button {
    background: linear-gradient(90deg, #667eea, #764ba2);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: 600;
    padding: 10px;
    transition: all 0.3s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

h1, h2, h3, h4 {
    color: white !important;
}

[data-testid="stSidebar"] h1 {
    color: #667eea !important;
}
</style>
""", unsafe_allow_html=True)
# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# Sidebar
with st.sidebar:
    st.markdown("<h1 style='text-align:center;'>📄 PDF AI</h1>", unsafe_allow_html=True)
    st.markdown("---")

    uploaded_file = st.file_uploader("PDF Uploaded", type="pdf")

    if uploaded_file:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        st.session_state.pdf_text = text
        st.success(f"✅ {len(reader.pages)} pages loaded")

    st.markdown("---")
    st.success("🟢 OpenRouter Connected")

    if st.button("🆕 New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.info("**PDF AI Assistant**\n\nPowered by Llama 3.1 8B Free")

# Main
st.markdown("<div class='main-title'>📄 PDF AI Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Upload PDF and Ask Anything</div>", unsafe_allow_html=True)

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💬 Messages", len(st.session_state.messages))
with col2:
    st.metric("📄 PDF Status", "Loaded" if st.session_state.pdf_text else "No PDF")
with col3:
    st.metric("🟢 Status", "Online")

st.markdown("---")

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("ask me Anything ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🧠 thinking ..."):
            try:
                
                context = ""
                if st.session_state.pdf_text:
                    context = f"Pdf content:\n{st.session_state.pdf_text[:8000]}\n\nquestion: {prompt}\ngenerate answer using pdf."
                else:
                    context = prompt

                response = client.chat.completions.create(
                    model="meta-llama/llama-3.1-8b-instruct",
                    messages=[{"role": "user", "content": context}],
                    temperature=0.7,
                    max_tokens=1000
                )

                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.caption("give answer according to pdf")