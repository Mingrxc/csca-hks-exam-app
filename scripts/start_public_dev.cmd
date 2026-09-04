@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_public_dev.ps1" %*
if errorlevel 1 (
  echo.
  echo Public development startup failed. Check the message above.
  pause
)
endlocal
