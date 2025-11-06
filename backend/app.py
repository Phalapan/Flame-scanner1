from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
import numpy as np
import base64
import io
import os

app = Flask(__name__, static_folder='../frontend')

# --- In-memory storage for email configuration ---
# In a real app, this would be stored securely in a database or config file
EMAIL_CONFIG = {"recipient_email": "user@example.com"}

def simulate_detection(image):
    """
    Simulates smoke and flame detection.
    This is a placeholder. In a real application, this function would
    contain a machine learning model (e.g., TensorFlow, PyTorch) for inference.

    - It checks for dominant colors (red/orange for fire, grey/white for smoke).
    - Returns 'unsafe' if significant amounts of these colors are found.
    - Confidence is a simple calculation based on the percentage of these pixels.
    """
    # Convert image to RGB
    image = image.convert("RGB")
    img_np = np.array(image)

    # Define color ranges for fire (reds/oranges) and smoke (greys)
    # These are very basic and would need to be tuned significantly.
    fire_lower = np.array([200, 0, 0])
    fire_upper = np.array([255, 150, 0])
    smoke_lower = np.array([100, 100, 100])
    smoke_upper = np.array([220, 220, 220])

    # Create masks
    fire_mask = np.all((img_np >= fire_lower) & (img_np <= fire_upper), axis=-1)
    smoke_mask = np.all((img_np >= smoke_lower) & (img_np <= smoke_upper), axis=-1)

    # Calculate the percentage of pixels that match
    fire_pixels = np.sum(fire_mask)
    smoke_pixels = np.sum(smoke_mask)
    total_pixels = img_np.shape[0] * img_np.shape[1]

    fire_confidence = (fire_pixels / total_pixels)
    smoke_confidence = (smoke_pixels / total_pixels)

    # Determine status based on thresholds
    # If more than 0.5% of pixels look like fire, or 2% look like smoke, trigger "unsafe"
    if fire_confidence > 0.005 or smoke_confidence > 0.02:
        status = "unsafe"
        # Confidence is the max of the two detections
        confidence = max(fire_confidence * 10, smoke_confidence * 2) # Scale up for visibility
    else:
        status = "safe"
        confidence = max(fire_confidence, smoke_confidence)

    # Cap confidence at 1.0
    confidence = min(confidence, 1.0)

    return status, confidence

def send_email_alert(recipient):
    """
    Simulates sending an email alert.
    In a real-world scenario, this would use a library like smtplib
    to connect to an SMTP server and send an email.
    """
    print("===================================================")
    print(f"SIMULATING EMAIL ALERT")
    print(f"To: {recipient}")
    print(f"Subject: URGENT: Unsafe Condition Detected!")
    print(f"Body: Unsafe condition (flame or smoke) detected at the flare.")
    print("===================================================")


@app.route('/')
def serve_index():
    # Serves the main HTML file from the frontend directory
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Serves other static files (like app.js, css) from the frontend directory
    return send_from_directory(app.static_folder, path)


@app.route('/detect', methods=['POST'])
def detect():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"error": "Invalid input"}), 400

    # Decode the base64 image
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))

    # Perform the simulated detection
    status, confidence = simulate_detection(image)

    # If unsafe, simulate sending an email
    if status == 'unsafe':
        send_email_alert(EMAIL_CONFIG["recipient_email"])

    return jsonify({"status": status, "confidence": confidence})

if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible on the network
    app.run(host='0.0.0.0', port=5000, debug=True)
