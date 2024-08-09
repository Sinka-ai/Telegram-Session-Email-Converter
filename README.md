# Telegram-Session-Email-Converter
This project is designed to manage Telegram sessions, including converting `tdata` folders into session strings, applying password protections, and optionally sending session strings via email.

## Features
- **Convert `tdata` folders**: Converts Telegram `tdata` session data into Pyrogram session strings.
- **Password management**: Adds or removes password protection from session files.
- **Email integration**: Sends session strings to a specified email address after processing.
- **Customizable settings**: Configure various options like device model, system version, and delay intervals.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/telegram-session-email-converter.git
    cd telegram-session-email-converter
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure the project:
    - Update the `config.json` file with your Telegram API credentials (`api_id`, `api_hash`), email settings, and other configuration options.

## Usage

1. Place your Telegram `tdata` folders into the designated input directory.

2. Run the script to process sessions:
    ```bash
    python main.py
    ```

3. After execution, session strings will be processed according to the configuration, and if email integration is enabled, they will be sent to the specified email address.

## Project Structure

- **main.py**: Main entry point for the application, handles the execution flow.
- **convert.py**: Contains the core logic for converting and processing Telegram sessions.
- **config.json**: Configuration file where you set your API keys, email credentials, and other options.

## Configuration
The `config.json` file allows for fine-tuning of the application's behavior. Key settings include:
- `api_id` and `api_hash`: Your Telegram API credentials.
- `password_to_remove` and `password_to_add`: Passwords for managing session encryption.
- `email`: The email address to send session strings to.
- `smtp_server`, `smtp_port`, `smtp_login`, `smtp_password`: SMTP server settings for sending emails.
- `interval_min`, `interval_max`: Time intervals between processing sessions.
- `delay_after_count` and `delay_duration`: Control how often and how long delays should occur during processing.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
