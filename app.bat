@echo off
echo Inicializando app...
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERRO: Ambiente virtual nao encontrado. Por favor, execute setup.bat primeiro.
    pause
    exit /b 1
)

REM Check if server.py exists
if not exist "server.py" (
    echo ERRO: server.py nao foi encontrado no diretorio atual.
    pause
    exit /b 1
)

REM Run the server
echo Iniciando servidor em http://127.0.0.1:8888
echo Use CTRL+C para fechar o server
echo.
start "" http://127.0.0.1:8888
python server.py

pause