import os
import paho.mqtt.client as mqtt
import random
import time
import logging
import threading

# Configurações do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurações do broker MQTT
mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')  # Use 'localhost' como padrão
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
mqtt_client = mqtt.Client()

# ID do carro (pode ser definido como variável de ambiente)
car_id = os.getenv('CAR_ID', 'carro1')

# Conectar ao broker MQTT
logging.info("Conectando ao broker MQTT...")
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()
logging.info("Conectado ao broker MQTT")

def publish_sensor_data():
    while True:
        # Simular leitura de temperatura e umidade com valores aleatórios
        temperatura = round(random.uniform(-10.0, 50.0), 2)
        umidade = round(random.uniform(10.0, 90.0), 2)
        topic = f"sensors/{car_id}/temperature_humidity"
        mqtt_client.publish(topic, f"{temperatura},{umidade}")
        logging.info(f"Publicado no tópico {topic}: {temperatura},{umidade}")

        # Simular detecção de CO₂
        co2_status = "high" if random.choice([True, False]) else "normal"
        topic = f"sensors/{car_id}/co2"
        mqtt_client.publish(topic, co2_status)
        logging.info(f"Publicado no tópico {topic}: {co2_status}")

        time.sleep(10)  # Envia dados a cada 10 segundos

def simulate_motion():
    while True:
        time.sleep(random.randint(5, 15))  # Espera entre 5 e 15 segundos
        topic = f"sensors/{car_id}/motion"
        mqtt_client.publish(topic, "detected")
        logging.info(f"Publicado no tópico {topic}: Movimento detectado")

try:
    # Inicia threads para simular sensores
    threading.Thread(target=publish_sensor_data, daemon=True).start()
    threading.Thread(target=simulate_motion, daemon=True).start()

    # Manter o programa em execução
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    logging.info("Encerrando o programa")
finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    logging.info("Desconectado do broker MQTT")