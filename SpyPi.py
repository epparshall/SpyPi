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
        t = time.time()
        freq = 0.1 # Hz
        a = np.sin(t * freq * np.pi) * 90
        a = int(a)

        pantilthat.pan(a)
        pantilthat.tilt(a)

        frame = picam2.capture_array()
        flipped_frame = cv2.flip(frame, -1)

        # Display the frame
        cv2.imshow("Camera Output", flipped_frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Stop the camera and close OpenCV windows
    picam2.stop()
    cv2.destroyAllWindows()
