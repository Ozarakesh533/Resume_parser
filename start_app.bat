@echo off
echo ========================================
echo    AI Resume Parser - Complete Setup
echo ========================================
echo.
echo Starting Backend API Server...
start "Backend API" cmd /k "python backend_api.py"
echo Backend starting at: http://127.0.0.1:8081
echo.
timeout /t 3 /nobreak >nul
echo Starting Frontend Server...
start "Frontend Server" cmd /k "python serve_frontend.py"
echo Frontend starting at: http://localhost:3000
echo.
echo ========================================
echo    Application Started Successfully!
echo ========================================
echo.
echo Backend API: http://127.0.0.1:8081
echo API Docs: http://127.0.0.1:8081/docs
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul
