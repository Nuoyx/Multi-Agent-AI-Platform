@echo off
where uv >nul 2>&1
if errorlevel 1 (
    echo uv is required to start the Python backend.
    exit /b 1
)
start "Auth" /D "%~dp0ALiceAI\backend\services\auth" cmd.exe /k uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8081
start "Chat" /D "%~dp0ALiceAI\backend\services\chat" cmd.exe /k uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8082
start "Agent" /D "%~dp0ALiceAI\backend\services\agent" cmd.exe /k uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8083
start "Gateway" /D "%~dp0ALiceAI\backend\gateway" cmd.exe /k uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
