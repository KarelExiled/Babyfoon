import os
from flask import Flask, render_template, request, jsonify
import librosa
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pydub import AudioSegment
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Path for uploading audio files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dummy classifier (for the example, we simulate this with a basic model)
sound_labels = ['crying', 'ambient', 'laughter', 'noise']
label_encoder = LabelEncoder()
label_encoder.fit(sound_labels)


# Fake sound classification function (can be replaced with actual sound classifier)
def classify_sound(audio_file):
    # Load the audio file
    y, sr = librosa.load(audio_file, sr=None)

    # Extract features like MFCC for classification (simplified)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    feature = np.mean(mfcc, axis=1)

    # Simple classification based on the average MFCC feature (for demo purposes)
    sound_type = np.random.choice(sound_labels)
    return sound_type


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['audio']

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    # Save the file
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Sound_{timestamp}.wav"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Classify the sound
    sound_type = classify_sound(filepath)

    # Example: Return data about the sound (time, type)
    analysis_data = {
        "timestamp": timestamp,
        "sound_type": sound_type,
        "filename": filename
    }

    return jsonify(analysis_data)


@app.route('/generate_plot', methods=['GET'])
def generate_plot():
    # Fake nightly overview for demo
    times = ['10:00', '12:00', '02:00', '04:00']
    sounds = ['ambient', 'crying', 'laughter', 'ambient']

    # Generate a simple bar plot for sounds
    plt.figure(figsize=(10, 5))
    sns.countplot(x=sounds)
    plt.title('Sound Occurrence')
    plt.xlabel('Sound Type')
    plt.ylabel('Frequency')

    # Save plot
    plot_filename = 'nightly_overview.png'
    plot_filepath = os.path.join(app.config['UPLOAD_FOLDER'], plot_filename)
    plt.savefig(plot_filepath)
    plt.close()

    return jsonify({"plot": plot_filename})


if __name__ == '__main__':
    app.run(debug=True)
