from flask import Flask, request, jsonify, render_template
import librosa
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper functions
def analyze_audio(file_path):
    """
    Analyze the audio file to extract key features like duration,
    average amplitude, and classification (e.g., baby crying).
    """
    y, sr = librosa.load(file_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    amplitude = np.mean(np.abs(y))

    # Simulate classification (e.g., baby crying vs. other sounds)
    if amplitude > 0.05:
        classification = 'Crying'
    else:
        classification = 'Ambient Noise'

    return {
        'duration': duration,
        'amplitude': amplitude,
        'classification': classification,
    }

def create_nightly_overview(data):
    """
    Generate a plot showing when the baby made sounds during the night.
    """
    timestamps = [d['timestamp'] for d in data]
    classifications = [1 if d['classification'] == 'Crying' else 0 for d in data]

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, classifications, marker='o', linestyle='-', label='Crying')
    plt.title('Nightly Sleep Pattern')
    plt.xlabel('Time')
    plt.ylabel('Sound Classification')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plot_path = os.path.join(UPLOAD_FOLDER, 'nightly_overview.png')
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

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        analysis_result = analyze_audio(file_path)
        analysis_result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Save analysis result to a database or a list (for simplicity, using a list here)
        if not hasattr(app, 'analysis_results'):
            app.analysis_results = []
        app.analysis_results.append(analysis_result)

        # Generate nightly overview plot
        plot_path = create_nightly_overview(app.analysis_results)

        return jsonify({
            'analysis': analysis_result,
            'nightly_overview_plot': plot_path,
        })

@app.route('/dashboard')
def dashboard():
    """
    Render the dashboard with analysis data.
    """
    results = getattr(app, 'analysis_results', [])
    return render_template('dashboard.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
