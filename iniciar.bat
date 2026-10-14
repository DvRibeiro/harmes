@echo off
setlocal
title HERMES - AI Orchestrator Companion
cd /d "%~dp0"

:: 1. Verificar se a venv existe. Se nao existir, criar e instalar dependencias.
if not exist "venv\Scripts\activate.bat" (
    echo ========================================================
    echo  [HERMES] Ambiente virtual nao encontrado.
    echo  Criando ambiente virtual em .\venv ...
    echo ========================================================
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo [ERRO] Falha ao criar a venv.
        echo Verifique se o Python esta instalado e disponivel no PATH do sistema.
        pause
        exit /b 1
    )

    echo.
    echo ========================================================
    echo  [HERMES] Ativando venv e instalando requirements.txt ...
    echo ========================================================
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERRO] Falha ao instalar as dependencias.
        pause
        exit /b 1
    )
    echo.
    echo [HERMES] Ambiente virtual configurado com sucesso!
    echo ========================================================
    echo.
) else (
    :: 2. Se a venv ja existir, apenas ativa
    call venv\Scripts\activate.bat
)

:: 3. Executar o assistente
echo [HERMES] Iniciando o assistente...
python main.py

if errorlevel 1 (
    echo.
    echo [HERMES] O assistente foi encerrado com erro.
    pause
)
