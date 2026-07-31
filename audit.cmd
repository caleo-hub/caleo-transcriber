@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\audit.ps1"
exit /b %errorlevel%
