@echo off
set "PYTHONUNBUFFERED=1"

cd /d "%~dp0"
python ../msfs_signalrgb_bridge.py
pause
