import os
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import ChatbotAssistant
from docx import Document
from PyPDF2 import PdfReader
from transformers import pipeline


app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load chatbot model
assistant = ChatbotAssistant(
    intents_path=os.path.join(os.path.dirname(__file__), 'intents.json'),
)
assistant.parse_intents()
assistant.load_model(
    model_path=os.path.join(os.path.dirname(__file__), 'chatbot_model.pth'),
    dimensions_path=os.path.join(os.path.dirname(__file__), 'dimensions.json'),
)

class ChatRequest(BaseModel):
    message: str

@app.api_route("/chat", methods=["POST", "OPTIONS"])
async def chat_endpoint(request: Request):
    if request.method == "OPTIONS":
        # CORS middleware will handle response
        return

    # If POST, parse the body
    body = await request.json()
    message = body.get("message")
    if not message:
        return {"reply": "No message received."}

    reply = assistant.process_message(message)
    return { "reply": reply }

# Preload a summarizer (uses pretrained model, no training needed)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text_from_file(file: UploadFile) -> str:
    ext = file.filename.split(".")[-1].lower()

    if ext == "txt":
        return file.file.read().decode("utf-8")

    elif ext == "pdf":
        reader = PdfReader(file.file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

    elif ext == "docx":
        contents = file.file.read()
        with open("temp.docx", "wb") as f:
            f.write(contents)
        doc = Document("temp.docx")
        os.remove("temp.docx")
        return "\n".join([p.text for p in doc.paragraphs])

    return "Unsupported file format."

@app.post("/upload-essay")
async def analyze_essay(file: UploadFile = File(...)):
    try:
        text = extract_text_from_file(file)

        if len(text.strip()) == 0:
            return {"error": "Document is empty."}

        summary = summarizer(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']

        return {
            "filename": file.filename,
            "summary": summary,
            "char_count": len(text),
            "message": "Essay successfully analyzed."
        }
    except Exception as e:
        return {"error": str(e)} #error message

#uvicorn main:app --reload --host 0.0.0.0 --port 8000
