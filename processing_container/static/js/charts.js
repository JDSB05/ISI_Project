const labels = [];
const temperatureData = [];
const humidityData = [];

// Temperature Chart
const tempCtx = document.getElementById('temperatureChart').getContext('2d');
const temperatureChart = new Chart(tempCtx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'Temperature (°C)',
            data: temperatureData,
            borderColor: 'rgba(255, 99, 132, 1)',
            fill: false
        }]
    },
    options: {
        scales: {
            x: { title: { display: true, text: 'Time' } },
            y: { title: { display: true, text: 'Temperature (°C)' } }
        },
        plugins: {
            annotation: {
                annotations: {
                    maxTempLine: { type: 'line', yMin: 30, yMax: 30, borderColor: 'red', borderDash: [6, 4] },
                    minTempLine: { type: 'line', yMin: 5, yMax: 5, borderColor: 'blue', borderDash: [6, 4] }
                }
            }
        }
    }
});

// Humidity Chart
const humCtx = document.getElementById('humidityChart').getContext('2d');
const humidityChart = new Chart(humCtx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'Humidity (%)',
            data: humidityData,
            borderColor: 'rgba(54, 162, 235, 1)',
            fill: false
        }]
    },
    options: {
        scales: {
            x: { title: { display: true, text: 'Time' } },
            y: { title: { display: true, text: 'Humidity (%)' } }
        },
        plugins: {
            annotation: {
                annotations: {
                    maxHumLine: { type: 'line', yMin: 70, yMax: 70, borderColor: 'red', borderDash: [6, 4] },
                    minHumLine: { type: 'line', yMin: 30, yMax: 30, borderColor: 'blue', borderDash: [6, 4] }
                }
            }
        }
    }
});

window.addEventListener('newSensorData', function (event) {
    const data = event.detail;
    labels.push(data.timestamp);
    temperatureData.push(data.temperature);
    humidityData.push(data.humidity);

    if (labels.length > 20) {
        labels.shift();
        temperatureData.shift();
        humidityData.shift();
    }

    temperatureChart.update();
    humidityChart.update();
});
