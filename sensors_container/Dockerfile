FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Configurar o diretório de trabalho
WORKDIR /app

# Copiar requirements.txt e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação e o script de espera
COPY sensors_container_code.py .
COPY wait-for-it.sh .

# Dar permissão de execução ao script
RUN chmod +x wait-for-it.sh

# Definir variáveis de ambiente padrão
ENV MQTT_BROKER=mqtt
ENV MQTT_PORT=1883
ENV CAR_ID=carro1

# Definir o comando de entrada com host e porta separados
CMD ["./wait-for-it.sh", "mqtt", "--", "python", "sensors_container_code.py"]