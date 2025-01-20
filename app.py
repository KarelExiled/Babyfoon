from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import os
import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import glob

app = Flask(__name__)

# Directory for uploaded sound files
UPLOAD_DIR = 'uploads'
PLOT_FOLDER = 'static/plots'

# Ensure the plot directory exists
if not os.path.exists(PLOT_FOLDER):
    os.makedirs(PLOT_FOLDER)

# Simulate sound classification (a real-world solution would use ML models)
def classify_sound(filename):
    # In a real implementation, you would analyze the sound file here
    # We will randomly classify it for this example
    if 'cry' in filename.lower():
        return 'Cry'
    return 'Other Noise'

# Route for index page
@app.route('/')
def index():
    return render_template('index.html')

# Route to set sleep schedule
@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    data = request.get_json()
    date_str = data['date']
    bedtime_str = data['bedtime']
    wake_time_str = data['wake_time']

    # Convert string times to datetime objects
    date = datetime.strptime(date_str, "%Y-%m-%d")
    bedtime = datetime.strptime(bedtime_str, "%H:%M")
    wake_time = datetime.strptime(wake_time_str, "%H:%M")

    if wake_time < bedtime:
        wake_time += timedelta(days=1)

    bedtime = date.replace(hour=bedtime.hour, minute=bedtime.minute, second=0, microsecond=0)
    wake_time = date.replace(hour=wake_time.hour, minute=wake_time.minute, second=0, microsecond=0)

    sleep_duration = wake_time - bedtime
    response = {
        'date': date_str,
        'bedtime': bedtime.strftime("%H:%M"),
        'wake_time': wake_time.strftime("%H:%M"),
        'sleep_duration': str(sleep_duration)
    }

    return jsonify(response)

# Route for fetching night overview
@app.route('/night_overview/<date>', methods=['GET'])
def night_overview(date):
    bedtime = '22:00'
    wake_time = '06:00'
    bedtime = datetime.strptime(bedtime, "%H:%M")
    wake_time = datetime.strptime(wake_time, "%H:%M")
    if wake_time < bedtime:
        wake_time += timedelta(days=1)
    sleep_duration = wake_time - bedtime
    hours = sleep_duration.total_seconds() // 3600
    minutes = (sleep_duration.total_seconds() % 3600) // 60
    return jsonify({
        'date': date,
        'bedtime': bedtime.strftime("%H:%M"),
        'wake_time': wake_time.strftime("%H:%M"),
        'sleep_duration': f"{int(hours)} hours and {int(minutes)} minutes"
    })

# Route for fetching sound events
@app.route('/sound_events/<date>', methods=['GET'])
def sound_events(date):
    sound_files = glob.glob(f"{UPLOAD_DIR}/Sound*_{date}*.wav")  # Match files by date
    events = []
    num_events = 0
    num_crying = 0

    for sound_file in sound_files:
        # Extract the timestamp from the filename
        timestamp = sound_file.split('_')[1]  # Extract timestamp from filename
        event_type = classify_sound(sound_file)

        events.append({
            'time': timestamp,
            'type': event_type
        })

        num_events += 1
        if event_type == 'Cry':
            num_crying += 1

    return jsonify({
        'date': date,
        'num_events': num_events,
        'num_crying_events': num_crying,
        'sound_events': events
    })

# Route for night plot (visualization)
@app.route('/plot/last_night/<date>', methods=['GET'])
def night_plot(date):
    plot_image_filename = f"{date.replace('-', '')}_timeline.png"
    plot_image_path = os.path.join(PLOT_FOLDER, plot_image_filename)

    if not os.path.exists(plot_image_path):
        generate_sleep_plot(date)

    return jsonify({"url": f"/static/plots/{plot_image_filename}"})


def generate_sleep_plot(date):
    bedtime_str = '22:00'
    wake_time_str = '06:00'
    bedtime = datetime.strptime(bedtime_str, "%H:%M")
    wake_time = datetime.strptime(wake_time_str, "%H:%M")
    if wake_time < bedtime:
        wake_time += timedelta(days=1)

    fig, ax = plt.subplots(figsize=(10, 2))
    ax.set_title(f"Sleep Timeline for {date}")

    ax.plot([bedtime, wake_time], [1, 1], color='b', lw=6)

    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_ylim(0.5, 1.5)
    ax.set_xlim(bedtime - timedelta(hours=1), wake_time + timedelta(hours=1))
    ax.set_yticks([])

    plot_image_filename = f"{date.replace('-', '')}_timeline.png"
    plot_image_path = os.path.join(PLOT_FOLDER, plot_image_filename)
    plt.savefig(plot_image_path, bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    app.run(debug=True)
