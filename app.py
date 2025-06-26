from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import google.generativeai as genai
import traceback

# ✅ Configure Gemini API
GOOGLE_API_KEY = "AIzaSyDRcSFJ7zDjxB6QMT-UpnQY-oFlODoP5XA"
genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)

# ✅ Serve homepage
@app.route('/')
def home():
    return render_template('index.html')

# ✅ Serve chatbot page
@app.route('/c')
def goToChat():
    return render_template('c.html')
@app.route('/api/models', methods=['GET'])
def list_models():
    try:
        models = genai.list_models()
        model_names = [model.name for model in models]
        return jsonify({"available_models": model_names})
    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ Handle chat input using Gemini
@app.route('/api/chat', methods=['POST'])
def chat_with_bot():
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    try:
        # ✅ Use Gemini Pro directly
        model = genai.GenerativeModel("")
        response = model.generate_content(user_input)

        print("✅ Gemini response:", response.text)
        return jsonify({"reply": response.text})

    except Exception as e:
        print("❌ Gemini error:", str(e))
        traceback.print_exc()
        return jsonify({"error": "Gemini error: " + str(e)}), 500

# ✅ Handle voice input
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

# ✅ Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
