import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, message):
    data = json.loads(message.payload.decode())
    print("Data received for integration:", data)
    # Data processing (simulation)
    processed_data = {
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "co2_level": data["co2_level"],
        "status": "normal" if data["co2_level"] < 500 else "alert"
    }
    client.publish("data/processed", json.dumps(processed_data))
    print("Processed data sent:", processed_data)

client = mqtt.Client("DataIntegrator")
client.connect("mosquitto", 1883, 60)
client.subscribe("sensors/data")

client.on_message = on_message
client.loop_forever()