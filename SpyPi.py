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

        # -----------------------------
        # Env
        # -----------------------------
        load_dotenv()
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # -----------------------------
        # Defaults
        # -----------------------------
        self.preview_size = (320, 240)
        self.snapshot_size = (640, 480)
        self.fps = 15
        self.jpeg_quality = 70
        self.pan_sensitivity = 3
        self.waitkey_interval = 15

        # Servo behavior
        self.pan_min = -90
        self.pan_max = 90
        self.tilt_min = -90
        self.tilt_max = 90

        self.reference_pan = 0
        self.reference_tilt = self.tilt_max   # <--- ceiling avoided

        self.init_delay_sec = 3.0
        self.ramp_step = 2        # degrees per step
        self.ramp_delay = 0.05    # seconds between steps

        if config:
            for k, v in config.items():
                setattr(self, k, v)

        # -----------------------------
        # State only (no motion yet)
        # -----------------------------
        self.pan_angle = self.reference_pan
        self.tilt_angle = self.reference_tilt
        self.servos_enabled = False

        # -----------------------------
        # Camera
        # -----------------------------
        self.picam2 = Picamera2()
        preview_config = self.picam2.create_preview_configuration(
            main={"size": self.preview_size},
            controls={"FrameRate": self.fps}
        )
        self.picam2.configure(preview_config)
        self.picam2.start()

        # -----------------------------
        # Telegram
        # -----------------------------
        self.bot = None
        if self.telegram_token and self.chat_id:
            self.bot = telebot.TeleBot(self.telegram_token)
            self.setup_telegram_handlers()
        elif self.debug:
            print("Telegram disabled: missing token or chat ID")

    # --------------------------------------------------
    # Servo ramping (critical safety feature)
    # --------------------------------------------------

    def ramp_to_angle(self, axis: str, start: int, target: int):
        step = self.ramp_step if target > start else -self.ramp_step
        for angle in range(start, target, step):
            if axis == "pan":
                pantilthat.pan(angle)
            else:
                pantilthat.tilt(angle)
            time.sleep(self.ramp_delay)

        # Final exact position
        if axis == "pan":
            pantilthat.pan(target)
        else:
            pantilthat.tilt(target)

    def enable_servos(self):
        if self.servos_enabled:
            return

        print(f"Enabling servos after {self.init_delay_sec:.1f}s...")
        time.sleep(self.init_delay_sec)

        # Start from wherever the servo currently is (unknown)
        # Ramp gently to reference
        self.ramp_to_angle("pan", 0, self.reference_pan)
        self.ramp_to_angle("tilt", 0, self.reference_tilt)

        self.servos_enabled = True

        print(f"Servos ready at Pan={self.pan_angle}, Tilt={self.tilt_angle}")

    # --------------------------------------------------
    # Telegram
    # --------------------------------------------------

    def setup_telegram_handlers(self):
        @self.bot.message_handler(func=lambda m: m.text and m.text.lower() == "snap")
        def handle_snap(message):
            if str(message.chat.id) != self.chat_id:
                return

            print("[Telegram] Received: snap")
            self.bot.reply_to(message, "Capturing image...")

            def capture_and_send():
                try:
                    config = self.picam2.create_still_configuration(
                        main={"size": self.snapshot_size}
                    )
                    path = f"capture_{int(time.time())}.jpg"

                    self.picam2.switch_mode_and_capture_file(config, path, wait=True)

                    with open(path, "rb") as f:
                        self.bot.send_photo(message.chat.id, f)
                        print(f"[Telegram] Sent photo: {path}")

                    os.remove(path)

                except Exception as e:
                    print(f"[Telegram] Capture failed: {e}")
                    self.bot.reply_to(message, f"Capture failed: {e}")

            threading.Thread(target=capture_and_send, daemon=True).start()

    def start_telegram_polling(self):
        if not self.bot:
            return

        print("Telegram polling started")
        while True:
            try:
                self.bot.polling(non_stop=True, timeout=60)
            except Exception as e:
                print(f"[Telegram] Polling error: {e}")
                time.sleep(10)

    # --------------------------------------------------
    # Manual control
    # --------------------------------------------------

    def update_pan_tilt(self, key):
        if not self.servos_enabled:
            return

        if key == ord("w"):
            self.tilt_angle -= self.pan_sensitivity
        elif key == ord("s"):
            self.tilt_angle += self.pan_sensitivity
        elif key == ord("a"):
            self.pan_angle -= self.pan_sensitivity
        elif key == ord("d"):
            self.pan_angle += self.pan_sensitivity

        self.pan_angle = max(self.pan_min, min(self.pan_max, self.pan_angle))
        self.tilt_angle = max(self.tilt_min, min(self.tilt_max, self.tilt_angle))

        pantilthat.pan(self.pan_angle)
        pantilthat.tilt(self.tilt_angle)

        if self.debug:
            print(f"Pan={self.pan_angle}, Tilt={self.tilt_angle}")

    # --------------------------------------------------
    # Main loop
    # --------------------------------------------------

    def run(self):
        if self.bot:
            threading.Thread(target=self.start_telegram_polling, daemon=True).start()

        threading.Thread(target=self.enable_servos, daemon=True).start()

        try:
            while True:
                frame = self.picam2.capture_array()
                cv2.imshow("Camera Output", cv2.flip(frame, 0))

                key = cv2.waitKey(self.waitkey_interval) & 0xFF
                if key == ord("q"):
                    break
                elif key in (ord("w"), ord("a"), ord("s"), ord("d")):
                    self.update_pan_tilt(key)
        finally:
            self.picam2.stop()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    config = {
        "fps": 10,
        "snapshot_size": (640, 480),
        "reference_tilt": 90,
        "ramp_step": 2,
        "ramp_delay": 0.05
    }

    SpyPi(config=config, debug=True).run()
