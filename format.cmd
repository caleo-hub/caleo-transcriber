@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\format.ps1"
exit /b %errorlevel%
