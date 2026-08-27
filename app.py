from flask import Flask, render_template, request, jsonify, redirect, url_for
import speech_recognition as sr
import google.generativeai as genai
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from a2wsgi import WSGIMiddleware
import traceback
import os
from dotenv import load_dotenv
from database import create_task, delete_task, initialize_database, list_tasks, update_task_status
from schemas import TaskCreate, TaskResponse
from services.prioritization_engine import prioritize_task

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

GEMINI_MODEL = "gemini-3.6-flash"
app = Flask(__name__)
initialize_database()


def generate_chat_reply(user_input):
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured on the server.")

    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(user_input)
    return response.text


@app.route('/')
def home():
    return render_template('login.html')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return redirect(url_for('index'))


@app.route('/c')
def goToChat():
    return render_template('c.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Simple hardcoded login check (demo only)
    if username == 'admin' and password == 'admin':
        return redirect(url_for('index'))
    else:
        error = "Invalid username or password"
        return render_template('login.html', error=error)


@app.route('/api/models', methods=['GET'])
def list_models():
    return jsonify({
        "provider": "google-gemini",
        "configured": bool(GEMINI_API_KEY),
        "model": GEMINI_MODEL
    })


@app.route('/api/chat', methods=['POST'])
def chat_with_bot():
    try:
        data = request.get_json()
        user_input = (data or {}).get("message", "").strip()
        print("🟢 User input received:", user_input)

        if not user_input:
            return jsonify({"error": "Empty message"}), 400

        reply = generate_chat_reply(user_input)

        print("✅ Gemini response:", reply)
        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Gemini error:", str(e))
        traceback.print_exc()
        return jsonify({"error": "Gemini error: " + str(e)}), 500


@app.route('/api/voice-task', methods=['POST'])
def process_voice_task():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        return jsonify({"task": text})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400

# FastAPI handles JSON endpoints while Flask continues serving the existing UI.
fastapi_app = FastAPI(title="MindFlow API")


class ChatRequest(BaseModel):
    message: str


@fastapi_app.get("/health")
def health_check():
    return {"status": "ok", "provider": "google-gemini", "configured": bool(GEMINI_API_KEY)}


@fastapi_app.post("/chat")
def fastapi_chat(request: ChatRequest):
    user_input = request.message.strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        return {"reply": generate_chat_reply(user_input)}
    except Exception as error:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"Gemini error: {error}") from error


def firebase_token(authorization):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Firebase authentication is required.")
    return authorization.split(" ", 1)[1]


@fastapi_app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task_endpoint(task: TaskCreate, authorization: str | None = Header(default=None)):
    try:
        id_token = firebase_token(authorization)
        prediction = prioritize_task(task)
        return create_task(task, prediction, id_token)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not create task.") from error


@fastapi_app.get("/tasks", response_model=list[TaskResponse])
def list_task_endpoint(user_id: str, authorization: str | None = Header(default=None)):
    if not user_id.strip():
        raise HTTPException(status_code=400, detail="user_id cannot be empty.")
    return list_tasks(user_id, firebase_token(authorization))


@fastapi_app.delete("/tasks/{task_id}", status_code=204)
def delete_task_endpoint(task_id: str, user_id: str, authorization: str | None = Header(default=None)):
    if not delete_task(task_id, user_id, firebase_token(authorization)):
        raise HTTPException(status_code=404, detail="Task not found.")


@fastapi_app.patch("/tasks/{task_id}/status", response_model=TaskResponse)
def update_task_status_endpoint(task_id: str, user_id: str, status: str, authorization: str | None = Header(default=None)):
    if status not in {"Pending", "In Progress", "Completed"}:
        raise HTTPException(status_code=422, detail="Invalid task status.")
    id_token = firebase_token(authorization)
    if not update_task_status(task_id, user_id, status, id_token):
        raise HTTPException(status_code=404, detail="Task not found.")
    task = next((item for item in list_tasks(user_id, id_token) if item["id"] == task_id), None)
    return task


# Uvicorn serves FastAPI and delegates all existing Flask routes to the WSGI app.
asgi_app = fastapi_app
asgi_app.mount("/", WSGIMiddleware(app))



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render sets the PORT env var
    import uvicorn
    uvicorn.run(asgi_app, host='0.0.0.0', port=port)
