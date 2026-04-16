import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="AI Customer Support",
    page_icon="🤖"
)
st.title("🤖 AI Customer Support")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt := st.chat_input("Apa yang ingin anda tanyakan?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = requests.get(
            f"{BACKEND_URL}/chat",
            params={"query": prompt}
        ).json()

        if "answer" in response:
            answer = response['answer']

            with st.chat_message("assistant"):
                st.markdown(answer)

            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error("Error from backend: " + response.get("error", "Unknown error"))

    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")