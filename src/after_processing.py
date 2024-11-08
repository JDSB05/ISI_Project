import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, message):
    data = json.loads(message.payload.decode())
    temp = data["temperature"]
    co2_level = data["co2_level"]

    if temp > 30:
        print("Alerta: Temperatura Alta!")
    elif temp < 15:
        print("Alerta: Temperatura Baixa!")

    if co2_level > 500:
        print("Alerta: Alto Nível de CO2!")
    else:
        print("Nível de CO2 normal.")

client = mqtt.Client("IntelligenceLayer")
client.connect("mosquitto", 1883, 60)
client.subscribe("data/processed")
client.on_message = on_message
client.loop_forever()
