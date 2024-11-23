FROM python:3.9-slim

# Instalar dependências do sistema (se necessário)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY sensors_container_code.py /app/
WORKDIR /app

# Definir o comando de entrada
CMD ["python", "sensors_container_code.py"]