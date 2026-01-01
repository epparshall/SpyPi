from picamera2 import Picamera2
import cv2
import pantilthat
import time
import os
import threading
import telebot
from dotenv import load_dotenv

class SpyPi:
    def __init__(self, config: dict = None, debug: bool = False):
        self.debug = debug

        # Load env vars
        load_dotenv()
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Default hyperparameters
        self.preview_size = (320, 240)
        self.fps = 15
        self.jpeg_quality = 70
        self.pan_sensitivity = 3
        self.waitkey_interval = 15
        self.snapshot_size = (640, 480)  # smaller still image

        if config:
            self.preview_size = config.get("preview_size", self.preview_size)
            self.fps = config.get("fps", self.fps)
            self.jpeg_quality = config.get("jpeg_quality", self.jpeg_quality)
            self.pan_sensitivity = config.get("pan_sensitivity", self.pan_sensitivity)
            self.waitkey_interval = config.get("waitkey_interval", self.waitkey_interval)
            self.snapshot_size = config.get("snapshot_size", self.snapshot_size)

        # Initialize pan/tilt
        self.pan_angle = 0
        self.tilt_angle = 0

        # Initialize camera
        self.picam2 = Picamera2()
        preview_config = self.picam2.create_preview_configuration(
            main={"size": self.preview_size},
            controls={"FrameRate": self.fps}
        )
        self.picam2.configure(preview_config)
        self.picam2.start()

        # Center pan/tilt
        pantilthat.pan(self.pan_angle)
        pantilthat.tilt(self.tilt_angle)
        if self.debug:
            print(f"Initial Pan: {self.pan_angle}, Initial Tilt: {self.tilt_angle}")

        # Telegram bot
        self.bot = None
        if self.telegram_token and self.chat_id:
            self.bot = telebot.TeleBot(self.telegram_token)
            self.setup_telegram_handlers()
        else:
            if self.debug:
                print("Telegram disabled: missing token or chat ID")

    def setup_telegram_handlers(self):
        @self.bot.message_handler(func=lambda m: m.text.lower() == "snap")
        def handle_snap(message):
            if str(message.chat.id) != self.chat_id:
                return
            print(f"[Telegram] Received snap command from {message.chat.id}")
            self.bot.reply_to(message, "Capturing image...")

            def capture_and_send():
                try:
                    config = self.picam2.create_still_configuration(main={"size": self.snapshot_size})
                    image_path = f"capture_{int(time.time())}.jpg"
                    self.picam2.switch_mode_and_capture_file(config, image_path, wait=True)

                    with open(image_path, "rb") as photo:
                        self.bot.send_photo(message.chat.id, photo)
                        print(f"[Telegram] Photo sent: {image_path}")

                    os.remove(image_path)
                except Exception as e:
                    self.bot.reply_to(message, f"Failed to capture image: {e}")
                    print(f"[Telegram] Error capturing image: {e}")

            threading.Thread(target=capture_and_send, daemon=True).start()

    def start_telegram_polling(self):
        if not self.bot:
            return
        print("Starting Telegram polling...")
        while True:
            try:
                # long polling with timeout to reduce CPU usage
                self.bot.polling(non_stop=True, interval=0, timeout=60)
            except Exception as e:
                print(f"[Telegram] Polling error: {e}. Restarting in 10s.")
                time.sleep(10)

    def update_pan_tilt(self, key):
        if key == ord("w"):
            self.tilt_angle -= self.pan_sensitivity
        elif key == ord("s"):
            self.tilt_angle += self.pan_sensitivity
        elif key == ord("a"):
            self.pan_angle -= self.pan_sensitivity
        elif key == ord("d"):
            self.pan_angle += self.pan_sensitivity

        # clamp
        self.pan_angle = max(-90, min(90, self.pan_angle))
        self.tilt_angle = max(-90, min(90, self.tilt_angle))

        pantilthat.pan(self.pan_angle)
        pantilthat.tilt(self.tilt_angle)

        if self.debug:
            print(f"Pan: {self.pan_angle}, Tilt: {self.tilt_angle}")

    def run(self):
        if self.bot:
            threading.Thread(target=self.start_telegram_polling, daemon=True).start()

        try:
            while True:
                frame = self.picam2.capture_array()
                flipped_frame = cv2.flip(frame, 0)
                cv2.imshow("Camera Output", flipped_frame)

                key = cv2.waitKey(self.waitkey_interval) & 0xFF
                if key == ord("q"):
                    break
                elif key in [ord("w"), ord("s"), ord("a"), ord("d")]:
                    self.update_pan_tilt(key)
        finally:
            self.picam2.stop()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    config = {"fps": 10, "jpeg_quality": 50, "snapshot_size": (640, 480)}
    spypi = SpyPi(config=config, debug=True)
    spypi.run()
