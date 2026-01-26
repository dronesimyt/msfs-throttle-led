@echo off
setlocal

REM ===== EDIT THESE =====
set "SRC_DIR=%USERPROFILE%\source\repos\msfs-throttle-led\MSFS Throttle LED"
set "DST_PARENT=%LOCALAPPDATA%\VortxEngine\app-2.5.28\Signal-x64\Effects\Static"
set "EFFECT_FOLDER=MSFS Throttle LED"
REM ======================

set "DST_DIR=%DST_PARENT%\%EFFECT_FOLDER%"

REM Remove existing target folder if it exists (junction or real folder)
if exist "%DST_DIR%" rmdir "%DST_DIR%"

REM Create folder junction
mklink /J "%DST_DIR%" "%SRC_DIR%"

echo.
echo Done. Restart SignalRGB to reload the effect.
pause
endlocal
