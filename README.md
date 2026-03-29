# Robot Controller

ESP8266-based robot controller with a Python Flet mobile/web app and ESP-NOW communication between transmitter and receiver modules.

## Project Structure

```
├── app/                    # Python Flet application
│   ├── main.py             # Main app entry point
│   ├── config.py           # Configuration loader
│   ├── ui_components.py    # UI component factory
│   ├── udp_handler.py      # UDP command sender
│   ├── websocket_handler.py# WebSocket client
│   └── requirements.txt    # Python dependencies
├── esp/
│   └── test/               # ESP8266 test sketches
├── reciever.ino            # ESP-NOW receiver firmware
├── transmitter.ino         # ESP-NOW transmitter firmware
└── config.json             # App configuration
```

## Features

- Real-time robot control via UDP (movement bitmask)
- WebSocket connection for settings (WiFi SSID/password)
- ESP-NOW wireless link between transmitter and receiver ESP8266
- Responsive UI with Flet framework (Android + Web)
- Farsi language support

## Setup

### Python App

```bash
pip install -r app/requirements.txt
python app/main.py
```

### ESP8266 Firmware

1. Open `transmitter.ino` and `reciever.ino` in Arduino IDE
2. Install ESP8266 board support
3. Upload to your ESP8266 boards

### Configuration

Edit `config.json` to change:
- `esp_ws_url`: WebSocket endpoint
- Theme colors

## Communication

| Layer | Protocol | Purpose |
|-------|----------|---------|
| App ↔ ESP8266 | WebSocket (port 81) | Settings & commands |
| App ↔ ESP8266 | UDP (port 12345) | Movement control |
| Transmitter → Receiver | ESP-NOW | Physical button control |

## Requirements

- Python 3.8+
- ESP8266 boards (2x for ESP-NOW link)
- Arduino IDE with ESP8266 support
