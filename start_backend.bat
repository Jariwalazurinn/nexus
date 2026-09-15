@echo off
title Orders Agent Backend
echo Starting Orders Agent Backend...
where python >nul 2>nul
if %errorlevel%==0 (
    python run_backend.py
) else (
    py run_backend.py
)
pause
