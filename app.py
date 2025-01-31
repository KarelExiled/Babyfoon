from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import os
import glob
import matplotlib.pyplot as plt
from pydub import AudioSegment
import numpy as np
import matplotlib.dates as mdates
from matplotlib.dates import HourLocator, DateFormatter

# Path to ffmpeg (update with the correct path for your system)
ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"  # Example path

if os.path.exists(ffmpeg_path):
    AudioSegment.ffmpeg = ffmpeg_path
else:
    AudioSegment.ffmpeg = None
    print("Warning: ffmpeg not found. Audio processing may not work.")

app = Flask(__name__)

UPLOAD_DIR = 'uploads'
PLOT_FOLDER = 'static/plots'
sleep_schedule = {}

if not os.path.exists(PLOT_FOLDER):
    os.makedirs(PLOT_FOLDER)

def classify_sound(filename):
    if 'cry' in filename.lower():
        return 'Cry'
    return 'Other Noise'

def get_audio_properties(filename):
    try:
        audio = AudioSegment.from_wav(filename)
        duration = len(audio) / 1000
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)

        if samples.size == 0:
            raise ValueError("The audio file has no valid samples.")

        samples = samples[~np.isnan(samples)]
        samples = samples[~np.isinf(samples)]
        samples = samples[np.abs(samples) > 1e-10]

        if samples.size == 0:
            raise ValueError("No valid audio samples remain after cleaning.")

        rms = np.sqrt(np.mean(samples ** 2))

        if rms <= 0:
            raise ValueError("RMS value is non-positive.")

        loudness = 20 * np.log10(rms)
        return round(loudness, 2), round(duration, 2)

    except ValueError as ve:
        print(f"Error processing file {filename}: {ve}")
        return None, None
    except Exception as e:
        print(f"Unexpected error processing file {filename}: {e}")
        return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    data = request.get_json()
    date_str = data['date']
    bedtime_str = data['bedtime']
    wake_time_str = data['wake_time']

    date = datetime.strptime(date_str, "%Y-%m-%d")
    bedtime = datetime.strptime(bedtime_str, "%H:%M")
    wake_time = datetime.strptime(wake_time_str, "%H:%M")

    if wake_time < bedtime:
        wake_time += timedelta(days=1)

    bedtime = date.replace(hour=bedtime.hour, minute=bedtime.minute, second=0, microsecond=0)
    wake_time = date.replace(hour=wake_time.hour, minute=wake_time.minute, second=0, microsecond=0)

    sleep_duration = wake_time - bedtime

    sleep_schedule[date_str] = {
        'bedtime': bedtime.strftime("%H:%M"),
        'wake_time': wake_time.strftime("%H:%M"),
        'sleep_duration': str(sleep_duration)
    }

    return jsonify({
        'date': date_str,
        'bedtime': bedtime.strftime("%H:%M"),
        'wake_time': wake_time.strftime("%H:%M"),
        'sleep_duration': str(sleep_duration)
    })

@app.route('/sound_events/<date>', methods=['GET'])
def sound_events(date):
    bedtime_str = '22:00'
    wake_time_str = '06:00'
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    previous_day = date_obj - timedelta(days=1)

    bedtime = datetime.strptime(f"{previous_day.strftime('%Y-%m-%d')} {bedtime_str}", "%Y-%m-%d %H:%M")
    wake_time = datetime.strptime(f"{date} {wake_time_str}", "%Y-%m-%d %H:%M")

    sound_files = glob.glob(f"{UPLOAD_DIR}/Sound*_{previous_day.strftime('%Y-%m-%d')}*.wav") + \
                  glob.glob(f"{UPLOAD_DIR}/Sound*_{date}*.wav")

    event_list = []
    num_events = 0
    num_crying = 0

    for sound_file in sound_files:
        filename = os.path.basename(sound_file)
        try:
            parts = filename.split('_')
            timestamp_str = f"{parts[1]}_{parts[2].replace('.wav', '')}"
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

            if bedtime <= timestamp <= wake_time:
                event_type = classify_sound(filename)
                loudness, duration = get_audio_properties(sound_file)

                if loudness is not None and duration is not None:
                    if event_type == "Other Noise":
                        event_type = "Crying"

                    event_list.append({
                        'time': timestamp.strftime('%H:%M:%S'),
                        'type': event_type,
                        'loudness': loudness,
                        'duration': duration
                    })
                    num_events += 1
                    if event_type == 'Crying':
                        num_crying += 1
        except ValueError:
            print(f"Error parsing timestamp from filename: {filename}")
            continue

    return jsonify({
        'date': date,
        'num_events': num_events,
        'num_crying_events': num_crying,
        'sound_events': event_list
    })

