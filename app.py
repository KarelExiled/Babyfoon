import os
import librosa
import numpy as np
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav'}
processed_files = {}
sleep_schedule = {}

# Default bedtime and wake-up time
DEFAULT_BEDTIME = "19:00"
DEFAULT_WAKEUP = "08:00"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def classify_sound(file_path):
    """Classify sound as baby cry or other noise, and measure volume."""
    y, sr = librosa.load(file_path)
    duration = librosa.get_duration(y=y, sr=sr)

    # Compute mean volume
    rms = librosa.feature.rms(y=y)
    volume = np.mean(rms) * 100  # Scale volume for readability

    # MFCC classification for sound type
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    mfcc_mean = np.mean(mfcc)

    sound_type = "Baby Cry" if mfcc_mean > 0 else "Other Noise"
    return sound_type, duration, round(volume, 1)

def extract_timestamp_from_filename(filename):
    """Extract the timestamp from the filename."""
    try:
        parts = filename.split('_')
        timestamp_str = '_'.join(parts[1:]).replace('.wav', '')
        return datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return "Unknown"

def process_existing_files():
    """Process all files in the /uploads directory."""
    for filename in os.listdir(UPLOAD_FOLDER):
        if allowed_file(filename) and filename not in processed_files:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            timestamp = extract_timestamp_from_filename(filename)
            sound_type, duration, volume = classify_sound(file_path)

            processed_files[filename] = {
                'timestamp': timestamp,
                'sound_type': sound_type,
                'duration': round(duration, 0),
                'volume': volume
            }

def calculate_sleep_duration(bedtime, wake_time, events):
    """Calculate the total sleep duration excluding noise events."""
    total_sleep = (datetime.combine(datetime.today(), wake_time) -
                   datetime.combine(datetime.today(), bedtime)).seconds / 3600

    noise_duration = sum(event["duration"] for event in events if event["sound_type"] == "Baby Cry")
    settling_time = len([event for event in events if event["sound_type"] == "Baby Cry"]) * 10 * 60
    total_interruption = (noise_duration + settling_time) / 3600

    return max(total_sleep - total_interruption, 0)

@app.route('/')
def index():
    today = datetime.today().strftime("%Y-%m-%d")
    last_night_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    return render_template('index.html', default_bedtime=DEFAULT_BEDTIME, default_wakeup=DEFAULT_WAKEUP,
                           last_night_date=last_night_date, today_date=today)

@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    data = request.json
    date = data['date']
    bedtime = data['bedtime']
    wake_time = data['wake_time']
    sleep_schedule[date] = {'bedtime': bedtime, 'wake_time': wake_time}
    return jsonify({'status': 'success', 'message': 'Schedule updated'})

@app.route('/night_overview/<date>', methods=['GET'])
def night_overview(date):
    bedtime = sleep_schedule.get(date, {}).get('bedtime', DEFAULT_BEDTIME)
    wake_time = sleep_schedule.get(date, {}).get('wake_time', DEFAULT_WAKEUP)

    bedtime = datetime.strptime(bedtime, "%H:%M").time()
    wake_time = datetime.strptime(wake_time, "%H:%M").time()

    events = [
        {
            "timestamp": info["timestamp"],
            "sound_type": info["sound_type"],
            "duration": info["duration"],
            "volume": info["volume"]
        }
        for filename, info in processed_files.items()
        if date in info["timestamp"]
    ]

    total_sleep = calculate_sleep_duration(bedtime, wake_time, events)
    return jsonify({
        "date": date,
        "bedtime": bedtime.strftime("%H:%M"),
        "wake_time": wake_time.strftime("%H:%M"),
        "total_sleep": round(total_sleep, 2),
        "events": events
    })

@app.route('/week_overview', methods=['GET'])
def week_overview():
    week_data = []
    today = datetime.today()
    for i in range(7):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        overview = night_overview(date).json
        week_data.append(overview)
    return jsonify(week_data)

if __name__ == '__main__':
    process_existing_files()
    app.run(debug=True)
