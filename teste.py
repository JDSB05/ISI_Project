import socketio

# Criar uma instância do cliente SocketIO
sio = socketio.Client()

@sio.event
def connect():
    print("Conectado ao servidor WebSocket")

@sio.event
def disconnect():
    print("Desconectado do servidor WebSocket")

@sio.on('sensor_update')
def on_sensor_update(data):
    print("Sensor update received:", data)

# Conectar ao servidor WebSocket
sio.connect('http://localhost:5000/')  # Substitua pela URL do seu WebSocket
sio.wait()