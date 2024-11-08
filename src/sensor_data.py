import paho.mqtt.client as mqtt
import json
import random
import time

client = mqtt.Client("DataCollector")
client.connect("mosquitto", 1883, 60)

def generate_synthetic_data():
    data = {
        "temperature": round(random.uniform(15, 35), 2),
        "humidity": round(random.uniform(30, 70), 2),
        "co2_level": round(random.uniform(400, 600), 2)
    }
    return data

while True:
    data = generate_synthetic_data()
    client.publish("sensors/data", json.dumps(data))
    print("Data sent:", data)
    time.sleep(5)
