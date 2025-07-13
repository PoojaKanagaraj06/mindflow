from flask import Flask, render_template, request, jsonify, redirect, url_for
import speech_recognition as sr
import google.generativeai as genai
import traceback

# ✅ Configure Gemini API key
genai.configure(api_key=GOOGLE_API_KEY)
'''
for m in genai.list_models():
    print(m.name, m.supported_generation_methods)'''
app = Flask(__name__)

# ✅ Serve login page
@app.route('/')
def home():
    return render_template('login.html')

# ✅ Serve index page after login
@app.route('/index')
def index():
    return render_template('index.html')

# ✅ Serve chatbot page
@app.route('/c')
def goToChat():
    return render_template('c.html')

# ✅ Handle login form submission
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

# ✅ List available Gemini models
@app.route('/api/models', methods=['GET'])
def list_models():
    try:
        models = genai.list_models()
        model_names = [model.name for model in models]
        return jsonify({"available_models": model_names})
    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ Handle chat with Gemini
@app.route('/api/chat', methods=['POST'])
def chat_with_bot():
    try:
        data = request.get_json()
        user_input = data.get("message", "")
        print("🟢 User input received:", user_input)

        if not user_input:
            return jsonify({"error": "Empty message"}), 400

        # ✅ Correct Gemini model name
        model = genai.GenerativeModel("models/gemini-2.5-flash-lite-preview-06-17") 
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
