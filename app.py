from flask import Flask, render_template, request, jsonify
import os
import librosa  # For audio file processing
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)

# Set up file upload folder
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav', 'flac'}

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Function to generate a plot from the audio data
def generate_nightly_plot(file_path):
    # Load the audio file
    y, sr = librosa.load(file_path)

    # Generate a simple waveform plot
    plt.figure(figsize=(10, 4))
    plt.plot(np.linspace(0, len(y) / sr, num=len(y)), y)
    plt.title("Nightly Sleep Pattern")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")

    # Save the plot as an image
    plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'nightly_plot.png')
    plt.savefig(plot_path)
    plt.close()

    return plot_path


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Process the audio file (just an example)
        y, sr = librosa.load(filename)
        duration = librosa.get_duration(y=y, sr=sr)
        amplitude = np.max(np.abs(y))
        classification = "Normal"  # Example classification (can be modified)

        # Generate plot for nightly overview
        plot_path = generate_nightly_plot(filename)

        # Return analysis as JSON
        return jsonify({
            'analysis': {
                'duration': duration,
                'amplitude': amplitude,
                'classification': classification
            },
            'nightly_overview_plot': plot_path
        })

    return jsonify({'error': 'File not allowed'}), 400


if __name__ == '__main__':
    app.run(debug=True)
