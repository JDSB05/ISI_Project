import os
import paho.mqtt.client as mqtt
import random
import time
import logging
import threading

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelName)s - %(message)s')

# MQTT broker configuration
mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')  # Use 'localhost' as default
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
mqtt_client = mqtt.Client()

# Car and sensor IDs (can be set as environment variables)
car_id = os.getenv('CAR_ID', 'car1')
sensor_id = os.getenv('SENSOR_ID', 'sensor1')

# Connect to the MQTT broker
logging.info("Connecting to the MQTT broker...")
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()
logging.info("Connected to the MQTT broker")

# Initial sensor values
current_temperature = random.uniform(3.0, 25.0)  # Initial temperature in a realistic range
current_humidity = random.uniform(40.0, 60.0)     # Initial humidity in a realistic range

def publish_sensor_data():
    global current_temperature, current_humidity

    while True:
        # Gradually adjust temperature
        current_temperature += random.uniform(-5.0, 5.0)
        current_temperature = max(-10.0, min(50.0, current_temperature))  # Keep within realistic bounds

        # Gradually adjust humidity
        current_humidity += random.uniform(-5.0, 5.0)
        current_humidity = max(10.0, min(90.0, current_humidity))  # Keep within realistic bounds

        # Publish temperature and humidity
        topic = f"sensors/{car_id}/{sensor_id}/temperature_humidity"
        mqtt_client.publish(topic, f"{current_temperature:.2f},{current_humidity:.2f}")
        logging.info(f"\n--- Temperature and Humidity Data ---\nTopic: {topic}\nTemperature: {current_temperature:.2f}°C\nHumidity: {current_humidity:.2f}%\n")

        # Simulate CO₂ detection
        co2_status = "high" if random.random() < 0.1 else "normal"  # 10% chance of high CO2
        topic = f"sensors/{car_id}/{sensor_id}/co2"
        mqtt_client.publish(topic, co2_status)
        logging.info(f"\n--- CO₂ Data ---\nTopic: {topic}\nCO₂ Status: {co2_status}\n")

        time.sleep(10)  # Send data every 10 seconds

def simulate_motion():
    while True:
        time.sleep(random.randint(5, 15))  # Wait between 5 and 15 seconds
        topic = f"sensors/{car_id}/{sensor_id}/motion"
        mqtt_client.publish(topic, "detected")
        logging.info(f"Published to topic {topic}: Motion detected")

try:
    # Start threads to simulate sensors
    threading.Thread(target=publish_sensor_data, daemon=True).start()
    threading.Thread(target=simulate_motion, daemon=True).start()

    # Keep the program running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    logging.info("Shutting down the program")
finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    logging.info("Disconnected from the MQTT broker")