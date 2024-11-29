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

# Configurações do broker MQTT
mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
mqtt_client = mqtt.Client()

# Inicialização do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

# Variáveis globais para armazenar os dados dos sensores
sensor_data = {}

# Caminho do arquivo CSV
csv_file = './sensor_data.csv'

# Escrever o cabeçalho no arquivo CSV
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
    print(f"\n[INFO] Enviando mensagem para o carro {car_id} e sensor {sensor_id}: {message}")
    data = {'car_id': car_id, 'sensor_id': sensor_id, 'message': message}
    try:
        response = requests.post(telegram_bot_url, json=data)
        if response.status_code != 200:
            print(f"[ERRO] Erro ao enviar mensagem: {response.text}")
    except Exception as e:
        print(f"[ERRO] Erro ao enviar mensagem ao bot Telegram: {e}")

# URL do serviço do bot do Telegram
telegram_bot_url = 'http://telegram_bot_container:5001/send_message'

def on_connect(client, userdata, flags, rc):
    print(f"\n[INFO] Conectado ao broker MQTT com código de resultado {rc}")
    client.subscribe("sensors/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[INFO] Mensagem recebida no tópico {topic}: {payload}")

    # Supondo que o ID do carro e do sensor sejam parte do tópico, por exemplo: sensors/carro1/sensor1/temperature_humidity
    parts = topic.split('/')
    if len(parts) >= 4:
        sensor_type = parts[3]
        car_id = parts[1]
        sensor_id = parts[2]

        # Inicializar os dados do carro e sensor se ainda não existir
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

        # Salvar os dados após atualizar
        save_data_to_csv(timestamp, car_id, sensor_id)

        # Enviar todos os dados para o cliente via SocketIO
        print(f"[INFO] Emitindo dados do carro {car_id} e sensor {sensor_id} para o cliente via SocketIO")
        data_copy = sensor_data[(car_id, sensor_id)].copy()
        data_copy["car_id"] = car_id
        data_copy["sensor_id"] = sensor_id
        data_copy["timestamp"] = timestamp
        # Resetar o valor de motion depois de enviar os dados
        sensor_data[(car_id, sensor_id)]["motion"] = False
        socketio.emit('sensor_data', data_copy)
    else:
        print("[ERRO] Formato de tópico inválido")

def check_environmental_conditions(car_id, sensor_id):
    messages = []

    temp = sensor_data[(car_id, sensor_id)].get("temperature")
    hum = sensor_data[(car_id, sensor_id)].get("humidity")

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

    for message in messages:
        send_telegram_message(car_id, sensor_id, message)

def check_co2_level(car_id, sensor_id):
    if sensor_data[(car_id, sensor_id)]["co2"] == "high":
        message = "\u26A0 ALERTA: NÍVEL ELEVADO DE CO₂!"
        send_telegram_message(car_id, sensor_id, message)

def simulate_object_detection(car_id, sensor_id):
    # Simular detecção de objetos
    possible_objects = ["person", "cat", "dog", None]
    detected_object = random.choice(possible_objects)
    print(f"\n[INFO] Objeto detectado na simulação do carro {car_id} e sensor {sensor_id}: {detected_object}")
    notify_users(car_id, sensor_id, detected_object)

def notify_users(car_id, sensor_id, detected_object):
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

    temp = sensor_data[(car_id, sensor_id)].get("temperature")
    hum = sensor_data[(car_id, sensor_id)].get("humidity")
    if temp is not None and hum is not None:
        message += f'Temperatura: {temp:.2f}°C, Umidade: {hum:.2f}%\n'

    send_telegram_message(car_id, sensor_id, message)

# Rota principal do Flask
@app.route('/')
def index():
    return render_template('index.html')

def start_flask_app():
    print("\n[INFO] Iniciando Flask app...")
    socketio.run(app, host='0.0.0.0', port=5000)

def start_mqtt_client():
    print("\n[INFO] Iniciando cliente MQTT...")
    # Configurar callbacks MQTT
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Conectar ao broker MQTT
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_start()
    print("[INFO] Cliente MQTT iniciado e aguardando mensagens...")

if __name__ == '__main__':
    print("\n[INFO] Iniciando aplicação...")

    # Iniciar o cliente MQTT em uma thread separada
    threading.Thread(target=start_mqtt_client, daemon=True).start()

    # Iniciar o Flask app
    start_flask_app()