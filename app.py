from flask import Flask, render_template, request, jsonify
import speech_recognition as sr

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Flask looks in /templates

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

if __name__ == '__main__':
    app.run(debug=True)
