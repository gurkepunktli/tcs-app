// API Configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// DOM Elements
const cameraSection = document.getElementById('camera-section');
const previewSection = document.getElementById('preview-section');
const resultSection = document.getElementById('result-section');
const loadingSection = document.getElementById('loading');

const video = document.getElementById('camera');
const canvas = document.getElementById('canvas');
const preview = document.getElementById('preview');
const locationInfo = document.getElementById('location-info');
const resultsDiv = document.getElementById('results');

const startCameraBtn = document.getElementById('start-camera');
const captureBtn = document.getElementById('capture');
const uploadBtn = document.getElementById('upload');
const retakeBtn = document.getElementById('retake');
const newScanBtn = document.getElementById('new-scan');

// State
let stream = null;
let capturedImage = null;
let coordinates = null;

// Event Listeners
startCameraBtn.addEventListener('click', startCamera);
captureBtn.addEventListener('click', capturePhoto);
uploadBtn.addEventListener('click', uploadPhoto);
retakeBtn.addEventListener('click', retakePhoto);
newScanBtn.addEventListener('click', newScan);

// Start camera
async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment',
                width: { ideal: 1920 },
                height: { ideal: 1080 }
            }
        });

        video.srcObject = stream;
        video.classList.add('active');
        startCameraBtn.style.display = 'none';
        captureBtn.style.display = 'block';

        // Get location
        getLocation();
    } catch (error) {
        console.error('Kamera-Fehler:', error);
        alert('Kamera konnte nicht gestartet werden. Bitte Berechtigungen prüfen.');
    }
}

// Get GPS location
function getLocation() {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                coordinates = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };
                console.log('Standort erfasst:', coordinates);
            },
            (error) => {
                console.error('Standort-Fehler:', error);
                coordinates = null;
            }
        );
    }
}

// Capture photo
function capturePhoto() {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    capturedImage = canvas.toDataURL('image/jpeg', 0.9);

    // Stop camera
    stopCamera();

    // Show preview
    preview.src = capturedImage;
    cameraSection.style.display = 'none';
    previewSection.style.display = 'block';

    // Show location info
    if (coordinates) {
        locationInfo.innerHTML = `
            <strong>Standort:</strong><br>
            Lat: ${coordinates.latitude.toFixed(6)}<br>
            Lng: ${coordinates.longitude.toFixed(6)}<br>
            Genauigkeit: ±${Math.round(coordinates.accuracy)}m
        `;
    } else {
        locationInfo.innerHTML = '<em>Standort nicht verfügbar</em>';
    }
}

// Stop camera
function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    video.classList.remove('active');
}

// Upload photo to backend
async function uploadPhoto() {
    if (!capturedImage) {
        alert('Kein Foto vorhanden');
        return;
    }

    // Show loading
    previewSection.style.display = 'none';
    loadingSection.style.display = 'block';

    try {
        // Convert base64 to blob
        const response = await fetch(capturedImage);
        const blob = await response.blob();

        // Create form data
        const formData = new FormData();
        formData.append('image', blob, 'photo.jpg');

        if (coordinates) {
            formData.append('latitude', coordinates.latitude);
            formData.append('longitude', coordinates.longitude);
            formData.append('accuracy', coordinates.accuracy);
        }

        // Send to backend
        const apiResponse = await fetch(`${API_URL}/api/ocr/process`, {
            method: 'POST',
            body: formData
        });

        if (!apiResponse.ok) {
            throw new Error(`HTTP ${apiResponse.status}: ${apiResponse.statusText}`);
        }

        const result = await apiResponse.json();

        // Show results
        displayResults(result);

    } catch (error) {
        console.error('Upload-Fehler:', error);
        alert(`Fehler beim Verarbeiten: ${error.message}\n\nStelle sicher, dass das Backend läuft.`);
        previewSection.style.display = 'block';
    } finally {
        loadingSection.style.display = 'none';
    }
}

// Display OCR results
function displayResults(result) {
    resultsDiv.innerHTML = '';

    if (result.prices && result.prices.length > 0) {
        result.prices.forEach(price => {
            const priceItem = document.createElement('div');
            priceItem.className = 'price-item';
            priceItem.innerHTML = `
                <span class="price-label">${price.type}</span>
                <span class="price-value">${price.value} CHF</span>
            `;
            resultsDiv.appendChild(priceItem);
        });
    } else {
        resultsDiv.innerHTML = '<p>Keine Preise erkannt. Bitte versuche es erneut.</p>';
    }

    if (result.raw_text) {
        const rawText = document.createElement('div');
        rawText.style.marginTop = '1rem';
        rawText.innerHTML = `<strong>Erkannter Text:</strong><br><pre style="white-space: pre-wrap; font-size: 0.85rem;">${result.raw_text}</pre>`;
        resultsDiv.appendChild(rawText);
    }

    resultSection.style.display = 'block';
}

// Retake photo
function retakePhoto() {
    previewSection.style.display = 'none';
    cameraSection.style.display = 'block';
    startCamera();
}

// New scan
function newScan() {
    capturedImage = null;
    coordinates = null;
    resultsDiv.innerHTML = '';

    resultSection.style.display = 'none';
    cameraSection.style.display = 'block';
    startCameraBtn.style.display = 'block';
    captureBtn.style.display = 'none';
}

// Register service worker for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('Service Worker registriert'))
            .catch(err => console.log('Service Worker Fehler:', err));
    });
}
