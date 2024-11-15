import paho.mqtt.client as mqtt
import telepot
from telepot.loop import MessageLoop
from io import BytesIO
import threading
import time
import cv2
import numpy as np

# MQTT Broker settings
mqtt_broker = "mqtt"  # Use 'mqtt' as the broker address in Docker Compose
mqtt_port = 1883
mqtt_client = mqtt.Client()

# Global variables to store sensor data
sensor_data = {
    "temperature": None,
    "humidity": None,
    "co2": None,
    "motion": False,
    "image": None
}

# Telegram bot token
bot_token = '7693586888:AAERrtk5fZZ2FkdRwFQK6-ovbNiNeZUrUic'  # Replace with your bot token
bot = telepot.Bot(bot_token)

# List to store chat IDs of users who have started the bot
user_chat_ids = set()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe("sensors/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload

    if topic == "sensors/temperature_humidity":
        temp_str, hum_str = payload.decode().split(",")
        sensor_data["temperature"] = float(temp_str)
        sensor_data["humidity"] = float(hum_str)
        print(f"Received temperature: {temp_str}, humidity: {hum_str}")

    elif topic == "sensors/co2":
        sensor_data["co2"] = payload.decode()
        print(f"Received CO2 status: {sensor_data['co2']}")

    elif topic == "sensors/motion":
        sensor_data["motion"] = True
        print("Motion detected")

    elif topic == "sensors/camera":
        sensor_data["image"] = payload
        print("Received image from camera")
        process_sensor_data()

def process_sensor_data():
    if sensor_data["motion"] and sensor_data["image"] is not None:
        # Reset motion flag
        sensor_data["motion"] = False

        # Process the image (object detection)
        detected_objects, img_bytes = perform_object_detection(sensor_data["image"])

        # Send alerts via Telegram
        for chat_id in user_chat_ids:
            send_telegram_alert(chat_id, detected_objects, img_bytes)

        # Clear the image data
        sensor_data["image"] = None

def perform_object_detection(image_bytes):
    # Load class names
    classFile = "coco.names"
    with open(classFile, "rt") as f:
        classNames = f.read().rstrip("\n").split("\n")

    # Load model configuration and weights
    configPath = "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
    weightsPath = "frozen_inference_graph.pb"

    net = cv2.dnn_DetectionModel(weightsPath, configPath)
    net.setInputSize(320, 320)
    net.setInputScale(1.0 / 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)

    # Decode image
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Object detection
    classIds, confs, bbox = net.detect(img, confThreshold=0.45, nmsThreshold=0.2)

    detected_objects = []
    objects_of_interest = ["person", "cat", "dog"]

    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects_of_interest:
                detected_objects.append(className)
                cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                cv2.putText(img, className.upper(), (box[0] + 10, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, f"{round(confidence * 100, 2)}%", (box[0] + 10, box[1] + 60),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

    # Encode image back to bytes
    _, img_encoded = cv2.imencode('.jpg', img)
    img_bytes = BytesIO(img_encoded.tobytes())

    return detected_objects, img_bytes

def send_telegram_alert(chat_id, detected_objects, photo_bytes):
    message = ''
    if detected_objects:
        if "person" in detected_objects:
            message += 'Pessoa Detectada! \n'
        if "cat" in detected_objects:
            message += 'Gato Detectado! \n'
        if "dog" in detected_objects:
            message += 'Cão Detectado! \n'
    else:
        message += 'Movimento Detectado. Por favor, verifique a fotografia.\n'

    # Add temperature and humidity info
    if sensor_data["temperature"] is not None and sensor_data["humidity"] is not None:
        temp = sensor_data["temperature"]
        hum = sensor_data["humidity"]
        message += f'Temperatura: {temp:.2f}°C, Umidade: {hum:.2f}%\n'

        if temp > 30.0:
            message += "\u26A0 ALERTA: TEMPERATURA ELEVADA! \u26A0\n"
        elif temp < 5.0:
            message += "\u26A0 ALERTA: TEMPERATURA MUITO BAIXA! \u26A0\n"

    # Add CO2 status
    if sensor_data["co2"] == "high":
        message += "\u26A0 ALERTA: QUALIDADE DO AR RUIM! \u26A0\n"

    # Send message and photo
    bot.sendMessage(chat_id, message)
    bot.sendPhoto(chat_id, ('photo.jpg', photo_bytes))

def handle_telegram_messages(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        command = msg['text'].lower()
        if command == '/start':
            user_chat_ids.add(chat_id)
            bot.sendMessage(chat_id, 'Bem-vindo! Você receberá alertas de sensores.')
        elif command == '/stop':
            if chat_id in user_chat_ids:
                user_chat_ids.remove(chat_id)
            bot.sendMessage(chat_id, 'Você não receberá mais alertas.')

# Start the Telegram bot message loop
MessageLoop(bot, handle_telegram_messages).run_as_thread()

# Set MQTT callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to MQTT broker
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting program")
finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
