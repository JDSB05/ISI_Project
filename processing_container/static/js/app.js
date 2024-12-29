const carSelector = document.getElementById('carSelector');
const allData = [];
let selectedCar = "all";

carSelector.addEventListener('change', (event) => {
    selectedCar = event.target.value;
    updateTable();
});

function addCarToSelector(carId) {
    if (!Array.from(carSelector.options).some(option => option.value === carId)) {
        const option = document.createElement('option');
        option.value = carId;
        option.textContent = carId;
        carSelector.appendChild(option);
    }
}

function updateTable() {
    const tableBody = document.getElementById('sensor-data-table');
    tableBody.innerHTML = ""; // Clear table

    const filteredData = selectedCar === "all"
        ? allData
        : allData.filter(data => data.car_id === selectedCar);

    filteredData.forEach(data => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${data.timestamp}</td>
            <td>${data.car_id}</td>
            <td>${data.temperature || 'N/A'}</td>
            <td>${data.humidity || 'N/A'}</td>
            <td>${data.co2 || 'N/A'}</td>
            <td>${data.motion ? 'Yes' : 'No'}</td>
        `;
        tableBody.appendChild(row);
    });
}

window.addEventListener('newSensorData', function (event) {
    const data = event.detail;
    addCarToSelector(data.car_id);
    allData.push(data);
    updateTable();
});
