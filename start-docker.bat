@echo off
echo Starting Item Balancing Tool Docker Container...

REM Überprüfen, ob Docker installiert ist
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut.
    pause
    exit /b
)

REM Docker Compose überprüfen
docker-compose --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Docker Compose gefunden. Starte Container mit docker-compose...
    docker-compose up -d
    echo Container gestartet. Zugriff auf http://localhost:8501
) else (
    echo Docker Compose nicht gefunden. Starte Container mit docker...
    docker build -t item-balancing-tool .
    docker run -d -p 8501:8501 --name item-balancing-tool -v %cd%/data.json:/app/data.json item-balancing-tool
    echo Container gestartet. Zugriff auf http://localhost:8501
)

pause
