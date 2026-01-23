# MSFS Throttle LED (SignalRGB)

This folder contains everything you need to run the MSFS → SignalRGB throttle + airline-theme bridge.

## Files

- `msfs_signalrgb_bridge.py` : SimConnect bridge + SimBrief theme sender (C1/C2) + throttle sender (THR)
- `MSFS Throttle LED.html` / `MSFS Throttle LED.png` : SignalRGB effect + icon
- `config.json` : SimBrief credentials (username or userid)
- `themes/` : airline color themes (`primary` = bar, `secondary` = background)

## SimBrief config

Edit `config.json`:

- Either set `simbrief_username`
- Or replace with `{ "simbrief_userid": "12345" }`

## Themes

Create a folder per airline ICAO (e.g. `DLH`, `BAW`) containing `theme.json`:

```json
{ "primary": "#005AA4", "secondary": "#FFFFFF" }
```

## SignalRGB install

Place this folder in your repo, then create a junction from SignalRGB `Effects\Static\MSFS Throttle LED` to this folder.
You can use `link_effect_folder.bat` (edit SRC_DIR once).

## Run

1. Start SignalRGB
2. Select effect: **MSFS Throttle LED**
3. Run `start_bridge.bat` (or `python msfs_signalrgb_bridge.py`)
