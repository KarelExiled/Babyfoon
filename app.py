import os
from flask import Flask, render_template, request, jsonify
import librosa
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
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

# Data to simulate night sounds and sleep patterns
night_sounds = [
    {"timestamp": "2025-01-13_22:15", "sound_type": "ambient"},
    {"timestamp": "2025-01-13_23:02", "sound_type": "crying"},
    {"timestamp": "2025-01-14_01:17", "sound_type": "laughter"},
    {"timestamp": "2025-01-14_05:30", "sound_type": "ambient"},
    {"timestamp": "2025-01-15_00:40", "sound_type": "crying"},
    {"timestamp": "2025-01-16_03:25", "sound_type": "ambient"},
    {"timestamp": "2025-01-16_04:03", "sound_type": "crying"},
    {"timestamp": "2025-01-17_21:58", "sound_type": "ambient"},
    {"timestamp": "2025-01-18_03:15", "sound_type": "crying"},
    {"timestamp": "2025-01-18_22:45", "sound_type": "laughter"},
]


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
    return render_template('index.html', sounds=night_sounds)


@app.route('/generate_plot', methods=['GET'])
def generate_plot():
    # Extract sound types and counts for the plot
    sounds = [entry['sound_type'] for entry in night_sounds]

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
