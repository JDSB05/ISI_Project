import paho.mqtt.client as mqtt
import telepot
from telepot.loop import MessageLoop
import threading
import time
import random

# Configurações do broker MQTT
mqtt_broker = "mqtt"  # Utilize 'mqtt' como endereço do broker no Docker Compose
mqtt_port = 1883
mqtt_client = mqtt.Client()

# Variáveis globais para armazenar os dados dos sensores
sensor_data = {
    "temperature": None,
    "humidity": None,
    "co2": "normal",
    "motion": False
}

# Token do bot Telegram
bot_token = '7693586888:AAERrtk5fZZ2FkdRwFQK6-ovbNiNeZUrUic'  # Substitua pelo seu token do bot
bot = telepot.Bot(bot_token)

# Lista para armazenar os chat IDs dos usuários que iniciaram o bot
user_chat_ids = set()

def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT com código de resultado " + str(rc))
    client.subscribe("sensors/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"Mensagem recebida no tópico {topic}: {payload}")

    if topic == "sensors/temperature_humidity":
        temp_str, hum_str = payload.split(",")
        sensor_data["temperature"] = float(temp_str)
        sensor_data["humidity"] = float(hum_str)
        print(f"Temperatura recebida: {temp_str}°C, Umidade: {hum_str}%")
        check_environmental_conditions()

    elif topic == "sensors/co2":
        sensor_data["co2"] = payload
        print(f"Status de CO₂ recebido: {sensor_data['co2']}")
        check_co2_level()

    elif topic == "sensors/motion":
        sensor_data["motion"] = True
        print("Movimento detectado")
        simulate_object_detection()

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
            message += 'Pessoa Detectada! \n'
        elif detected_object == "cat":
            message += 'Gato Detectado! \n'
        elif detected_object == "dog":
            message += 'Cão Detectado! \n'
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
        MessageLoop(bot, handle_telegram_messages).run_as_thread()
        print("Bot Telegram iniciado e aguardando mensagens...")
    except Exception as e:
        print(f"Erro ao iniciar o bot Telegram: {e}")

# Iniciar o bot Telegram em uma thread separada
threading.Thread(target=start_telegram_bot, daemon=True).start()

# Configurar callbacks MQTT
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Conectar ao broker MQTT
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()
print("Cliente MQTT iniciado e aguardando mensagens...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Encerrando o programa")
finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("Cliente MQTT desconectado")