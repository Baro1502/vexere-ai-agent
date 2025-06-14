import os
import re
import requests
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

# ================== Streaming Response Function ==================
def get_response(user_input, image_path=None):
    """
    Send request to /chat or /image depending on whether an image is included.
    Stream the response back with UTF-8 decoding.
    """
    if image_path:
        url = "http://127.0.0.1:1206/image"
        with open(image_path, 'rb') as img_file:
            files = {
                'file': ('image.jpg', img_file, 'image/jpeg'),
                'user_input': (None, user_input)
            }
            response = requests.post(url, files=files, stream=True)
    else:
        url = "http://127.0.0.1:1206/chat"
        headers = {"Content-Type": "application/json"}
        payload = {"user_input": user_input}
        response = requests.post(url, json=payload, headers=headers, stream=True)

    # Iterate with raw bytes and decode manually
    for chunk in response.iter_content(chunk_size=None):
        if chunk:
            try:
                yield chunk.decode("utf-8")
            except UnicodeDecodeError:
                continue  # Skip undecodable chunks safely

# ================== Streamlit UI Setup ==================
st.set_page_config(page_title="Chat", page_icon="🤖")
st.title("Chat")

if "context_log" not in st.session_state:
    st.session_state.context_log = ["Context sẽ được hiển thị tại đây."]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ========== Optional Image Upload ==========
uploaded_image = st.file_uploader("Tải ảnh lên (nếu cần)", type=["jpg", "jpeg", "png"])
image_path = None
if uploaded_image:
    image_path = "temp_uploaded_image.jpg"
    with open(image_path, "wb") as f:
        f.write(uploaded_image.read())

# ========== Toggle Context ==========
if st.toggle("Toggle Context"):
    st.write(st.session_state.context_log)

# ========== Display Chat History ==========
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# ========== User Input ==========
user_query = st.chat_input("Nhập câu hỏi tại đây...")
if user_query:
    # Append user message
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("Human"):
        st.markdown(user_query)

    # Stream AI response
    final_response = ""
    with st.chat_message("AI"):
        placeholder = st.empty()
        for chunk in get_response(user_query, image_path=image_path):
            final_response += chunk
            final_response = re.sub(r'<think>.*?</think>', '', final_response, flags=re.DOTALL)
            placeholder.markdown(final_response)

    st.session_state.chat_history.append(AIMessage(content=final_response))

# ========== Clean up uploaded image ==========
if image_path and os.path.exists(image_path):
    os.remove(image_path)
