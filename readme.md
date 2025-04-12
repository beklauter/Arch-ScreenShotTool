# ScreenShot Tool

A modern, lightweight screenshot utility for Wayland/Hyprland built with PyQt5. This tool allows you to capture portions of your screen with a clean, sleek interface.

![Screenshot Tool](https://example.com/screenshot.png)

## Features

- Area selection with visual guides and sizing handles
- Real-time dimension display during selection
- Multiple output formats (PNG, JPG)
- Automatic clipboard copy of captured images
- System notifications when screenshots are saved
- Dark, material-inspired modern UI
- Global hotkey support (Win+Shift+S in Hyprland)

## Installation

### Prerequisites

Make sure you have the following dependencies installed:

```bash
# For Arch-based distributions
sudo pacman -S python-pyqt5 python-pillow grim wl-clipboard notify-send

# For Debian/Ubuntu-based distributions
sudo apt install python3-pyqt5 python3-pil grim wl-clipboard libnotify-bin
```

### Setup

1. Clone the repository:

```bash
git clone https://github.com/beklauter/ScreenShotTool.git
cd ScreenShotTool
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Make the script executable:

```bash
chmod +x main.py
```

## Usage

### Running Manually

Launch the application from your terminal:

```bash
./main.py
```

Or if using a virtual environment:

```bash
.venv/bin/python main.py
```

### Setting up a Global Hotkey (Hyprland)

To use the familiar Win+Shift+S shortcut from Windows:

1. Create a wrapper script:

```bash
mkdir -p ~/bin
```

2. Create the script file with the following content:

```bash
#!/bin/bash
cd ~/PycharmProjects/ScreenShotTool
/home/beklauter/PycharmProjects/ScreenShotTool/.venv/bin/python /home/beklauter/PycharmProjects/ScreenShotTool/main.py
```

3. Make it executable:

```bash
chmod +x ~/bin/screenshot-tool.sh
```

4. Add to your Hyprland configuration (typically `~/.config/hypr/hyprland.conf`):

```
# Screenshot tool keybinding (Win+Shift+S)
bind = SUPER SHIFT, S, exec, ~/bin/screenshot-tool.sh
```

5. Reload your Hyprland configuration or restart Hyprland.

## How It Works

1. Press the global shortcut key (Win+Shift+S) or click "Capture Screenshot"
2. The screen will dim and display a selection interface
3. Click and drag to select the area you want to capture
4. Release to capture the screenshot
5. The image is automatically saved and copied to clipboard

## Configuration

Currently, configuration options are available through the UI:

- **Format**: Choose between PNG or JPG
- **Close after capture**: Automatically close after capturing a screenshot

All screenshots are saved to `~/Pictures/Screenshots` by default.

## Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Screenshots

[Screenshots would be added here]

## Future Improvements

- Configuration file for custom settings
- Additional screenshot modes (window capture, full screen)
- Basic annotation tools
- Upload to popular image sharing services