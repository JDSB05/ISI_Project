import os
import threading
import time
import eventlet
eventlet.monkey_patch()
import random
import csv
import requests
from datetime import datetime
import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# MQTT broker configurations
mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
mqtt_client = mqtt.Client()

# Flask initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

# Global variables to store sensor data
sensor_data = {}

# Path to the CSV file
csv_file = './sensor_data.csv'

# Write the header to the CSV file
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['timestamp', 'car_id', 'sensor_id', 'temperature', 'humidity', 'co2', 'motion'])

def save_data_to_csv(timestamp, car_id, sensor_id):
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        data = sensor_data.get((car_id, sensor_id), {})
        writer.writerow([
            timestamp,
            car_id,
            sensor_id,
            data.get("temperature"),
            data.get("humidity"),
            data.get("co2"),
            data.get("motion")
        ])

def send_telegram_message(car_id, sensor_id, message):
    print(f"\n[INFO] Sending message to car {car_id} and sensor {sensor_id}: {message}")
    data = {'car_id': car_id, 'sensor_id': sensor_id, 'message': message}
    try:
        response = requests.post(telegram_bot_url, json=data)
        if response.status_code != 200:
            print(f"[ERROR] Error sending message: {response.text}")
    except Exception as e:
        print(f"[ERROR] Error sending message to Telegram bot: {e}")

# URL of the Telegram bot service
telegram_bot_url = 'http://telegram_bot_container:5001/send_message'

def on_connect(client, userdata, flags, rc):
    print(f"\n[INFO] Connected to MQTT broker with result code {rc}")
    client.subscribe("sensors/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[INFO] Message received on topic {topic}: {payload}")

    # Assuming the car ID and sensor ID are part of the topic, e.g., sensors/car1/sensor1/temperature_humidity
    parts = topic.split('/')
    if len(parts) >= 4:
        sensor_type = parts[3]
        car_id = parts[1]
        sensor_id = parts[2]

        # Initialize car and sensor data if it doesn't exist yet
        if (car_id, sensor_id) not in sensor_data:
            sensor_data[(car_id, sensor_id)] = {
                "temperature": None,
                "humidity": None,
                "co2": None,
                "motion": False
            }

        if sensor_type == "temperature_humidity":
            temp_str, hum_str = payload.split(",")
            sensor_data[(car_id, sensor_id)]["temperature"] = float(temp_str)
            sensor_data[(car_id, sensor_id)]["humidity"] = float(hum_str)
            check_environmental_conditions(car_id, sensor_id)

        elif sensor_type == "co2":
            sensor_data[(car_id, sensor_id)]["co2"] = payload
            check_co2_level(car_id, sensor_id)

        elif sensor_type == "motion":
            sensor_data[(car_id, sensor_id)]["motion"] = True
            simulate_object_detection(car_id, sensor_id)

        # Save data after updating
        save_data_to_csv(timestamp, car_id, sensor_id)

        # Send all data to the client via SocketIO
        print(f"[INFO] Emitting data of car {car_id} and sensor {sensor_id} to the client via SocketIO")
        data_copy = sensor_data[(car_id, sensor_id)].copy()
        data_copy["car_id"] = car_id
        data_copy["sensor_id"] = sensor_id
        data_copy["timestamp"] = timestamp
        # Reset the motion value after sending the data
        sensor_data[(car_id, sensor_id)]["motion"] = False
        socketio.emit('sensor_data', data_copy)
    else:
        print("[ERROR] Invalid topic format")

def check_environmental_conditions(car_id, sensor_id):
    messages = []

    temp = sensor_data[(car_id, sensor_id)].get("temperature")
    hum = sensor_data[(car_id, sensor_id)].get("humidity")

    if temp is not None:
        if temp > 30.0:
            messages.append(f"\u26A0 ALERT: HIGH TEMPERATURE ({temp:.2f}°C)!")
        elif temp < 5.0:
            messages.append(f"\u26A0 ALERT: VERY LOW TEMPERATURE ({temp:.2f}°C)!")

    if hum is not None:
        if hum > 70.0:
            messages.append(f"\u26A0 ALERT: HIGH HUMIDITY ({hum:.2f}%)!")
        elif hum < 30.0:
            messages.append(f"\u26A0 ALERT: VERY LOW HUMIDITY ({hum:.2f}%)!")

    for message in messages:
        send_telegram_message(car_id, sensor_id, message)

def check_co2_level(car_id, sensor_id):
    if sensor_data[(car_id, sensor_id)]["co2"] == "high":
        message = "\u26A0 ALERT: HIGH CO₂ LEVEL!"
        send_telegram_message(car_id, sensor_id, message)

def simulate_object_detection(car_id, sensor_id):
    # Simulate object detection
    possible_objects = ["person", "cat", "dog", None]
    detected_object = random.choice(possible_objects)
    print(f"\n[INFO] Object detected in simulation for car {car_id} and sensor {sensor_id}: {detected_object}")
    notify_users(car_id, sensor_id, detected_object)

def notify_users(car_id, sensor_id, detected_object):
    message = ''
    if detected_object:
        if detected_object == "person":
            message += 'Person Detected!\n'
        elif detected_object == "cat":
            message += 'Cat Detected!\n'
        elif detected_object == "dog":
            message += 'Dog Detected!\n'
    else:
        message += 'Motion Detected.\n'

    temp = sensor_data[(car_id, sensor_id)].get("temperature")
    hum = sensor_data[(car_id, sensor_id)].get("humidity")
    if temp is not None and hum is not None:
        message += f'Temperature: {temp:.2f}°C, Humidity: {hum:.2f}%\n'

    send_telegram_message(car_id, sensor_id, message)

# Main route of Flask
@app.route('/')
def index():
    return render_template('index.html')

def start_flask_app():
    print("\n[INFO] Starting Flask app...")
    socketio.run(app, host='0.0.0.0', port=5000)

def start_mqtt_client():
    print("\n[INFO] Starting MQTT client...")
    # Configure MQTT callbacks
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Connect to the MQTT broker
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_start()
    print("[INFO] MQTT client started and waiting for messages...")

if __name__ == '__main__':
    print("\n[INFO] Starting application...")

    # Start the MQTT client in a separate thread
    threading.Thread(target=start_mqtt_client, daemon=True).start()

    # Start the Flask app
    start_flask_app()