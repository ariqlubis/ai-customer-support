import streamlit as st
import requests
import os
import json

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="AI Customer Support", page_icon="🤖")
st.title("🤖 AI Customer Support")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])
        if message['role'] == "assistant" and "debug" in message:
            with st.expander("🔍 Trace AI Thought Process"):
                st.write("**Top Retrieved Docs:**")
                for i, d in enumerate(message["debug"].get("retrieved_docs", [])):
                    st.caption(f"{i+1}. {d[:250]}...")

if prompt := st.chat_input("Apa yang ingin anda tanyakan?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        formatted_history = []
        messages = st.session_state.messages

        for i in range(0, len(messages)-1, 2):
            if messages[i]['role'] == 'user' and messages[i+1]['role'] == 'assistant':
                formatted_history.append({
                    "question": messages[i]['content'],
                    "answer": messages[i+1]['content']
                })
    
        payload = {
            "query": prompt,
            "history": formatted_history
        }

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            debug_info = {}
            
            response_obj = requests.post(f"{BACKEND_URL}/chat", json=payload, stream=True)
            
            if response_obj.status_code == 200:
                for line in response_obj.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        
                        if "error" in data:
                            st.error(f"Backend Error: {data['error']}")
                            break

                        data_type = data.get("type")
                        if data_type == "debug":
                            debug_info = data.get("data", {})
                        elif data_type == "chunk":
                            full_response += data.get("content", "")
                            message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                if debug_info:
                    with st.expander("🔍 Trace AI Thought Process"):
                        st.write("**Top Retrieved Docs:**")
                        for i, d in enumerate(debug_info.get("retrieved_docs", [])):
                            st.caption(f"{i+1}. {d[:250]}...")

                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response, 
                    "debug": debug_info
                })
            else:
                st.error(f"Error dari server: {response_obj.text}")

    except Exception as e:
        st.error(f"Failed to connect: {e}")
