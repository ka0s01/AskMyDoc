import streamlit as st
import os
from utils import extract_text_from_pdf, extract_text_from_image

# Ensure upload folder exists
UPLOAD_FOLDER = "data/uploaded_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.title("📄 Document QA App - Step 1: Upload & View")
# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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

    # Show extracted text
    st.subheader("📜 Extracted Text")
    st.text_area("Raw Text", value=extracted_text, height=300)

    # Save extracted text for Q&A
    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(extracted_text)

    st.markdown("---")

# Q&A section (independent of upload)
# Chat-style QA
st.subheader("💬 Chat with your document")

user_question = st.text_input("Ask a question", key="chat_input")

if st.button("Send") and user_question:
    from qa_engine import chat_with_document

    try:
        with open("extracted_text.txt", "r", encoding="utf-8") as f:
            doc_text = f.read()

        answer = chat_with_document(doc_text, user_question)

        # Save to session state chat history
        st.session_state.chat_history.append(("user", user_question))
        st.session_state.chat_history.append(("ai", answer))

    except FileNotFoundError:
        st.error("❌ Please upload a document first.")

# Show chat history
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Gemini:** {msg}")

