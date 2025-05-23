@echo off
echo =======================================
echo Camera-Pan Video Combiner Setup Script
echo =======================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Please ensure Python and pip are installed and accessible.
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.
echo Starting Camera-Pan Video Combiner...
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start application!
    echo Please check that Python is installed correctly.
    pause
    exit /b 1
)

pause 