@echo off
echo Starting application setup...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao esta instalado ou nao foi encontrado no PATH.
    echo Por favor, instale Python 3.8+ de https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python versao encontrada: 
python --version

REM Check if LM Studio is running by testing the API endpoints
echo.
echo Checando conexao com LM Studio...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:1234/v1/embeddings > response.txt
set /p EMBEDDING_RESPONSE=<response.txt
del response.txt

curl -s -o nul -w "%%{http_code}" http://127.0.0.1:1234/v1/chat/completions > response.txt
set /p COMPLETION_RESPONSE=<response.txt
del response.txt

if "%EMBEDDING_RESPONSE%"=="200" if "%COMPLETION_RESPONSE%"=="200" (
    echo LM Studio esta rodando e seu acesso esta ativo!
) else (
    echo.
    echo ERRO: LM Studio parece nao estar rodando ou nao ha acesso.
    echo Por favor, confira se:
    echo 1. LM Studio esta instalado de https://lmstudio.ai/
    echo 2. LM Studio esta aberto
    echo 3. O 'local server' esta ativo nas configuracoes do LM Studio
    echo 4. The server is running on port 1234
    echo.
    echo Aperte qualquer botao para rodar o programa de qualquer jeito ou aperte CTRL+C para cancelar...
    pause >nul
)

REM Create virtual environment
echo.
echo Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo ERRO: Falha em criar o ambiente virtual
    pause
    exit /b 1
)

REM Activate virtual environment and install requirements
echo.
echo Ativando ambiente virtual e baixando dependencias...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERRO: Falha em ativar o ambiente virtual
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha em baixar dependencias
    pause
    exit /b 1
)

REM Create documents directory
if not exist "documents" (
    echo.
    echo Criando diretorio dos documentos 'documents'...
    mkdir documents
    echo criado diretorio 'documents'
    echo Por favor, coloque seus arquivos em PDF no diretorio 'documents'
)

echo.
echo ============================
echo       Setup Completo!      
echo ============================
echo.
echo Para rodar a aplicacao use:
echo   venv\Scripts\activate.bat
echo   python main.py
echo Ou simplesmente execute o arquivo:
echo   app.bat
echo.
echo Lembre de:
echo 1. Colocar seus arquivos em PDF na pasta 'documents'
echo 2. Conferir se o LM Studio esta rodando com as configuracoes de 'local server' ativadas
echo.
pause