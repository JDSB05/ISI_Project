import os
import paho.mqtt.client as mqtt
import telepot
from telepot.loop import MessageLoop
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
import random
import csv
from datetime import datetime

# Configurações do broker MQTT
mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')  # Use 'localhost' como padrão
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
mqtt_client = mqtt.Client()

# Inicialização do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, logger=True, engineio_logger=True)

# Variáveis globais para armazenar os dados dos sensores
sensor_data = {
    "temperature": None,
    "humidity": None,
    "co2": "normal",
    "motion": False
}

# Nome do arquivo CSV
csv_file = 'sensor_data.csv'

# Escrever o cabeçalho no arquivo CSV
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['timestamp', 'temperature', 'humidity', 'co2', 'motion'])

# Token do bot Telegram
bot_token = '7693586888:AAERrtk5fZZ2FkdRwFQK6-ovbNiNeZUrUic'  # Substitua pelo seu token do bot
if bot_token == 'SEU_TOKEN_DO_BOT':
    raise ValueError("Você deve substituir 'SEU_TOKEN_DO_BOT' pelo token real do seu bot Telegram.")
bot = telepot.Bot(bot_token)

# Lista para armazenar os chat IDs dos usuários que iniciaram o bot
user_chat_ids = set()

@socketio.on('connect')
def handle_socket_connect():
    print("Cliente conectado via SocketIO")

    

def send_data_to_sockets(data):
    socketio.emit('sensor_update', data)
    

def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT com código de resultado " + str(rc))
    client.subscribe("sensors/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Mensagem recebida no tópico {topic}: {payload}")

    if topic == "sensors/temperature_humidity":
        temp_str, hum_str = payload.split(",")
        sensor_data["temperature"] = float(temp_str)
        sensor_data["humidity"] = float(hum_str)
        save_data_to_csv(timestamp)
        check_environmental_conditions()
        # Enviar dados para o cliente via SocketIO
        print("Enviando os dados para o cliente...")
        data = {'timestamp': timestamp, 'temperature': sensor_data['temperature'], 'humidity': sensor_data['humidity']}
        print(data)
        send_data_to_sockets(data)

    elif topic == "sensors/co2":
        sensor_data["co2"] = payload
        save_data_to_csv(timestamp)
        check_co2_level()
        socketio.emit('co2_update', {'timestamp': timestamp, 'co2': sensor_data["co2"]})

    elif topic == "sensors/motion":
        sensor_data["motion"] = True
        save_data_to_csv(timestamp)
        simulate_object_detection()
        socketio.emit('motion_update', {'timestamp': timestamp, 'motion': True})

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

def check_environmental_conditions():
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
        for chat_id in user_chat_ids:
            for message in messages:
                send_telegram_message(chat_id, message)

def check_co2_level():
    if sensor_data["co2"] == "high":
        message = "\u26A0 ALERTA: NÍVEL ELEVADO DE CO₂!"
        for chat_id in user_chat_ids:
            send_telegram_message(chat_id, message)

def simulate_object_detection():
    # Simular detecção de objetos
    possible_objects = ["person", "cat", "dog", None]
    detected_object = random.choice(possible_objects)
    print(f"Objeto detectado na simulação: {detected_object}")
    notify_users(detected_object)

def notify_users(detected_object):
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

    for chat_id in user_chat_ids:
        send_telegram_message(chat_id, message)

def send_telegram_message(chat_id, message):
    print(f"Enviando mensagem para o chat_id {chat_id}: {message}")
    bot.sendMessage(chat_id, message)

def handle_telegram_messages(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(f"Mensagem recebida do Telegram: {msg}")
    if content_type == 'text':
        command = msg['text'].lower()
        if command == '/start':
            user_chat_ids.add(chat_id)
            bot.sendMessage(chat_id, 'Bem-vindo! Você receberá alertas de sensores.')
            print(f"Usuário {chat_id} iniciou o bot.")
        elif command == '/stop':
            if chat_id in user_chat_ids:
                user_chat_ids.remove(chat_id)
            bot.sendMessage(chat_id, 'Você não receberá mais alertas.')
            print(f"Usuário {chat_id} parou o bot.")

def start_telegram_bot():
    try:
        print("Iniciando bot Telegram...")
        MessageLoop(bot, handle_telegram_messages).run_as_thread()
        print("Bot Telegram iniciado e aguardando mensagens...")
    except Exception as e:
        print(f"Erro ao iniciar o bot Telegram: {e}")

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

    # Iniciar o bot Telegram em uma thread separada
    threading.Thread(target=start_telegram_bot, daemon=True).start()

    # Iniciar o cliente MQTT em uma thread separada
    threading.Thread(target=start_mqtt_client, daemon=True).start()

    # Iniciar o Flask app
    start_flask_app()