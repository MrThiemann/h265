@echo off
chcp 65001 >nul
title H.264 AVC Converter - Installation und Start

echo.
echo ========================================
echo H.264 AVC Converter - Installation
echo ========================================
echo.

echo Prüfe Python-Installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    echo.
    echo Bitte installieren Sie Python 3.7+ von:
    echo https://www.python.org/downloads/
    echo.
    echo Wichtig: Aktivieren Sie "Add Python to PATH" bei der Installation
    echo.
    pause
    exit /b 1
)

echo Python gefunden!
python --version

echo.
echo Prüfe FFmpeg-Installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNUNG: FFmpeg ist nicht installiert!
    echo.
    echo Bitte installieren Sie FFmpeg von:
    echo https://ffmpeg.org/download.html
    echo.
    echo Oder verwenden Sie Chocolatey: choco install ffmpeg
    echo.
    echo Die Anwendung wird ohne FFmpeg nicht funktionieren!
    echo.
    set /p continue="Möchten Sie trotzdem fortfahren? (j/n): "
    if /i not "%continue%"=="j" exit /b 1
)

echo FFmpeg gefunden!
ffmpeg -version 2>&1 | findstr "ffmpeg version"

echo.
echo Installiere Python-Abhängigkeiten...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo FEHLER: Installation der Abhängigkeiten fehlgeschlagen!
    echo.
    echo Versuchen Sie folgendes:
    echo 1. Python neu installieren
    echo 2. pip aktualisieren: python -m pip install --upgrade pip
    echo 3. Virtuelle Umgebung verwenden
    echo.
    pause
    exit /b 1
)

echo.
echo Abhängigkeiten erfolgreich installiert!
echo.
echo Starte H.264 AVC Converter...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo FEHLER: Anwendung konnte nicht gestartet werden!
    echo.
    echo Prüfen Sie die Fehlermeldungen oben.
    echo.
    pause
)

echo.
echo Anwendung beendet.
pause
