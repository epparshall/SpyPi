# SpyPi

A Python script for controlling a Raspberry Pi camera mounted on a Pan-Tilt HAT.

## Description

This project allows you to manually control the direction of a Raspberry Pi camera using the arrow keys on your keyboard. It displays the camera feed in a window on your desktop.

## Installation

1. Clone this repository.
2. Install the required Python libraries using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script from your terminal:
```bash
python SpyPi.py
```

A window will open showing the camera feed.

## Controls

- **Up Arrow**: Tilt the camera up.
- **Down Arrow**: Tilt the camera down.
- **Left Arrow**: Pan the camera to the left.
- **Right Arrow**: Pan the camera to the right.
- **q**: Quit the application.

## Run on Boot

To automatically run the `SpyPi.py` script when your Raspberry Pi boots up, you can use the provided `start_spypi.sh` script and `crontab`.

1. **Make the script executable**:
   If you haven't already, make the `start_spypi.sh` script executable:
   ```bash
   chmod +x start_spypi.sh
   ```

2. **Edit your crontab**:
   Open your crontab file for editing:
   ```bash
   crontab -e
   ```
   If it's your first time, you might be asked to choose an editor. Select your preferred one.

3. **Add the boot job**:
   Add the following line to the end of your crontab file. This will execute the `start_spypi.sh` script every time the Raspberry Pi is rebooted.

   **Important**: Make sure to replace `/path/to/start_spypi.sh` with the absolute path to the `start_spypi.sh` script on your system. For example, if your project is in `/home/pi/SpyPi`, the line would look like this: `@reboot /home/pi/SpyPi/start_spypi.sh`

   ```
   @reboot /path/to/start_spypi.sh &
   ```
   Adding `&` at the end will run the script in the background. This is crucial because `SpyPi.py` is a long-running process and running it in the background allows the Raspberry Pi to continue its boot sequence without waiting for the Python script to terminate.

4. **Save and Exit**:
   Save the file and exit the editor. Your script is now scheduled to run on boot.

## Telegram Integration

To control the SpyPi via Telegram, you'll need to provide a bot token and your chat ID in the `.env` file.

### Getting your Telegram Bot Token

1.  **Find BotFather**: In the Telegram app, search for "BotFather" (it has a verified checkmark) and start a chat with it.
2.  **Create a new bot**: Type `/newbot` and send it.
3.  **Name your bot**: Follow the prompts to give your bot a name (e.g., "SpyPi Camera") and a username (e.g., "MySpyPiBot"). The username must end in "bot".
4.  **Copy your token**: BotFather will provide you with an API token. It's a long string of letters and numbers. Copy this token and paste it into the `.env` file as the value for `TELEGRAM_BOT_TOKEN`.

### Getting your Telegram Chat ID

1.  **Find and start your bot**: In the Telegram app's search bar, type the username of the bot you just created. Select it from the search results to open a chat, then send it a message (e.g., "/start" or "hello").
2.  **Retrieve your chat ID**: Open your web browser and go to the following URL, replacing `<YOUR_TELEGRAM_BOT_TOKEN_HERE>` with the token you just received:
    ```
    https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN_HERE>/getUpdates
    ```
3.  **Find the ID**: Look for the `result` array in the JSON response. If it's empty (`[]`), go back to your bot on Telegram, send another message, and then refresh the browser page.
    
    Inside the `result` array, find the `message` object, and inside that, find the `chat` object. The `id` field within this `chat` object is your `TELEGRAM_CHAT_ID`.
    
    **Important**: Be sure to use the `id` from the `chat` object, *not* the `update_id`. Copy this `id` and paste it into the `.env` file.