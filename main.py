import streamlit as st
import os
from utils import extract_text_from_pdf, extract_text_from_image
from qa_engine import chat_with_document  # ensure this exists and returns a string (or has .text)

# -------- CSS (UI + thinking animation) --------
st.markdown(
    """
    <style>
    /* Overall app background */
    .main { background-color: #f9f9f9; }

    /* Chat container */
    .chat-container {
        padding: 12px;
        border-radius: 12px;
        background-color: #ffffff;
        max-height: 520px;
        overflow-y: auto;
    }

    /* User bubble */
    .user-bubble {
        background-color: #dcf8c6;
        color: #000;
        padding: 10px 14px;
        border-radius: 16px;
        margin: 6px 0;
        max-width: 75%;
        text-align: right;
        word-wrap: break-word;
    }

    /* Assistant bubble */
    .ai-bubble {
        background-color: #f1f0f0;
        color: #000;
        padding: 10px 14px;
        border-radius: 16px;
        margin: 6px 0;
        max-width: 75%;
        text-align: left;
        word-wrap: break-word;
    }

    .bubble-row { display: flex; }
    .bubble-row.user { justify-content: flex-end; }
    .bubble-row.ai { justify-content: flex-start; }

    /* Thinking animation */
    .thinking {
        font-size: 14px;
        color: #666;
        font-style: italic;
        margin-top: 8px;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    .dots span {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #666;
        opacity: 0.25;
        transform: translateY(0);
        animation: blink 1s infinite ease-in-out;
    }
    .dots span:nth-child(1){ animation-delay: 0s; }
    .dots span:nth-child(2){ animation-delay: 0.15s; }
    .dots span:nth-child(3){ animation-delay: 0.3s; }

    @keyframes blink {
        0% { opacity: 0.25; transform: translateY(0); }
        50% { opacity: 1; transform: translateY(-4px); }
        100% { opacity: 0.25; transform: translateY(0); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------- Setup --------
UPLOAD_FOLDER = "data/uploaded_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.title("Welcome to Ask My Doc")

# -------- Session state init --------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}  # filename -> [("user", msg), ("assistant", msg)]

if "files" not in st.session_state:
    st.session_state.files = {}  # filename -> extracted text

if "current_file" not in st.session_state:
    st.session_state.current_file = None

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# -------- File uploader (dynamic key to allow resets) --------
uploaded_file = st.file_uploader(
    "Upload a PDF or Image",
    type=["pdf", "png", "jpg", "jpeg"],
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_file:
    # Save file to disk
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ Uploaded: {uploaded_file.name}")

    # Extract text
    if uploaded_file.name.lower().endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)
    else:
        extracted_text = extract_text_from_image(file_path)

    # Store & ensure chat history exists
    st.session_state.files[uploaded_file.name] = extracted_text
    st.session_state.chat_history.setdefault(uploaded_file.name, [])
    st.session_state.current_file = uploaded_file.name

# -------- Sidebar file selector (stable) --------
st.sidebar.subheader("📂 Uploaded Files")
file_list = list(st.session_state.files.keys())
if file_list:
    default_index = 0
    if st.session_state.current_file in file_list:
        default_index = file_list.index(st.session_state.current_file)
    selected = st.sidebar.radio(
        "Open file",
        options=file_list,
        index=default_index,
        key="sidebar_file_radio"
    )
    st.session_state.current_file = selected
else:
    st.sidebar.info("No uploaded files yet.")

# -------- Main UI when a file is selected --------
if st.session_state.current_file:
    current_file = st.session_state.current_file
    st.markdown(f"### 📄 Chat with: `{current_file}`")

    # Collapsible extracted text preview
    with st.expander("📜 View Extracted Text", expanded=False):
        st.text_area(
            "Extracted Text",
            value=st.session_state.files.get(current_file, ""),
            height=220,
            label_visibility="collapsed"
        )

    st.divider()

    # Buttons row (unique keys per file)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    # Clear chat
    with col1:
        if st.button("🧹 Clear Chat", key=f"clear_{current_file}", use_container_width=True):
            st.session_state.chat_history[current_file] = []
            st.success("Chat cleared.")
            st.rerun()

    # Remove file
    with col2:
        if st.button("❌ Remove File", key=f"remove_{current_file}", use_container_width=True):
            # delete physical file if present
            file_path = os.path.join(UPLOAD_FOLDER, current_file)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                st.warning(f"Couldn't delete the file from disk: {e}")

            # remove from session state
            st.session_state.files.pop(current_file, None)
            st.session_state.chat_history.pop(current_file, None)

            # if any remaining files, select the first; otherwise reset and bump uploader key
            remaining = list(st.session_state.files.keys())
            if remaining:
                st.session_state.current_file = remaining[0]
            else:
                st.session_state.current_file = None
                st.session_state.uploader_key += 1  # force new uploader instance on next render

            st.success(f"Removed `{current_file}`.")
            st.rerun()

    # Download extracted text
    with col3:
        st.download_button(
            "⬇️ Download Text",
            data=st.session_state.files.get(current_file, ""),
            file_name=f"{current_file}_extracted.txt",
            mime="text/plain",
            key=f"download_text_{current_file}",
            use_container_width=True
        )

    # Download chat history
    with col4:
        chat_export = "\n".join(
            [f"You: {m}" if r == "user" else f"AI: {m}" for r, m in st.session_state.chat_history.get(current_file, [])]
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

    # Chat area (HTML bubbles)
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for role, msg in st.session_state.chat_history.get(current_file, []):
            safe_msg = str(msg).replace("\n", "<br>")
            if role == "user":
                st.markdown(f'<div class="bubble-row user"><div class="user-bubble">{safe_msg}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bubble-row ai"><div class="ai-bubble">{safe_msg}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Add File button (secondary uploader)
    with st.expander("➕ Add Another File", expanded=False):
        new_file = st.file_uploader(
            "Upload another PDF or Image",
            type=["pdf", "png", "jpg", "jpeg"],
            key="new_file_uploader"
        )

        if new_file:
            # Save file
            new_path = os.path.join(UPLOAD_FOLDER, new_file.name)
            with open(new_path, "wb") as f:
                f.write(new_file.getbuffer())

            st.success(f"✅ Added: {new_file.name}")

            # Extract text
            if new_file.name.lower().endswith(".pdf"):
                new_text = extract_text_from_pdf(new_path)
            else:
                new_text = extract_text_from_image(new_path)

            # Store in session_state
            st.session_state.files[new_file.name] = new_text
            st.session_state.current_file = new_file.name

            if new_file.name not in st.session_state.chat_history:
                st.session_state.chat_history[new_file.name] = []

            st.rerun()


    # Thinking placeholder (will show animated dots via client-side CSS)
    thinking_placeholder = st.empty()

    # Input box
    user_question = st.chat_input("💬 Ask a question...")

    if user_question:
        try:
            # append user message immediately
            st.session_state.chat_history.setdefault(current_file, []).append(("user", user_question))

            # show client-side animated thinking indicator (CSS-driven)
            thinking_html = """
            <div class="thinking">
                <div>🤔 Thinking</div>
                <div class="dots"><span></span><span></span><span></span></div>
            </div>
            """
            thinking_placeholder.markdown(thinking_html, unsafe_allow_html=True)

            # blocking call to your QA engine (this can take time)
            doc_text = st.session_state.files.get(current_file, "")
            answer = chat_with_document(doc_text, user_question)

            # if answer is an object with .text, use it
            if hasattr(answer, "text"):
                answer_text = answer.text
            elif isinstance(answer, dict) and "text" in answer:
                answer_text = answer["text"]
            else:
                answer_text = str(answer)

            # clear thinking placeholder and append assistant reply
            thinking_placeholder.empty()
            st.session_state.chat_history.setdefault(current_file, []).append(("assistant", answer_text))

            # refresh to show assistant message
            st.rerun()

        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Error while getting response: {e}")

# If no file selected
else:
    st.info("📂 Upload a file or select one from the sidebar to start chatting.")
