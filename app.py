from flask import Flask, render_template, request, jsonify
import os
import librosa
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = f"Sound{len(os.listdir(UPLOAD_FOLDER)) + 1}_{file.filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the file (dummy classification logic for now)
        sound_type = classify_sound(file_path)

        # Return the sound type and timestamp
        return jsonify({'sound_type': sound_type, 'timestamp': filename.split('_')[1]})
    else:
        return jsonify({'error': 'Invalid file type'}), 400


def classify_sound(file_path):
    # Example using librosa for basic sound classification
    y, sr = librosa.load(file_path)
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    mfcc_mean = np.mean(mfcc)

    # Dummy logic for classification based on MFCC mean
    if mfcc_mean > 0:
        return "Baby Cry"
    else:
        return "Other Noise"


@app.route('/generate_plot', methods=['GET'])
def generate_plot():
    # Example: Generate a plot of the baby's sleep patterns (dummy data for now)
    plot_filename = "plot.png"
    plot_path = os.path.join('static', plot_filename)

    # Plot generation code (e.g., using matplotlib)
    plt.plot([1, 2, 3, 4, 5], [10, 20, 25, 30, 40])
    plt.title("Nightly Overview")
    plt.xlabel("Time")
    plt.ylabel("Sleep Events")
    plt.savefig(plot_path)

    return jsonify({'plot': plot_filename})


if __name__ == '__main__':
    app.run(debug=True)
