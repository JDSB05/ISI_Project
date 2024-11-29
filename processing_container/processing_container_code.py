import os
import threading
import time
import random
import csv
import requests
from datetime import datetime
import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# Configurações do broker MQTT
mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
mqtt_client = mqtt.Client()

# Inicialização do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', logger=True, engineio_logger=True)

# Variáveis globais para armazenar os dados dos sensores
sensor_data = {
    "temperature": None,
    "humidity": None,
    "co2": "normal",
    "motion": False
}

# Caminho do arquivo CSV
csv_file = './sensor_data.csv'

# Escrever o cabeçalho no arquivo CSV
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['timestamp', 'temperature', 'humidity', 'co2', 'motion'])

def save_data_to_csv(timestamp):
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            timestamp,
            sensor_data.get("temperature"),
            sensor_data.get("humidity"),
            sensor_data.get("co2"),
            sensor_data.get("motion")
        ])
    # Resetar o valor de motion depois de salvar
    sensor_data["motion"] = False

# URL do serviço do bot do Telegram
telegram_bot_url = 'http://telegram_bot_container:5001/send_message'

def send_telegram_message(car_id, message):
    print(f"Enviando mensagem para o carro {car_id}: {message}")
    data = {'car_id': car_id, 'message': message}
    response = requests.post(telegram_bot_url, json=data)
    if response.status_code != 200:
        print(f"Erro ao enviar mensagem: {response.text}")

def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT com código de resultado " + str(rc))
    client.subscribe("sensors/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Mensagem recebida no tópico {topic}: {payload}")

    # Supondo que o ID do carro seja parte do tópico, por exemplo: sensors/carro1/temperature_humidity
    parts = topic.split('/')
    if len(parts) >= 3:
        sensor_type = parts[2]
        car_id = parts[1]

        if sensor_type == "temperature_humidity":
            temp_str, hum_str = payload.split(",")
            sensor_data["temperature"] = float(temp_str)
            sensor_data["humidity"] = float(hum_str)
            save_data_to_csv(timestamp)
            check_environmental_conditions(car_id)
            # Enviar dados para o cliente via SocketIO
            print("Emitindo dados para o cliente via SocketIO")
            socketio.emit('sensor_update', {'timestamp': timestamp, 'temperature': sensor_data["temperature"], 'humidity': sensor_data["humidity"]})

        elif sensor_type == "co2":
            sensor_data["co2"] = payload
            save_data_to_csv(timestamp)
            check_co2_level(car_id)
            socketio.emit('co2_update', {'timestamp': timestamp, 'co2': sensor_data["co2"]})

        elif sensor_type == "motion":
            sensor_data["motion"] = True
            save_data_to_csv(timestamp)
            simulate_object_detection(car_id)
            socketio.emit('motion_update', {'timestamp': timestamp, 'motion': True})
    else:
        print("Formato de tópico inválido")

def check_environmental_conditions(car_id):
    messages = []

    temp = sensor_data.get("temperature")
    hum = sensor_data.get("humidity")

    if temp is not None:
        if temp > 30.0:
            messages.append(f"\u26A0 ALERTA: TEMPERATURA ELEVADA ({temp:.2f}°C)!")
        elif temp < 5.0:
            messages.append(f"\u26A0 ALERTA: TEMPERATURA MUITO BAIXA ({temp:.2f}°C)!")

    if hum is not None:
        if hum > 70.0:
            messages.append(f"\u26A0 ALERTA: UMIDADE ELEVADA ({hum:.2f}%)!")
        elif hum < 30.0:
            messages.append(f"\u26A0 ALERTA: UMIDADE MUITO BAIXA ({hum:.2f}%)!")

    if messages:
        for message in messages:
            send_telegram_message(car_id, message)

def check_co2_level(car_id):
    if sensor_data["co2"] == "high":
        message = "\u26A0 ALERTA: NÍVEL ELEVADO DE CO₂!"
        send_telegram_message(car_id, message)

def simulate_object_detection(car_id):
    # Simular detecção de objetos
    possible_objects = ["person", "cat", "dog", None]
    detected_object = random.choice(possible_objects)
    print(f"Objeto detectado na simulação: {detected_object}")
    notify_users(car_id, detected_object)

def notify_users(car_id, detected_object):
    message = ''
    if detected_object:
        if detected_object == "person":
            message += 'Pessoa Detectada!\n'
        elif detected_object == "cat":
            message += 'Gato Detectado!\n'
        elif detected_object == "dog":
            message += 'Cão Detectado!\n'
    else:
        message += 'Movimento Detectado.\n'

    temp = sensor_data.get("temperature")
    hum = sensor_data.get("humidity")
    if temp is not None and hum is not None:
        message += f'Temperatura: {temp:.2f}°C, Umidade: {hum:.2f}%\n'

    send_telegram_message(car_id, message)

# Rota principal do Flask
@app.route('/')
def index():
    return render_template('index.html')

def start_flask_app():
    print("Iniciando Flask app...")
    socketio.run(app, host='0.0.0.0', port=5000)

def start_mqtt_client():
    print("Iniciando cliente MQTT...")
    # Configurar callbacks MQTT
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Conectar ao broker MQTT
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_start()
    print("Cliente MQTT iniciado e aguardando mensagens...")

if __name__ == '__main__':
    print("Iniciando aplicação...")

    # Iniciar o cliente MQTT em uma thread separada
    threading.Thread(target=start_mqtt_client, daemon=True).start()

    # Iniciar o Flask app
    start_flask_app()