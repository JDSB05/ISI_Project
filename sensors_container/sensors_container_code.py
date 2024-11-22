import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import adafruit_dht
from gpiozero import MotionSensor
import cv2
import time
import board

# Configurações do broker MQTT
mqtt_broker = "mqtt"  # Utilize 'mqtt' como endereço do broker no Docker Compose
mqtt_port = 1883
mqtt_client = mqtt.Client()

# Conectar ao broker MQTT
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

# Configuração dos pinos GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
pin_do_sensor_co2 = 18
pin_do_sensor_movimento = 13

GPIO.setup(pin_do_sensor_co2, GPIO.IN)
pir = MotionSensor(pin_do_sensor_movimento)

# Inicializa o sensor DHT22 no pino GPIO 4
dht_device = adafruit_dht.DHT22(board.D4)

def detectar_co2():
    valor = GPIO.input(pin_do_sensor_co2)
    co2_high = valor == GPIO.HIGH
    return co2_high

def ler_temperatura_umidade():
    try:
        temperatura = dht_device.temperature
        humidade = dht_device.humidity
        return temperatura, humidade
    except RuntimeError as error:
        print(f"Erro ao ler o sensor DHT22: {error}")
        return None, None

def capture_image():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Erro ao acessar a câmera")
            return None
        success, img = cap.read()
        cap.release()
        if success:
            _, img_encoded = cv2.imencode('.jpg', img)
            return img_encoded.tobytes()
        else:
            print("Falha ao capturar imagem")
            return None
    except Exception as e:
        print(f"Erro ao acessar a câmera: {e}")
        return None

def publish_sensor_data():
    temp, umid = ler_temperatura_umidade()
    if temp is not None and umid is not None:
        mqtt_client.publish("sensors/temperature_humidity", f"{temp},{umid}")
    else:
        print("Falha ao ler temperatura e humidade")

    co2_status = "high" if detectar_co2() else "normal"
    mqtt_client.publish("sensors/co2", co2_status)

def motion_detected():
    print("Movimento detectado!")
    mqtt_client.publish("sensors/motion", "detected")
    img_bytes = capture_image()
    if img_bytes:
        mqtt_client.publish("sensors/camera", img_bytes)
    else:
        print("Falha ao capturar imagem")

# Atribuir função de detecção de movimento
pir.when_motion = motion_detected

try:
    while True:
        publish_sensor_data()
        time.sleep(60)  # Ajuste a frequência conforme necessário
except KeyboardInterrupt:
    print("Encerrando o programa")
except Exception as e:
    print(f"Erro inesperado: {e}")
finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    GPIO.cleanup()
