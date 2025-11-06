const video = document.getElementById('video');
const statusDiv = document.getElementById('status');
const alarmSound = document.getElementById('alarm-sound');
const chartCanvas = document.getElementById('chart');

// Chart.js setup
const ctx = chartCanvas.getContext('2d');
const detectionChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Unsafe Confidence',
            data: [],
            borderColor: 'rgba(220, 53, 69, 1)',
            backgroundColor: 'rgba(220, 53, 69, 0.2)',
            borderWidth: 1,
            fill: true,
        }]
    },
    options: {
        scales: {
            x: {
                display: false
            },
            y: {
                beginAtZero: true,
                max: 1
            }
        },
        animation: {
            duration: 200
        }
    }
});

function updateChart(value) {
    const now = new Date();
    const label = `${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}`;

    detectionChart.data.labels.push(label);
    detectionChart.data.datasets[0].data.push(value);

    // Keep the chart to a fixed number of data points
    if (detectionChart.data.labels.length > 30) {
        detectionChart.data.labels.shift();
        detectionChart.data.datasets[0].data.shift();
    }
    detectionChart.update();
}


// Access camera
async function setupCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        video.srcObject = stream;
    } catch (err) {
        console.error("Error accessing camera: ", err);
        alert("Could not access the camera. Please allow camera access and refresh the page.");
    }
}

// Send frame to backend for detection
async function detectFlare() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL('image/jpeg');

    try {
        const response = await fetch('/detect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: dataUrl }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        updateUI(result);

    } catch (error) {
        console.error("Error sending frame to backend:", error);
        // If backend is down, default to safe and show 0 confidence
        updateUI({ status: 'safe', confidence: 0 });
    }
}

// Update UI based on detection result
function updateUI(result) {
    const confidence = result.confidence || 0;

    if (result.status === 'unsafe') {
        statusDiv.textContent = 'UNSAFE';
        statusDiv.className = 'unsafe';
        if (alarmSound.paused) {
            alarmSound.play().catch(e => console.error("Error playing sound:", e));
        }
    } else {
        statusDiv.textContent = 'SAFE';
        statusDiv.className = 'safe';
        if (!alarmSound.paused) {
            alarmSound.pause();
            alarmSound.currentTime = 0;
        }
    }
    // Update chart with the confidence score
    updateChart(confidence);
}


window.addEventListener('load', async () => {
    await setupCamera();
    // Start detection loop after a short delay to allow the camera to initialize
    video.onloadedmetadata = () => {
        setInterval(detectFlare, 1000); // Send a frame every 1 second
    };
});
