import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai

# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Andriyy AI Tes",
    page_icon="🤖",
    layout="wide",
)

# --------------------------------------------------
# GOOGLE GENERATIVE AI CLIENT

try:
    GOOGLE_GEMINI_API_KEY = st.secrets["GOOGLE_GEMINI_API_KEY"]
except Exception:
    # Fallback ke .env saat lokal
    from dotenv import load_dotenv
    load_dotenv()
    GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

if not GOOGLE_GEMINI_API_KEY:
    st.error("❌ API‑key belum ditemukan di secrets atau .env")
    st.stop()
if st.secrets:
    print("🟢 Keys in st.secrets:", list(st.secrets.keys()))
else:
    print("🔴 st.secrets is empty!")
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

chat = model.start_chat(history=[])
response = chat.send_message("Apa itu AI?")
print(response.text)
# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation: list[dict[str, str]] = []

# --------------------------------------------------
# HELPER – kirim prompt ke Google Gemini
# --------------------------------------------------

def ask_ai(question: str) -> str:
    st.session_state.conversation.append({"role": "user", "content": question})

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Gunakan history yang sesuai
        chat = model.start_chat(history=[
            {"role": m["role"], "parts": [m["content"]]}
            for m in st.session_state.conversation
        ])

        response = chat.send_message(question)

        reply = response.text
        st.session_state.conversation.append({"role": "assistant", "content": reply})
        return reply

    except Exception as e:
        return f"⚠️ Error: {e}"


# --------------------------------------------------
# SIDEBAR (hanya clear chat dan ganti API‑key)
# --------------------------------------------------
with st.sidebar:
    st.title("Settings")
    if st.button("Clear Chat"):
        st.session_state.conversation = []
        st.rerun()

# --------------------------------------------------
# MAIN UI
# --------------------------------------------------
st.title("💬 Bearman Chat")
st.caption("Ayo mulai!!")

chat_container = st.container(height=600, border=False)

# tampilkan riwayat
for msg in st.session_state.conversation:
    with chat_container:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# input user
if prompt := st.chat_input("monggo"):
    with chat_container:
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("Berpikir, mohon tunggu..."):
            response = ask_ai(prompt)

            with st.chat_message("assistant"):
                st.write(response)

        # optional: delay jika rate‑limit
        if "429" in response:
            time.sleep(10)