@app.route('/night_overview/<date>', methods=['GET'])
def night_overview(date):
    print(f"Requested date: {date}")

    if date not in sleep_schedule:
        bedtime_str = '22:00'
        wake_time_str = '06:00'
    else:
        bedtime_str = sleep_schedule[date]['bedtime']
        wake_time_str = sleep_schedule[date]['wake_time']

    bedtime = datetime.strptime(bedtime_str, "%H:%M")
    wake_time = datetime.strptime(wake_time_str, "%H:%M")

    if wake_time < bedtime:
        wake_time += timedelta(days=1)

    sleep_duration = wake_time - bedtime

    return jsonify({
        'date': date,
        'bedtime': bedtime.strftime("%H:%M"),
        'wake_time': wake_time.strftime("%H:%M"),
        'sleep_duration': str(sleep_duration)
    })

def extract_sound_events(date, sound_files):
    events = []
    for sound_file in sound_files:
        filename_parts = sound_file.split('_')
        timestamp_str = filename_parts[-1].replace('.wav', '')
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
        except ValueError:
            try:
                timestamp = datetime.strptime(timestamp_str, "%m-%d-%y")
            except ValueError:
                timestamp = None

        if timestamp:
            event_type = classify_sound(sound_file)
            events.append({'time': timestamp, 'type': event_type})
    return events

@app.route('/plot/last_night/<date>', methods=['GET'])
def night_plot(date):
    plot_image_filename = f"{date.replace('-', '')}_timeline.png"
    plot_image_path = os.path.join(PLOT_FOLDER, plot_image_filename)

    if not os.path.exists(plot_image_path):
        generate_sleep_plot(date)

    return jsonify({"url": f"/static/plots/{plot_image_filename}"})


def generate_sleep_plot(date):
    if date not in sleep_schedule:
        bedtime = datetime.strptime(f"{date} 22:00", "%Y-%m-%d %H:%M")
        wake_time = datetime.strptime(f"{date} 06:00", "%Y-%m-%d %H:%M") + timedelta(days=1)
    else:
        bedtime_str = sleep_schedule[date]['bedtime']
        wake_time_str = sleep_schedule[date]['wake_time']
        bedtime = datetime.strptime(f"{date} {bedtime_str}", "%Y-%m-%d %H:%M")
        wake_time = datetime.strptime(f"{date} {wake_time_str}", "%Y-%m-%d %H:%M")
        if wake_time < bedtime:
            wake_time += timedelta(days=1)

    time_axis = [bedtime + timedelta(minutes=i) for i in range(int((wake_time - bedtime).total_seconds() / 60))]
    sleep_state = np.ones(len(time_axis))

    sound_files = glob.glob(f"{UPLOAD_DIR}/Sound*_{date}*.wav")
    extracted_events = []
    for sound_file in sound_files:
        filename = os.path.basename(sound_file)
        try:
            parts = filename.split('_')
            timestamp_str = f"{parts[1]}_{parts[2].replace('.wav', '')}"
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
            if bedtime <= timestamp <= wake_time:
                loudness, duration = get_audio_properties(sound_file)
                if loudness is not None and duration is not None:
                    extracted_events.append({"time": timestamp.strftime("%H:%M:%S"), "loudness": loudness, "duration": duration})
        except ValueError:
            print(f"Error parsing timestamp from filename: {filename}")

    for event in extracted_events:
        event_time = datetime.strptime(event["time"], "%H:%M:%S").replace(year=bedtime.year, month=bedtime.month, day=bedtime.day)
        if event_time < bedtime:
            event_time += timedelta(days=1)
        interruption_duration = 30
        start_index = max(0, int((event_time - bedtime).total_seconds() / 60))
        end_index = min(len(sleep_state), start_index + interruption_duration)
        sleep_state[start_index:end_index] = 0

    total_sleep_minutes = np.sum(sleep_state)
    total_sleep_hours = total_sleep_minutes / 60

    plt.figure(figsize=(12, 6))
    plt.plot(time_axis, sleep_state, label="Sleep State (1 = Sleeping, 0 = Awake)", color="blue")
    for event in extracted_events:
        event_time = datetime.strptime(event["time"], "%H:%M:%S").replace(year=bedtime.year, month=bedtime.month, day=bedtime.day)
        if event_time < bedtime:
            event_time += timedelta(days=1)
        plt.scatter(event_time, 0, color="red", label=f"Sound ({event['loudness']} dB)", zorder=5)

    plt.title(f"Sleep and Sound Events ({bedtime.strftime('%H:%M')} - {wake_time.strftime('%H:%M')}) for {date}")
    plt.xlabel("Time")
    plt.ylabel("Sleep State")
    plt.yticks([0, 1], ["Awake", "Sleeping"])
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    time_formatter = mdates.DateFormatter("%H:%M")
    plt.gca().xaxis.set_major_formatter(time_formatter)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    plot_image_filename = f"{date.replace('-', '')}_timeline.png"
    plot_image_path = os.path.join(PLOT_FOLDER, plot_image_filename)
    plt.savefig(plot_image_path)
    plt.close()

    print(f"Total sleep time: {total_sleep_hours:.2f} hours")

    # Run the app
    if __name__ == '__main__':
        app.run(debug=True)
