import socketio

# Create an instance of the SocketIO client
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to the WebSocket server")

@sio.event
def disconnect():
    print("Disconnected from the WebSocket server")

@sio.on('sensor_update')
def on_sensor_update(data):
    print("Sensor update received:", data)

# Connect to the WebSocket server
sio.connect('http://localhost:5000/')  # Replace with your WebSocket URL
sio.wait()