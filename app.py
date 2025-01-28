from flask import Flask, request, jsonify, render_template, send_from_directory
import os

app = Flask(__name__)

# Folder to save uploaded audio
UPLOAD_FOLDER = './static/audio'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    # List all audio files in the folder
    audio_files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', audio_files=audio_files)

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    try:
        # Save the binary audio data
        audio_data = request.data
        if not audio_data:
            return jsonify({'error': 'No audio data received'}), 400

        # Save audio file with a unique name
        filename = f"audio_{len(os.listdir(UPLOAD_FOLDER))}.wav"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, 'wb') as f:
            f.write(audio_data)

        return jsonify({'message': 'Audio uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/audio/<filename>')
def get_audio(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
