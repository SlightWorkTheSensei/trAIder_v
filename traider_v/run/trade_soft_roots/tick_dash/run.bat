@echo off

:: Navigate to the directory of the script and run the Flask app
cd /d "%~dp0"
start "" python app.py

:: Open the Flask app in the default browser
start "" http://127.0.0.1:5000

pause
