from picamera2 import Picamera2, Preview
import cv2
import pantilthat
import time

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

# Global variables for pan and tilt angles
pan_angle = 0
tilt_angle = 0
sensitivity = 3

# Function to update the pan and tilt angles
def update_pan_tilt(key):
    global pan_angle, tilt_angle, sensitivity

    if key == 82:  # Up arrow
        tilt_angle -= int(sensitivity)
    elif key == 84:  # Down arrow
        tilt_angle += int(sensitivity)
    elif key == 81:  # Left arrow
        pan_angle -= int(sensitivity)
    elif key == 83:  # Right arrow
        pan_angle += int(sensitivity)

    # Clamp the angles to stay within the servo's range
    pan_angle = max(-90, min(90, pan_angle))
    tilt_angle = max(-90, min(90, tilt_angle))

    # Update the servo positions
    pantilthat.pan(pan_angle)
    pantilthat.tilt(tilt_angle)

    print(f"Pan: {pan_angle}, Tilt: {tilt_angle}")

try:
    while True:
        # Capture and display the camera feed
        frame = picam2.capture_array()
        flipped_frame = cv2.flip(frame, -1)
        cv2.imshow("Camera Output", flipped_frame)

        # Check for key presses
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):  # Exit on 'q'
            break
        elif key in [81, 82, 83, 84]:  # Arrow keys
            update_pan_tilt(key)
finally:
    # Cleanup resources
    picam2.stop()
    cv2.destroyAllWindows()
