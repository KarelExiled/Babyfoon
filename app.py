from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Endpoint for handling live audio data
@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    try:
        # Check if the audio data is in the request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file uploaded'}), 400
        
        audio_file = request.files['audio']
        
        # Save the file (you can customize the path and filename)
        audio_file.save(f"./received_audio/{audio_file.filename}")
        
        return jsonify({'message': 'Audio received successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return "Audio Receiver is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
