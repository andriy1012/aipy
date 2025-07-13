import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import time

# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Andriyy AI Tes",
    page_icon="🤖",
    layout="wide",
)

# --------------------------------------------------
# LOAD API‑KEY (Cloud ➜ st.secrets | Local ➜ .env)
# --------------------------------------------------
try:
    GOOGLE_GEMINI_API_KEY = st.secrets["GOOGLE_GEMINI_API_KEY"]     # Streamlit Cloud
except Exception:
    load_dotenv()                                                   # Local
    GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

if not GOOGLE_GEMINI_API_KEY:
    st.error("❌ API‑key belum ditemukan di Secrets atau .env")
    st.stop()

# DEBUG (log Cloud)
print("🟢 Keys in st.secrets:", list(st.secrets.keys()) if st.secrets else "EMPTY")
print("📦 KEY FROM st.secrets:", st.secrets.get("GOOGLE_GEMINI_API_KEY", "⛔ NOT FOUND"))

# --------------------------------------------------
# INIT GEMINI
# --------------------------------------------------
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# --------------------------------------------------
# HELPER
# --------------------------------------------------
def ask_ai(question: str) -> str:
    """Kirim prompt ke Gemini + simpan ke history."""
    st.session_state.conversation.append({"role": "user", "content": question})

    try:
        chat = model.start_chat(history=[
            {"role": m["role"], "parts": [m["content"]]}
            for m in st.session_state.conversation
        ])
        reply = chat.send_message(question).text
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    st.session_state.conversation.append({"role": "assistant", "content": reply})
    return reply

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.title("Settings")
    if st.button("🗑 Clear Chat"):
        st.session_state.conversation = []
        st.rerun()

# --------------------------------------------------
# MAIN UI
# --------------------------------------------------
st.title("💬 Bearman Chat")
st.caption("Ayo mulai!")

chat_container = st.container(height=600, border=False)

# — tampilkan history —
for msg in st.session_state.conversation:
    with chat_container:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# — input user —
if prompt := st.chat_input("Tulis pertanyaan di sini…"):
    with chat_container:
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("Berpikir…"):
            response = ask_ai(prompt)
            with st.chat_message("assistant"):
                st.write(response)

        # delay opsional bila rate‑limit
        if "429" in response:
            time.sleep(10)
