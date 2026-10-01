@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_runner.ps1"
echo.
if errorlevel 1 (
  echo Prototype runner installation failed.
) else (
  echo Prototype runner installation completed.
)
pause
