# SpyPi

A Python script for controlling a Raspberry Pi camera mounted on a Pan-Tilt HAT.

## Description

This project allows you to manually control the direction of a Raspberry Pi camera using the arrow keys on your keyboard. It displays the camera feed in a window on your desktop.

## Installation

This project requires a mix of system-level libraries (for hardware access) and Python packages. Follow these steps in order for a correct setup on a Raspberry Pi.

1.  **Clone the Repository**:
    First, get the code onto your Raspberry Pi.
    ```bash
    git clone <repository_url>
    cd SpyPi
    ```

2.  **Fix Directory Ownership**:
    This step is crucial to avoid "Permission denied" errors during package installation. If you used `sudo` to clone, you must give ownership back to your user.
    ```bash
    # Replace 'evan' with your actual username if different
    sudo chown -R evan:evan .
    ```

3.  **Install System-Level Dependencies via `apt`**:
    On Raspberry Pi, the entire camera stack (`picamera2` and `libcamera`) and other dependencies should be installed via `apt`. This handles all hardware-specific libraries correctly.
    ```bash
    sudo apt-get update
    sudo apt-get install python3-picamera2 python3-prctl libcap-dev
    ```

4.  **Create a Virtual Environment (with System Access)**:
    This isolates the project's dependencies while allowing access to the system-wide Python packages we installed via `apt`. The `--system-site-packages` flag is essential for hardware-specific libraries like `picamera2`.
    ```bash
    python3 -m venv .venv --system-site-packages
    ```

5.  **Activate the Virtual Environment**:
    You must activate the environment every time you open a new terminal to work on the project.
    ```bash
    source .venv/bin/activate
    ```
    Your shell prompt should change to show `(.venv)`.

6.  **Install Remaining Python Packages via `pip`**:
    Finally, install the remaining application-level Python libraries into your active virtual environment. **Do not use `sudo` for this command.**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Before running the script, make sure you are in the project directory and have activated the virtual environment.

1.  **Activate the virtual environment** (if it's not already active):
    ```bash
    source .venv/bin/activate
    ```

2.  **Run the script**:
    ```bash
    python3 SpyPi.py
    ```

3.  **Deactivate the virtual environment** (optional):
    When you are finished, you can deactivate the environment.
    ```bash
    deactivate
    ```

A window will open showing the camera feed.

## Controls

- **Up Arrow**: Tilt the camera up.
- **Down Arrow**: Tilt the camera down.
- **Left Arrow**: Pan the camera to the left.
- **Right Arrow**: Pan the camera to the right.
- **q**: Quit the application.

## Run on Boot (systemd)

To automatically run the `SpyPi.py` script when your Raspberry Pi boots up, the recommended method is to use `systemd`, which is the standard service manager on Raspberry Pi OS.

### Setup Instructions

1.  **Edit the service file (if necessary)**:
    Open the `spypi.service` file. By default, it assumes the project is located at `/home/evan/Documents/Github/SpyPi` and will be run by the `evan` user. If you placed the project in a different directory or are using a different username, you must update the `ExecStart`, `WorkingDirectory`, and `User` lines in `spypi.service` accordingly.

2.  **Copy the service file**:
    Copy the `spypi.service` file to the `systemd` directory on your Raspberry Pi. You will need to use `sudo` for this.
    ```bash
    sudo cp spypi.service /etc/systemd/system/spypi.service
    ```

3.  **Reload the systemd daemon**:
    After copying the file, tell `systemd` to look for new or changed services.
    ```bash
    sudo systemctl daemon-reload
    ```

4.  **Enable the service**:
    To make the service start automatically on every boot, enable it with the following command:
    ```bash
    sudo systemctl enable spypi.service
    ```

5.  **Start the service**:
    You can start the service immediately to test it without rebooting.
    ```bash
    sudo systemctl start spypi.service
    ```

### Managing the Service

Once the service is set up, you can manage it with these commands:

-   **Check the status**:
    See if the service is running and view its recent log output.
    ```bash
    sudo systemctl status spypi.service
    ```
    (Press `q` to exit the status view)

-   **Stop the service**:
    Manually stop the service.
    ```bash
    sudo systemctl stop spypi.service
    ```

-   **Start the service**:
    Manually start the service if it's stopped.
    ```bash
    sudo systemctl start spypi.service
    ```

-   **Disable the service**:
    To prevent the service from starting automatically on boot.
    ```bash
    sudo systemctl disable spypi.service
    ```

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

## Troubleshooting

### Telegram Installation Issues

This project uses `pyTelegramBotAPI`, which provides the `telebot` module. Be careful, as there are similarly named Telegram packages that are not compatible:

*   `python-telegram-bot` (uses a different API and module structure)
*   `py-telegram-bot-api` (a broken placeholder package often found on PiWheels or in caches)

If Telegram imports or functionality fails, you may have an incorrect or conflicting package installed. You can fix this by running the following commands from within your activated virtual environment:

1.  **Remove any conflicting Telegram-related packages**:
    ```bash
    pip uninstall -y pyTelegramBotAPI python-telegram-bot py-telegram-bot-api
    ```

2.  **Force a clean re-install of the correct package**:
    This command clears the cache and ensures you get the correct `pyTelegramBotAPI` from PyPI.
    ```bash
    pip install --no-cache-dir -r requirements.txt
    ```