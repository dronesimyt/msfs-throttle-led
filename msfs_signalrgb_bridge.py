import time
import requests

from SimConnect import SimConnect, AircraftRequests  # same style you used before

EVENT_URL = "http://localhost:16034/canvas/event"
SENDER = "MSFSBridge"


def post_thr(value: float):
    # value expected 0..100
    try:
        requests.post(
            EVENT_URL,
            params={"sender": SENDER, "event": f"THR={value:.1f}"},
            timeout=0.2,
        )
    except requests.RequestException:
        # SignalRGB not running or endpoint blocked -> ignore and keep trying
        pass


def clamp01(x):
    return max(0.0, min(1.0, x))


def main():
    sm = SimConnect()
    aq = AircraftRequests(sm, _time=200)  # request pacing

    # Pick ONE metric for “engine state”.
    # N1 is often best for airliners; throttle lever % also works.
    #
    # Variable names can differ depending on wrapper/version.
    # Start with these common candidates and adjust if needed.
    candidates = [
        ("GENERAL_ENG_THROTTLE_LEVER_POSITION:1", "GENERAL_ENG_THROTTLE_LEVER_POSITION:2"),
        ("GENERAL_ENG_THROTTLE_LEVER_POSITION_1", "GENERAL_ENG_THROTTLE_LEVER_POSITION_2"),
        ("TURB_ENG_N1:1", "TURB_ENG_N1:2"),
        ("TURB_ENG_N1_1", "TURB_ENG_N1_2"),
    ]

    chosen = None
    for a, b in candidates:
        try:
            _ = aq.get(a)
            _ = aq.get(b)
            chosen = (a, b)
            break
        except Exception:
            continue

    if not chosen:
        raise RuntimeError(
            "Could not read engine vars. You likely just need to adjust the SimVar names "
            "to match your SimConnect wrapper."
        )

    v1_name, v2_name = chosen
    print("Using vars:", v1_name, v2_name)

    # Update loop
    while True:
        try:
            v1 = aq.get(v1_name)
            v2 = aq.get(v2_name)

            # If N1: already 0..100. If throttle lever: usually 0..100.
            # Convert safely:
            v1f = float(aq.get(v1_name) or 0.0)
            v2f = float(aq.get(v2_name) or 0.0)
            avg = (v1f + v2f) / 2.0  # already 0..100 typically
            avg = max(0.0, min(100.0, avg))

            # avg is your throttle lever position (0..100)
            FULL_AT = 70.0  # tune: if CLB sits ~57-60, set this to 60

            scaled = (avg / FULL_AT) * 100.0
            scaled = max(0.0, min(100.0, scaled))

            post_thr(scaled)
            print(f"ENG1={v1f:.1f} ENG2={v2f:.1f} AVG={avg:.1f}", end="\r", flush=True)
            print(f"RAW={avg:.1f} SCALED={scaled:.1f}", end="\r", flush=True)
            # post_thr(avg)

        except Exception:
            # MSFS closed / SimConnect hiccup; keep retrying
            time.sleep(1.0)
            try:
                sm = SimConnect()
                aq = AircraftRequests(sm, _time=200)
            except Exception:
                pass

        time.sleep(0.01)
        # (You can go 0.05 for 20 Hz if you want.)


if __name__ == "__main__":
    main()
