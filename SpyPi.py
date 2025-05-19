from picamera2 import Picamera2, Preview
import cv2
import pantilthat
import time
import numpy as np
import threading

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

# Global variables for pan and tilt angles
pan_angle = 0
tilt_angle = 0

# Function to update pan and tilt angles based on user input
def update_orientation():
    global pan_angle, tilt_angle
    while True:
        try:
            # Prompt user for input
            user_input = input("Enter pan and tilt angles (e.g., 45 30): ").strip()
            # Parse the input
            pan, tilt = map(int, user_input.split())

            # Clamp the angles to prevent servo overdrive
            pan = max(-90, min(90, pan))
            tilt = max(-90, min(90, tilt))

            # Update the global angles
            pan_angle = pan
            tilt_angle = tilt
        except ValueError:
            print("Invalid input. Please enter two integers separated by a space.")

# Start a separate thread for updating pan and tilt
thread = threading.Thread(target=update_orientation, daemon=True)
thread.start()

try:
    while True:
        # Set the pan and tilt angles
        pantilthat.pan(pan_angle)
        pantilthat.tilt(tilt_angle)

        # Capture and display the camera feed
        frame = picam2.capture_array()
        flipped_frame = cv2.flip(frame, -1)
        cv2.imshow("Camera Output", flipped_frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Cleanup resources
    picam2.stop()
    cv2.destroyAllWindows()
