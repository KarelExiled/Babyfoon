from flask import Flask, render_template, request, jsonify
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
import matplotlib.dates as mdates
from scipy.stats import pearsonr
import os
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Fixed bedtime and wake-up time
bedtime_fixed = datetime(2025, 1, 21, 19, 0)  # 19:00 (7:00 PM)
wake_time_fixed = datetime(2025, 1, 22, 9, 0)  # 09:00 (9:00 AM)

# Create a directory to save images temporarily
UPLOAD_FOLDER = 'static/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store received events
received_events = []

# Function to process received event data
def process_received_event(event_type, amplitude, p_value):
    event_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "amplitude": amplitude,
        "p_value": p_value
    }
    received_events.append(event_data)

# Route to handle receiving data (POST)
@app.route('/receive_data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()  # Expecting JSON data
        event_type = data.get("event_type")
        amplitude = data.get("amplitude")
        p_value = data.get("p_value")

        # Debugging: Print the received data
        print(f"Received Data: event_type={event_type}, amplitude={amplitude}, p_value={p_value}")

        if event_type and amplitude and p_value:
            # Process the received event data
            process_received_event(event_type, amplitude, p_value)
            return jsonify({"status": "success", "message": "Data received!"}), 200
        else:
            return jsonify({"status": "error", "message": "Missing required fields!"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Route to handle the homepage and show data for a specific night
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        chosen_day = request.form['chosen_day']
        chosen_day = datetime.strptime(chosen_day, "%Y-%m-%d")

        # Find the index of the chosen day
        chosen_night_index = next((index for index, day in enumerate(sleep_data) if day["date"] == chosen_day), None)

        if chosen_night_index is not None:
            image_filename, total_sleep_hours, total_sleep_minutes, adjusted_sleep_hours, adjusted_sleep_minutes, chosen_night = generate_sleep_plot(
                chosen_night_index)

            # Descriptive statistics for the last 7 nights (excluding the current day)
            total_sleep_durations = []
            total_wake_ups = []

            for i in range(max(0, chosen_night_index - 7), chosen_night_index):
                night_data = sleep_data[i]
                bedtime = night_data["bedtime"]
                wake_time = night_data["wake_time"]
                sound_events = night_data["sound_events"]

                # Create time axis for the current night
                time_axis = [bedtime + timedelta(minutes=i) for i in range(int((wake_time - bedtime).seconds / 60))]

                # Initialize sleep state (1 = Sleeping, 0 = Awake)
                sleep_state = np.ones(len(time_axis))

                # Mark awake periods during sound events
                for event in sound_events:
                    event_time = event["time"]
                    start_index = max(0, (event_time - bedtime).seconds // 60)
                    end_index = min(len(sleep_state), start_index + int(event["duration"]))

                    sleep_state[start_index:end_index] = 0

                    # Gradually transition back to sleep
                    transition_duration = 15  # 15 minutes for transition
                    transition_end_index = min(len(sleep_state), end_index + transition_duration)
                    transition_range = np.linspace(0, 1, transition_end_index - end_index)
                    sleep_state[end_index:transition_end_index] = transition_range

                # Calculate the total sleep time (time spent in sleep state = 1)
                sleep_times = np.array(time_axis)[sleep_state == 1]
                total_sleep_duration = len(sleep_times) * 60  # in seconds
                total_sleep_durations.append(total_sleep_duration)
                total_wake_ups.append(len(sound_events))  # Each sound event represents a wake-up

            # Convert total sleep durations from seconds to hours for descriptive statistics
            mean_sleep_duration = np.mean(total_sleep_durations) / 3600  # in hours
            median_sleep_duration = np.median(total_sleep_durations) / 3600  # in hours
            std_sleep_duration = np.std(total_sleep_durations) / 3600  # in hours

            # Calculate Pearson correlation between wake-ups and total sleep duration
            correlation_sleep_wake_up, _ = pearsonr(total_wake_ups, total_sleep_durations)

            # Get the latest received event (if any)
            received_event = received_events[-1] if received_events else None
            latest_p_value = received_event['p_value'] if received_event else None

            return render_template(
                'index.html',
                chosen_night=chosen_night,
                image_filename=image_filename,
                total_sleep_hours=total_sleep_hours,
                total_sleep_minutes=total_sleep_minutes,
                adjusted_sleep_hours=adjusted_sleep_hours,
                adjusted_sleep_minutes=adjusted_sleep_minutes,
                mean_sleep_duration=mean_sleep_duration,
                median_sleep_duration=median_sleep_duration,
                std_sleep_duration=std_sleep_duration,
                correlation_sleep_wake_up=correlation_sleep_wake_up,
                p_value=latest_p_value,  # pass the latest p-value from received events
                received_event=received_event,  # pass the latest event
                received_events=received_events
            )

    return render_template('index.html', received_events=received_events)

# Function to generate random sound events for a night
def generate_sound_events(bedtime, wake_time):
    num_events = random.randint(0, 5)
    events = []

    for _ in range(num_events):
        event_time = bedtime + timedelta(minutes=random.randint(0, int((wake_time - bedtime).seconds / 60)))
        loudness = round(random.uniform(70, 120), 2)
        duration = random.uniform(5, 20)

        events.append({"time": event_time, "loudness": loudness, "duration": duration})

    return events

# Simulate 4 weeks of data
start_date = datetime(2025, 1, 1)
sleep_data = []

for day in range(28):
    date = start_date + timedelta(days=day)
    bedtime = bedtime_fixed
    wake_time = wake_time_fixed
    sound_events = generate_sound_events(bedtime, wake_time)
    sleep_data.append({"date": date, "bedtime": bedtime, "wake_time": wake_time, "sound_events": sound_events})

# Function to process sleep data and generate plot
def generate_sleep_plot(chosen_night_index):
    chosen_night = sleep_data[chosen_night_index]
    time_axis = [chosen_night["bedtime"] + timedelta(minutes=i) for i in
                 range(int((chosen_night["wake_time"] - chosen_night["bedtime"]).seconds / 60))]

    # Initialize sleep state (1 = Sleeping, 0 = Awake)
    sleep_state = np.ones(len(time_axis))

    # Mark awake periods during sound events
    for event in chosen_night["sound_events"]:
        event_time = event["time"]
        start_index = max(0, (event_time - chosen_night["bedtime"]).seconds // 60)
        end_index = min(len(sleep_state), start_index + int(event["duration"]))
        sleep_state[start_index:end_index] = 0

        # Gradually transition back to sleep
        transition_duration = 15  # 15 minutes for transition
        transition_end_index = min(len(sleep_state), end_index + transition_duration)
        transition_range = np.linspace(0, 1, transition_end_index - end_index)
        sleep_state[end_index:transition_end_index] = transition_range

    # Calculate the total sleep time (time spent in sleep state = 1)
    sleep_times = np.array(time_axis)[sleep_state == 1]
    total_sleep_duration = len(sleep_times) * 60  # in seconds
    total_sleep_hours = total_sleep_duration // 3600
    total_sleep_minutes = (total_sleep_duration % 3600) // 60

    # Adjusted sleep time considering sound events
    adjusted_sleep_duration = 14 * 60 - len(
        chosen_night["sound_events"]) * 30  # 14 hours minus sound events * 0.5 hours
    adjusted_sleep_hours = adjusted_sleep_duration // 60
    adjusted_sleep_minutes = adjusted_sleep_duration % 60

    # Plot the sleep state for the chosen night
    plt.figure(figsize=(12, 6))
    plt.plot(time_axis, sleep_state, label=f"Night of {chosen_night['date'].strftime('%b %d, %Y')}", color="blue")

    # Add sound events as red dots
    for event in chosen_night["sound_events"]:
        plt.scatter(event["time"], 0, color="red", label=f"Sound: {event['loudness']} dB", zorder=5)

    # Formatting the plot
    plt.title(f"Sleep Data for Night of {chosen_night['date'].strftime('%b %d, %Y')}")
    plt.xlabel("Time")
    plt.ylabel("Sleep State (1 = Sleeping, 0 = Awake)")
    plt.yticks([0, 1], ["Awake", "Sleeping"])
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a file
    filename = f"sleep_plot_{chosen_night['date'].strftime('%Y%m%d')}.png"
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    plt.savefig(image_path)
    plt.close()

    return filename, total_sleep_hours, total_sleep_minutes, adjusted_sleep_hours, adjusted_sleep_minutes, chosen_night

if __name__ == '__main__':
    app.run(debug=True)
