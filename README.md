# MSFS Throttle LED (SignalRGB)

A real-time bridge that connects Microsoft Flight Simulator 2024 with SignalRGB, displaying live engine throttle data and airline-specific LED color themes on compatible RGB hardware.

## Overview

This project integrates MSFS 2024 with SignalRGB, providing:

- **Live Throttle Display**: Real-time engine power (N1 or throttle lever) visualization as a bar on RGB devices
- **Airline Theming**: Automatically fetches your SimBrief flight plan and applies airline-specific LED colors
- **Light Status**: Displays strobe and beacon light states
- **Multi-Aircraft Support**: Works with turbine engines (N1 preferred) or throttle lever position
- **Zero Configuration**: Pre-configured with major airline themes

## Features

- **SimConnect Integration**: Direct connection to MSFS for live flight data
- **SimBrief Integration**: Automatic airline detection from flight plans (updates every 15 seconds)
- **18+ Airline Themes**: Pre-loaded themes for Lufthansa, Delta, KLM, British Airways, United Airlines, and more
- **Customizable Themes**: Easy to add new airline colors
- **Robust Reconnection**: Automatically reconnects if MSFS closes
- **Lightweight**: Minimal CPU overhead, efficient update cycles

## Requirements

- **Microsoft Flight Simulator 2024** (or compatible version with SimConnect)
- **SignalRGB** (latest version)
- **Python 3.8+** with PySimConnect library
- Windows 10/11
- Compatible RGB hardware supported by SignalRGB

## Installation

### 1. Python Dependencies

Install required Python packages:

```bash
pip install pySimConnect requests
```

### 2. SignalRGB Effect Setup

The SignalRGB effect files are included in this folder. Create a symbolic link in your SignalRGB installation:

**Option A: Automatic (Recommended)**

- Edit `bin/install_simlinks.bat` and set the `SRC_DIR` to your SignalRGB directory
- Run `bin/install_simlinks.bat` as Administrator

**Option B: Manual**

- Navigate to your SignalRGB installation folder (`Effects\Static\`)
- Create a symbolic link/shortcut named `MSFS Throttle LED` pointing to this folder

### 3. Configuration

Edit `config.json` with your SimBrief credentials:

```json
{
  "simbrief_username": "your_simbrief_username",
  "simbrief_userid": "your_simbrief_userid"
}
```

**Note**: You need only one of these fields:

- `simbrief_username`: Your SimBrief login username
- `simbrief_userid`: Your SimBrief numeric user ID (found in SimBrief account settings)

## Usage

### Starting the Bridge

1. Start **Microsoft Flight Simulator 2024**
2. Start **SignalRGB**
3. In SignalRGB, select the **MSFS Throttle LED** effect
4. Run the bridge:
   - **Quick Start**: Double-click `bin/start_bridge.bat`
   - **Manual**: Open PowerShell/Command Prompt and run `python msfs_signalrgb_bridge.py`

The bridge will display connection status and throttle updates in the console.

### Real-Time Data

The bridge sends these signals to SignalRGB:

| Signal | Range | Description                                              |
| ------ | ----- | -------------------------------------------------------- |
| `THR`  | 0-100 | Engine power as percentage (N1 or throttle lever scaled) |
| `C1`   | R,G,B | Bar color (airline secondary color)                      |
| `C2`   | R,G,B | Background color (airline primary color)                 |
| `STR`  | 0-1   | Strobe light state (0 = off, 1 = on)                     |
| `BCN`  | 0-1   | Beacon light state (0 = off, 1 = on)                     |

## Themes

### Pre-Configured Airlines

The `themes/themes.json` file includes 18+ airline themes:

- **DAL** - Delta Air Lines
- **DLH** - Lufthansa
- **EWG** - Eurowings
- **EZY** - EasyJet
- **IBE** - Iberia
- **KLM** - KLM Royal Dutch Airlines
- **RJA** - Royal Jordanian Airlines
- **And more...** (see `themes/themes.json`)

### Adding Custom Themes

To add a new airline theme:

1. Open `themes/themes.json`
2. Add a new entry under `themes` with the airline's ICAO code:

```json
{
  "themes": {
    "YOUR_ICAO": {
      "name": "Your Airline Name",
      "colors": {
        "primary": "#RRGGBB",
        "secondary": "#RRGGBB",
        "text": "#FFFFFF"
      },
      "logo": {
        "light": "logo_white.png",
        "dark": "logo_color.png"
      }
    }
  }
}
```

**Color Guide**:

- `primary`: Main brand color (displayed as LED background)
- `secondary`: Accent color (displayed as LED bar)
- `text`: Text color for UI elements

### Default Theme

If no SimBrief flight plan is found or the airline is not configured, the default theme is used (defined in the `default` section of `themes.json`).

## Project Structure

```
msfs-throttle-led/
├── msfs_signalrgb_bridge.py      # Main bridge application
├── config.json                   # SimBrief credentials
├── README.md                     # This file
├── bin/
│   ├── start_bridge.bat          # Quick start script
│   └── install_simlinks.bat      # Creates symbolic links in SignalRGB
├── themes/
│   ├── themes.json               # All airline color themes
│   ├── DAL/                      # Airline-specific theme folders
│   ├── DLH/
│   ├── default/
│   └── ...
└── MSFS Throttle LED/
    ├── MSFS Throttle LED.html    # SignalRGB effect definition
    └── MSFS Throttle LED.png     # Effect icon
```

## Troubleshooting

### Bridge won't connect to MSFS

- Ensure MSFS 2024 is running
- Check that SimConnect is available in your MSFS installation
- Verify Windows Firewall isn't blocking the connection

### Colors not updating

- Confirm SimBrief username/userid in `config.json` is correct
- Check internet connection (SimBrief API requires connectivity)
- Manually verify your flight plan exists on simbrief.com
- The bridge refreshes themes every 15 seconds

### SignalRGB not receiving data

- Ensure SignalRGB is running and the MSFS Throttle LED effect is selected
- Check that SignalRGB REST API is enabled (default: port 16034)
- Verify the symbolic link points to this folder correctly

### No throttle data displayed

- Ensure you're in an aircraft with engines (the simulator must load an aircraft first)
- Check the console for aircraft variable compatibility messages
- N1 variables are preferred; throttle lever is the fallback

## Advanced Configuration

### Engine Variable Scaling

Edit `msfs_signalrgb_bridge.py` to adjust throttle scaling:

```python
FULL_AT = 70.0  # Throttle lever percentage that maps to 100% on display
SLEEP_S = 0.05  # Update interval in seconds (0.05 = 20 Hz)
```

### Theme Refresh Rate

```python
THEME_REFRESH_S = 15.0  # SimBrief poll interval in seconds
```

## Support & Contributing

For issues, feature requests, or contributions, please refer to the project repository.

---

**Happy flying!** ✈️ 🎮
