@echo off
echo Setting up the Full-Stack Web Todo Application...

REM Install frontend dependencies
echo Installing frontend dependencies...
npm install

REM Check if Python and pip are available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python first.
    pause
    exit /b 1
)

pip --version >nul 2>&1
if errorlevel 1 (
    echo pip not found. Please install pip first.
    pause
    exit /b 1
)

echo Installing backend dependencies...
cd src/backend
pip install -r requirements.txt
cd ..\..

echo Setup complete!
echo.
echo To run the application, use:
echo   npm run dev:concurrent
echo.
echo To run individually:
echo   Frontend: npm run dev
echo   Backend: npm run backend
pause