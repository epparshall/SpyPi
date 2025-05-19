from picamera2 import Picamera2, Preview
import cv2
import pantilthat
import time
import numpy as np

# Initialize the camera
picam2 = Picamera2()

# Configure the camera for preview
picam2.configure(picam2.create_preview_configuration())

# Start the camera
picam2.start()

try:
    while True:
        # Capture a frame
        frame = picam2.capture_array()
        t = time.time()
        freq = 10 # Hz
        a = math.sin(t * freq * np.pi) * 90
        a = int(a)

        pantilthat.pan(a)
        pantilthat.tilt(a)

        # Display the frame
        cv2.imshow("Camera Output", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Stop the camera and close OpenCV windows
    picam2.stop()
    cv2.destroyAllWindows()
