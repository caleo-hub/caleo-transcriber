@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build-package.ps1" %*
exit /b %ERRORLEVEL%
