import paho.mqtt.client as mqtt
import random
import time

# Configurações do broker MQTT
mqtt_broker = "mqtt"  # Utilize 'mqtt' como endereço do broker no Docker Compose
mqtt_port = 1883
mqtt_client = mqtt.Client()

# Conectar ao broker MQTT
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

# Funções simuladas para sensores
def detectar_co2():
    # Simula detecção de CO2 com valor aleatório
    return random.choice([True, False])

def ler_temperatura_umidade():
    # Simula leitura de temperatura e umidade com valores aleatórios
    temperatura = round(random.uniform(20.0, 30.0), 2)  # Temperatura entre 20 e 30 graus Celsius
    humidade = round(random.uniform(30.0, 70.0), 2)     # Umidade entre 30% e 70%
    return temperatura, humidade

def capture_image():
    # Simula captura de imagem (pode retornar dados fixos ou aleatórios)
    return b"ImagemEmBytesSimulada"

def publish_sensor_data():
    temp, umid = ler_temperatura_umidade()
    mqtt_client.publish("sensors/temperature_humidity", f"{temp},{umid}")

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

# Simular detecção de movimento periodicamente
def simulate_motion():
    while True:
        time.sleep(random.randint(5, 15))  # Espera entre 5 e 15 segundos
        motion_detected()

try:
    # Inicia thread para simular movimento (opcional)
    import threading
    threading.Thread(target=simulate_motion, daemon=True).start()

    while True:
        publish_sensor_data()
        time.sleep(60)  # Ajuste a frequência conforme necessário
except KeyboardInterrupt:
    print("Encerrando o programa")
finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()