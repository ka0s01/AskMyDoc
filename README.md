# 📄 Ask My Doc

An interactive **Document Question-Answering (QA) App** built with **Streamlit** and powered by **Gemini AI**.  
Upload a **PDF or Image**, extract its text, and chat with your document in real-time.  

---

## ✨ Features

- 📂 **Upload Documents** (PDFs, PNGs, JPGs, JPEGs)  
- 🔍 **Automatic Text Extraction** from PDFs and Images  
- 💬 **Chat with Your Document** using Gemini AI  
- 🗂 **Multi-file Support** → switch between uploaded files easily  
- 📜 **Collapsible Extracted Text Preview**  
- ⬇️ **Download Options**  
  - Extracted text as `.txt`  
  - Full chat history as `.txt`  
- 🧹 **Clear Chat** (per file)  
- ❌ **Remove Files** (from memory + disk)  
- 🤔 **Thinking Indicator** while the model processes your query  
- 🖌 **Clean Chat UI** with styled bubbles  

---

## 📸Preview


---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) – UI & app framework  
- [Google Gemini API](https://ai.google.dev/) – LLM for Q&A  
- [pdfplumber](https://pypi.org/project/pdfplumber/) – PDF text extraction  
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) + [Pillow](https://pypi.org/project/Pillow/) – Image text extraction  
- Python 3.9+  

---

## 🚀 Installation & Setup

### Clone the repo:
```bash
git clone https://github.com/your-username/ask-my-doc.git
cd ask-my-doc
```
### Create a Virtual Environment
```
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```
### Install The dependancies
```
pip install -r requirements.txt

export GEMINI_API_KEY="your_api_key"    # Mac/Linux
setx GEMINI_API_KEY "your_api_key"      # Windows
```
### Run the app
```
streamlit run main.py


Project Structure
ask-my-doc/
│
├── main.py                 # Streamlit UI
├── qa_engine.py            # Gemini Q&A logic
├── utils.py                # Text extraction helpers
├── data/
│   └── uploaded_docs/      # Uploaded files stored here
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```


## 🧑‍💻 Future Improvements

- 🔄 Streaming responses from Gemini 
- ⏳ True animated "thinking..." loader
- 🗃 Persistent storage of chat histories
- 🌐 Deploy on Streamlit Cloud 
