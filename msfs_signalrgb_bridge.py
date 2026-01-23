#!/usr/bin/env python3
# msfs_signalrgb_bridge.py
#
# Sends:
#   THR=<0..100>  (throttle lever position, scaled)
#   C1=R,G,B      (BAR color)
#   C2=R,G,B      (BACKGROUND color)
#
# Reads themes from ONE file: themes/themes.json with your structure:
# {
#   "default": { "colors": { "primary": "#..", "secondary": "#.." } },
#   "themes":  { "DLH": { "colors": {...} }, ... }
# }

import os
import json
import time
from typing import Optional, Tuple
from urllib.parse import quote

import requests
from SimConnect import SimConnect, AircraftRequests

EVENT_URL = "http://localhost:16034/canvas/event"
SENDER = "MSFSBridge"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

THEMES_DIR = os.path.join(BASE_DIR, "themes")
THEMES_INDEX = os.path.join(THEMES_DIR, "themes.json")

SIMBRIEF_URL = "https://www.simbrief.com/api/xml.fetcher.php"
THEME_REFRESH_S = 15.0

FULL_AT = 70.0  # lever% that maps to 100% (tune)
SLEEP_S = 0.05  # throttle update rate

# These are "theme semantics" (not SignalRGB event semantics):
# primary/secondary come from your themes.json colors.
DEFAULT_THEME = {"primary": "#ff0000", "secondary": "#0000ff"}


def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def safe_float(x) -> float:
    try:
        if x is None:
            return 0.0
        return float(x)
    except Exception:
        return 0.0


def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = (h or "").strip().lstrip("#")
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    if len(h) != 6:
        return (255, 0, 0)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def post_event(msg: str) -> bool:
    """
    Critical detail: keep '=' and ',' unescaped, so SignalRGB receives "C1=R,G,B".
    """
    try:
        ev = quote(msg, safe="=,")
        sender = quote(SENDER, safe="")
        url = f"{EVENT_URL}?sender={sender}&event={ev}"
        r = requests.post(url, timeout=1.0)
        return r.status_code == 200
    except requests.RequestException:
        return False


def load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def get_theme_for_airline(index: dict, airline_icao: Optional[str]) -> dict:
    # index["default"]["colors"]["primary|secondary"]
    default_colors = None
    try:
        default_colors = (index.get("default") or {}).get("colors")
    except Exception:
        default_colors = None

    def get_default_hex(key: str) -> str:
        if isinstance(default_colors, dict) and isinstance(default_colors.get(key), str):
            return default_colors[key]
        return DEFAULT_THEME[key]

    if airline_icao:
        key = airline_icao.upper().strip()
        t = (index.get("themes") or {}).get(key)
        if isinstance(t, dict):
            colors = t.get("colors")
            if isinstance(colors, dict):
                p = colors.get("primary") or get_default_hex("primary")
                s = colors.get("secondary") or get_default_hex("secondary")
                return {"primary": p, "secondary": s}

    return {"primary": get_default_hex("primary"), "secondary": get_default_hex("secondary")}


def fetch_simbrief_airline_icao(cfg: dict) -> Optional[str]:
    username = cfg.get("simbrief_username")
    userid = cfg.get("simbrief_userid")
    if not username and not userid:
        return None

    params = {"userid": userid} if userid else {"username": username}

    try:
        r = requests.get(SIMBRIEF_URL, params=params, timeout=4)
        r.raise_for_status()
        xml = r.text
    except Exception:
        return None

    for tag in ("icao_airline", "airline"):
        s = f"<{tag}>"
        e = f"</{tag}>"
        i = xml.find(s)
        if i != -1:
            j = xml.find(e, i + len(s))
            if j != -1:
                val = xml[i + len(s) : j].strip()
                return val if val else None

    return None


def pick_first_working_pair(aq: AircraftRequests, candidates) -> Tuple[str, str]:
    for v1, v2 in candidates:
        try:
            _ = aq.get(v1)
            _ = aq.get(v2)
            return v1, v2
        except Exception:
            continue
    return candidates[0]


def main():
    sm = SimConnect()
    aq = AircraftRequests(sm, _time=100)

    candidates = [
        ("GENERAL_ENG_THROTTLE_LEVER_POSITION:1", "GENERAL_ENG_THROTTLE_LEVER_POSITION:2"),
        ("GENERAL_ENG_THROTTLE_LEVER_POSITION_1", "GENERAL_ENG_THROTTLE_LEVER_POSITION_2"),
        ("TURB_ENG_N1:1", "TURB_ENG_N1:2"),
        ("TURB_ENG_N1_1", "TURB_ENG_N1_2"),
    ]

    v1_name, v2_name = pick_first_working_pair(aq, candidates)
    print(f"Using vars: {v1_name} {v2_name}")

    last_airline = None
    last_colors_sent = None  # (bar_rgb, bg_rgb)
    next_theme_check = 0.0

    while True:
        now = time.time()

        # Theme refresh (SimBrief -> themes.json -> send colors)
        if now >= next_theme_check:
            next_theme_check = now + THEME_REFRESH_S

            cfg = load_json(CONFIG_PATH)
            themes_index = load_json(THEMES_INDEX)

            airline = fetch_simbrief_airline_icao(cfg)
            theme = get_theme_for_airline(themes_index, airline)

            # Option A mapping (swapped from your previous B):
            #   Background = PRIMARY
            #   Bar        = SECONDARY
            primary_rgb = hex_to_rgb(theme.get("primary", DEFAULT_THEME["primary"]))
            secondary_rgb = hex_to_rgb(theme.get("secondary", DEFAULT_THEME["secondary"]))

            bar_rgb = secondary_rgb
            bg_rgb = primary_rgb

            if airline != last_airline or last_colors_sent != (bar_rgb, bg_rgb):
                # C1 = bar, C2 = background
                post_event(f"C1={bar_rgb[0]},{bar_rgb[1]},{bar_rgb[2]}")
                post_event(f"C2={bg_rgb[0]},{bg_rgb[1]},{bg_rgb[2]}")
                last_airline = airline
                last_colors_sent = (bar_rgb, bg_rgb)

        # Throttle -> THR
        v1 = safe_float(aq.get(v1_name))
        v2 = safe_float(aq.get(v2_name))
        avg = (v1 + v2) / 2.0

        # normalize 0..1 to 0..100
        if avg <= 1.0:
            avg *= 100.0

        scaled = clamp((avg / FULL_AT) * 100.0, 0.0, 100.0)
        post_event(f"THR={scaled:.1f}")

        time.sleep(SLEEP_S)


if __name__ == "__main__":
    main()
