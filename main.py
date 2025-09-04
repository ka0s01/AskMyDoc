import streamlit as st
import os
import time
from utils import extract_text_from_pdf, extract_text_from_image

st.markdown(
    """
    <style>
    /* Overall app background */
    .main {
        background-color: #f9f9f9;
    }

    /* Chat container */
    .chat-container {
        padding: 10px;
        border-radius: 12px;
        background-color: #ffffff;
        max-height: 500px;
        overflow-y: auto;
    }

    /* User bubble */
    .user-bubble {
        background-color: #dcf8c6;
        color: #000;
        padding: 10px 15px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 75%;
        align-self: flex-end;
        text-align: right;
    }

    /* Assistant bubble */
    .ai-bubble {
        background-color: #f1f0f0;
        color: #000;
        padding: 10px 15px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 75%;
        align-self: flex-start;
        text-align: left;
    }

    /* Chat alignment */
    .bubble-row {
        display: flex;
    }
    .bubble-row.user {
        justify-content: flex-end;
    }
    .bubble-row.ai {
        justify-content: flex-start;
    }

    /* Thinking loader */
    .thinking {
        font-size: 14px;
        color: #999;
        font-style: italic;
        margin-top: 5px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)


UPLOAD_FOLDER = "data/uploaded_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.title("Welcome to Ask My Doc")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}  # {filename: [("user", msg), ("assistant", msg)]}

if "files" not in st.session_state:
    st.session_state.files = {}  # {filename: extracted_text}

if "current_file" not in st.session_state:
    st.session_state.current_file = None

# File uploader
uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ Uploaded: {uploaded_file.name}")

    # Extract text
    if uploaded_file.name.lower().endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)
    else:
        extracted_text = extract_text_from_image(file_path)

    # Store in session_state
    st.session_state.files[uploaded_file.name] = extracted_text
    st.session_state.current_file = uploaded_file.name

    if uploaded_file.name not in st.session_state.chat_history:
        st.session_state.chat_history[uploaded_file.name] = []  # New chat for this file

# Sidebar to switch between uploaded files
st.sidebar.subheader("📂 Uploaded Files")
for fname in st.session_state.files.keys():
    if st.sidebar.button(f"Open {fname}"):
        st.session_state.current_file = fname

# Show active file
if st.session_state.current_file:
    current_file = st.session_state.current_file
    st.markdown(f"### 📄 Chat with: `{current_file}`")

    # Collapsible extracted text preview
    with st.expander("📜 View Extracted Text", expanded=False):
        st.text_area(
            "Extracted Text",
            st.session_state.files[current_file],
            height=250,
            label_visibility="collapsed"
        )

    st.divider()

    # Button row (all 4 in one line)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.chat_history[current_file] = []
            st.rerun()
    with col2:
        if st.button("❌ Remove", use_container_width=True):
            try:
                file_path = os.path.join(UPLOAD_FOLDER, current_file)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                st.warning(f"Couldn't delete the file from disk: {e}")
            st.session_state.files.pop(current_file, None)
            st.session_state.chat_history.pop(current_file, None)
            st.session_state.current_file = next(iter(st.session_state.files), None)
            st.rerun()
    with col3:
        st.download_button(
            "⬇️ Download Text",
            data=st.session_state.files[current_file],
            file_name=f"{current_file}_extracted.txt",
            mime="text/plain",
            key=f"download_text_{current_file}",
            use_container_width=True
        )
    with col4:
        chat_export = "\n".join(
            [f"You: {msg}" if role == "user" else f"AI: {msg}"
             for role, msg in st.session_state.chat_history[current_file]]
        )
        st.download_button(
            "⬇️ Download Chat",
            data=chat_export,
            file_name=f"{current_file}_chat.txt",
            mime="text/plain",
            key=f"download_chat_{current_file}",
            use_container_width=True
        )

    st.divider()

    # Chat area
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for role, msg in st.session_state.chat_history[current_file]:
            if role == "user":
                st.markdown(f'<div class="bubble-row user"><div class="user-bubble">{msg}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bubble-row ai"><div class="ai-bubble">{msg}</div></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Placeholder for "Thinking..." message
    thinking_placeholder = st.empty()

    # Input box stays pinned at bottom
    user_question = st.chat_input("💬 Ask a question...")

    if user_question:
        from qa_engine import chat_with_document

        try:
            doc_text = st.session_state.files[current_file]
            st.session_state.chat_history[current_file].append(("user", user_question))

            # Show a "Thinking..." placeholder
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown(
                "<div class='thinking'>🤔 Thinking...</div>", unsafe_allow_html=True
            )

            # Call Gemini / QA engine
            answer = chat_with_document(doc_text, user_question)

            # Replace placeholder with nothing (clear it)
            thinking_placeholder.empty()

            # Save AI response
            st.session_state.chat_history[current_file].append(("assistant", answer))

            st.rerun()
        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"❌ Error: {e}")

