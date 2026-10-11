@echo off
rem Build the itch.io English demo ZIP (double-click). Output: Claude outputs\itch\heroschool_demo_en_BUILD.zip
cd /d "%~dp0..\.."
where python >nul 2>nul
if %errorlevel%==0 (python tools\itch\build_itch.py) else (py -3 tools\itch\build_itch.py)
if exist "Claude outputs\itch" start "" "Claude outputs\itch"
echo.
pause
