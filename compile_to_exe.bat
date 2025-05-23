@echo off
echo ================================================
echo Camera-Pan Video Combiner Compilation Script
echo ================================================
echo.

echo Installing dependencies (including py2exe)...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Please ensure Python and pip are installed and accessible.
    pause
    exit /b 1
)

echo.
echo Compiling to Windows executable...
python setup.py py2exe

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Compilation failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ================================
echo Compilation completed successfully!
echo ================================
echo.
echo The executable has been created in the 'dist' folder:
echo   dist\CameraPanVideoCombiner.exe
echo.
echo You can now distribute this executable file independently.
echo.

pause 