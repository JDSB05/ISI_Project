const socket = io();
console.log("Connected to WebSocket server");

socket.on('sensor_data', function (data) {
    console.log("New data received: ", data);
    window.dispatchEvent(new CustomEvent('newSensorData', { detail: data }));
});

socket.on('disconnect', function () {
    console.log("Disconnected from WebSocket server");
});

socket.on('connect_error', function () {
    console.log("Error connecting to WebSocket server");
});
