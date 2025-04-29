import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import ChatbotAssistant

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

#uvicorn main:app --reload --host 0.0.0.0 --port 8000
