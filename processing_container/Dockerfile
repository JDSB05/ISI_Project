FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Configurar o diretório de trabalho
WORKDIR /app

# Definir variáveis de ambiente
ENV MQTT_BROKER=mqtt
ENV MQTT_PORT=1883

# Copiar requirements.txt e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação, templates, estáticos e o script de espera
COPY processing_container_code.py wait-for-it.sh ./
COPY templates/ ./templates/
COPY static/ ./static/

# Dar permissão de execução ao script
RUN chmod +x wait-for-it.sh

# Definir o comando de entrada
CMD ["./wait-for-it.sh", "mqtt", "--", "python", "processing_container_code.py"]