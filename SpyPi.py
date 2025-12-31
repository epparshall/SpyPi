from picamera2 import Picamera2
import cv2
import pantilthat
import time
import os
import threading
import telebot
from dotenv import load_dotenv

class SpyPi:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Initialize the camera
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration())
        self.picam2.start()

        # Pan and tilt angles
        self.pan_angle = 0
        self.tilt_angle = 0
        self.sensitivity = 3

        # Set initial pan/tilt to center
        pantilthat.pan(self.pan_angle)
        pantilthat.tilt(self.tilt_angle)
        print(f"Initial Pan: {self.pan_angle}, Initial Tilt: {self.tilt_angle}")

        # Initialize Telegram Bot
        if self.telegram_token and self.chat_id:
            self.bot = telebot.TeleBot(self.telegram_token)
            self.setup_telegram_handlers()
        else:
            self.bot = None
            print("Telegram token or chat ID not found. Telegram functionality disabled.")

    def setup_telegram_handlers(self):
        @self.bot.message_handler(func=lambda message: message.text.lower() == 'snap')
        def handle_snap(message):
            if str(message.chat.id) == self.chat_id:
                self.bot.reply_to(message, "Capturing image...")
                try:
                    # Capture a high-resolution image
                    config = self.picam2.create_still_configuration()
                    image_path = "capture.jpg"
                    self.picam2.switch_mode_and_capture_file(config, image_path, wait=False)
                    
                    # Wait for capture to complete
                    time.sleep(2) 

                    # Send the photo
                    with open(image_path, 'rb') as photo:
                        self.bot.send_photo(message.chat.id, photo)
                    
                    # Clean up the image file
                    os.remove(image_path)
                except Exception as e:
                    self.bot.reply_to(message, f"Failed to capture image: {e}")

    def start_telegram_polling(self):
        if self.bot:
            print("Starting Telegram polling...")
            # Run polling in a loop to auto-restart on errors
            while True:
                try:
                    self.bot.polling(non_stop=True)
                except Exception as e:
                    print(f"Telegram polling error: {e}. Restarting in 10 seconds.")
                    time.sleep(10)


    def update_pan_tilt(self, key):
        if key == ord('w'):  # Up
            self.tilt_angle -= int(self.sensitivity)
        elif key == ord('s'):  # Down
            self.tilt_angle += int(self.sensitivity)
        elif key == ord('a'):  # Left
            self.pan_angle -= int(self.sensitivity)
        elif key == ord('d'):  # Right
            self.pan_angle += int(self.sensitivity)

        # Clamp the angles
        self.pan_angle = max(-90, min(90, self.pan_angle))
        self.tilt_angle = max(-90, min(90, self.tilt_angle))

        pantilthat.pan(self.pan_angle)
        pantilthat.tilt(self.tilt_angle)
        print(f"Pan: {self.pan_angle}, Tilt: {self.tilt_angle}")


    def run(self):
        # Start Telegram bot in a separate thread
        if self.bot:
            telegram_thread = threading.Thread(target=self.start_telegram_polling, daemon=True)
            telegram_thread.start()

        try:
            while True:
                # Capture and display the camera feed
                frame = self.picam2.capture_array()
                flipped_frame = cv2.flip(frame, -1)
                cv2.imshow("Camera Output", flipped_frame)

                # Check for key presses
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):  # Exit on 'q'
                    break
                elif key in [ord('w'), ord('s'), ord('a'), ord('d')]:  # Movement keys
                    self.update_pan_tilt(key)
        finally:
            # Cleanup resources
            self.picam2.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    spypi = SpyPi()
    spypi.run()

