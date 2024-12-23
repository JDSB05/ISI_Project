import os
import paho.mqtt.client as mqtt
import random
import time
import logging
import threading

# Logger settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MQTT broker settings
mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')  # Use 'localhost' as default
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
mqtt_client = mqtt.Client()

# Car and sensor ID (can be set as environment variables)
car_id = os.getenv('CAR_ID', 'car1')
sensor_id = os.getenv('SENSOR_ID', 'sensor1')

# Connect to the MQTT broker
logging.info("Connecting to the MQTT broker...")
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()
logging.info("Connected to the MQTT broker")

def publish_sensor_data():
    while True:
        # Simulate temperature and humidity readings with random values
        temperature = round(random.uniform(-10.0, 50.0), 2)
        humidity = round(random.uniform(10.0, 90.0), 2)
        topic = f"sensors/{car_id}/{sensor_id}/temperature_humidity"
        mqtt_client.publish(topic, f"{temperature},{humidity}")
        logging.info(f"\n--- Temperature and Humidity Data ---\nTopic: {topic}\nTemperature: {temperature}°C\nHumidity: {humidity}%\n")

        # Simulate CO₂ detection
        co2_status = "high" if random.choice([True, False]) else "normal"
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