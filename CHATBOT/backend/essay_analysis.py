from transformers import pipeline
import PyPDF2
import docx

# Simple course mapping
COURSE_SUGGESTIONS = {
    "computer science": ["BSc in Computer Science", "BSc in IT", "BSc in Software Engineering"],
    "machine learning": ["BSc in AI", "BSc in Data Science"],
    "web development": ["BSc in Web Technologies"],
    "cybersecurity": ["Diploma in Cybersecurity", "BSc in Network Engineering"],
    "robotics": ["BSc in Mechatronics", "BSc in Robotics"],
}

summarizer = pipeline("summarization")

def summarize_essay(text):
    # Basic summarization using Hugging Face model
    result = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return result[0]['summary_text']

def extract_course_recommendations(summary):
    summary = summary.lower()
    courses = []
    for keyword, suggestions in COURSE_SUGGESTIONS.items():
        if keyword in summary:
            courses.extend(suggestions)
    return list(set(courses))  # Avoid duplicates

def extract_keywords(summary):
    summary = summary.lower()
    found_topics = []
    for topic in COURSE_SUGGESTIONS:
        if topic in summary:
            found_topics.extend(COURSE_SUGGESTIONS[topic])
    return found_topics



def read_essay(file):
    filename = file.filename.lower()

    if filename.endswith('.txt'):
        return file.read().decode('utf-8')

    elif filename.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text

    elif filename.endswith('.docx'):
        doc = docx.Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])

    else:
        return "Unsupported file format."