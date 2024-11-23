FROM python:3.9-slim

# Instalar dependências do sistema (se necessário)
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação e o script de espera
COPY sensors_container_code.py /app/
COPY wait-for-it.sh /app/
WORKDIR /app

# Definir o comando de entrada
CMD ["./wait-for-it.sh", "mqtt", "--", "python", "sensors_container_code.py"]