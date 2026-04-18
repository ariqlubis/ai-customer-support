import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="AI Customer Support", page_icon="🤖")
st.title("🤖 AI Customer Support")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Update Loop Pesan: Tampilkan Debug jika ada
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])
        # Tampilkan detail proses jika itu jawaban assistant
        if message['role'] == "assistant" and "debug" in message:
            with st.expander("🔍 Trace AI Thought Process"):
                st.write("**Standalone Query:**", message["debug"].get("standalone_query"))
                st.write("**Top Retrieved Docs:**")
                for i, d in enumerate(message["debug"].get("reranked_docs", [])):
                    st.caption(f"{i+1}. {d[:250]}...")

if prompt := st.chat_input("Apa yang ingin anda tanyakan?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = requests.get(f"{BACKEND_URL}/chat", params={"query": prompt}).json()

        if "answer" in response:
            answer = response['answer']
            debug_info = response.get('debug', {}) 

            with st.chat_message("assistant"):
                st.markdown(answer)
                with st.expander("🔍 Trace AI Thought Process"):
                    st.write("**Standalone Query:**", debug_info.get("standalone_query"))
                    st.write("**Top Retrieved Docs:**")
                    for i, d in enumerate(debug_info.get("reranked_docs", [])):
                        st.caption(f"{i+1}. {d[:250]}...")

            # Simpan pesan BESERTA data debug-nya
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer, 
                "debug": debug_info
            })
        else:
            st.error("Error: " + response.get("error", "Unknown error"))
    except Exception as e:
        st.error(f"Failed to connect: {e}")
