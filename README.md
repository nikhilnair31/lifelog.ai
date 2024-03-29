# lifelog.ai

This Python application, called lifelog.ai, is designed to capture screenshots at regular intervals, process them, and interact with various AI models for analysis. The application provides a user interface for configuration and control.

## Installation

1. Clone the repository

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the `app.py` script to start the application:

```bash
python app.py
```

or create executable with:

```bash
pyinstaller --onefile --windowed app.py
```

Once the application starts, you'll see a graphical user interface (GUI) where you can configure the interval between screenshots, select the desired quality, choose the AI model for analysis, and start or stop the screenshot process.

## Features

- **Automatic Screenshot Capture**: lifelog.ai captures screenshots at regular intervals from all connected monitors.

- **Quality Adjustment**: The application allows you to adjust the quality of the captured screenshots to optimize file size and clarity.

- **AI Model Integration**: lifelog.ai integrates with two AI models for image analysis: GPT (OpenAI) and Moondream. These models can analyze the captured screenshots and provide insights based on the selected model.

- **Database Storage**: Captured screenshots and corresponding AI analysis results are stored in a SQLite database (`data/*.db`) for future reference.

## Configuration

- **Interval**: Set the time interval (in minutes) between consecutive screenshots.

- **System Prompt**: Customize the default prompt used when interacting with the AI models.

- **Quality**: Choose the desired quality percentage for the captured screenshots.

- **Model Selection**: Select the AI models (GPT/Together/Whisper/Moondream) for image/audio analysis.

## Dependencies

- Python 3.x
- `base64`
- `sqlite3`
- `tempfile`
- `requests`
- `pyautogui`
- `tkinter`
- `PIL`
- `gradio_client`
- `dotenv`
- `screeninfo`

## Contributing

Contributions are welcome! If you have any suggestions, enhancements, or bug fixes, feel free to open an issue or create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.