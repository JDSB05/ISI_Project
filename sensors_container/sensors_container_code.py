import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import Adafruit_DHT
from gpiozero import MotionSensor
import cv2
import numpy as np
import time

# MQTT Broker settings
mqtt_broker = "mqtt"  # Use 'mqtt' as the broker address in Docker Compose
mqtt_port = 1883
mqtt_client = mqtt.Client()

# Connect to MQTT broker
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
pin_do_sensor_co2 = 18
pin_do_sensor_temperatura = 4
pin_do_sensor_movimento = 13

GPIO.setup(pin_do_sensor_co2, GPIO.IN)
pir = MotionSensor(pin_do_sensor_movimento)

def detectar_co2():
    valor = GPIO.input(pin_do_sensor_co2)
    co2_high = valor == GPIO.HIGH
    return co2_high

def ler_temperatura_umidade():
    umid, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin_do_sensor_temperatura)
    return temp, umid

def capture_image():
    cap = cv2.VideoCapture(0)
    success, img = cap.read()
    cap.release()
    if success:
        _, img_encoded = cv2.imencode('.jpg', img)
        return img_encoded.tobytes()
    else:
        return None

def publish_sensor_data():
    temp, umid = ler_temperatura_umidade()
    if temp is not None and umid is not None:
        mqtt_client.publish("sensors/temperature_humidity", f"{temp},{umid}")
    else:
        print("Failed to read temperature and humidity")

    co2_status = "high" if detectar_co2() else "normal"
    mqtt_client.publish("sensors/co2", co2_status)

def motion_detected():
    print("Motion detected!")
    mqtt_client.publish("sensors/motion", "detected")
    img_bytes = capture_image()
    if img_bytes:
        mqtt_client.publish("sensors/camera", img_bytes)
    else:
        print("Failed to capture image")

# Assign motion detection handler
pir.when_motion = motion_detected

try:
    while True:
        publish_sensor_data()
        time.sleep(60)  # Adjust the frequency as needed
except KeyboardInterrupt:
    print("Exiting program")
finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    GPIO.cleanup()
