import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import ChatbotAssistant
from docx import Document
from PyPDF2 import PdfReader
from transformers import pipeline
from essay_analysis import read_essay, summarize_essay, extract_keywords

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})  # Flask equivalent of add_middleware

# Load chatbot model
assistant = ChatbotAssistant(
    intents_path=os.path.join(os.path.dirname(__file__), 'intents.json'),
)
assistant.parse_intents()
assistant.load_model(
    model_path=os.path.join(os.path.dirname(__file__), 'chatbot_model.pth'),
    dimensions_path=os.path.join(os.path.dirname(__file__), 'dimensions.json'),
)

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"reply": "No message received."}), 400

    reply = assistant.process_message(message)
    return jsonify({"reply": reply})

# Essay summarizer pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.route('/upload-essay', methods=['POST'])
def upload_essay():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    essay_text = read_essay(file)
    summary = summarize_essay(essay_text)
    suggested_courses = extract_keywords(summary)

    if suggested_courses:
        response_text = (
            f"Based on your essay, you seem interested in areas like technology or AI. "
            f"You might consider the following programs: {', '.join(suggested_courses)}."
        )
    else:
        response_text = (
            "Thank you for your essay. Please make sure to specify your interests more clearly "
            "for tailored course suggestions."
        )

    return jsonify({
        "summary": summary,
        "suggested_courses": suggested_courses,
        "response": response_text
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
