@echo off
setlocal
cd /d "%~dp0"
rem Verifica se o interpretador realmente inicia, nao apenas se o launcher existe.
set "VIGENERE_CHECK=import sys; sys.exit(20) if sys.version_info < (3, 9) else None; import importlib.util; sys.exit(0 if importlib.util.find_spec('venv') else 21)"
set "VIGENERE_ENCONTRADO=0"
set "VIGENERE_ANTIGO=0"
set "VIGENERE_SEM_VENV=0"

where py >nul 2>nul
if errorlevel 1 goto :testar_python
set "VIGENERE_ENCONTRADO=1"
py -3 -c "%VIGENERE_CHECK%" >nul 2>nul
if not errorlevel 1 goto :executar_py
call :registrar_falha

:testar_python
where python >nul 2>nul
if errorlevel 1 goto :testar_python3
set "VIGENERE_ENCONTRADO=1"
python -c "%VIGENERE_CHECK%" >nul 2>nul
if not errorlevel 1 goto :executar_python
call :registrar_falha

:testar_python3
where python3 >nul 2>nul
if errorlevel 1 goto :testar_versoes
set "VIGENERE_ENCONTRADO=1"
python3 -c "%VIGENERE_CHECK%" >nul 2>nul
if not errorlevel 1 goto :executar_python3
call :registrar_falha

:testar_versoes
rem O padrao do py pode estar quebrado mesmo com outra versao instalada.
where py >nul 2>nul
if errorlevel 1 goto :sem_python
for %%V in (14 13 12 11 10 9) do (
    py -3.%%V -c "%VIGENERE_CHECK%" >nul 2>nul
    if not errorlevel 1 (
        set "VIGENERE_VERSION=3.%%V"
        goto :executar_versao
    )
    call :registrar_falha
)
goto :sem_python

:executar_py
py -3 instalar.py %*
goto :terminar

:executar_python
python instalar.py %*
goto :terminar

:executar_python3
python3 instalar.py %*
goto :terminar

:executar_versao
py -%VIGENERE_VERSION% instalar.py %*
goto :terminar

:sem_python
echo.
echo NAO FOI POSSIVEL INICIAR O PROGRAMA
echo Requisito: Python 3.9 ou superior.
echo.
if "%VIGENERE_SEM_VENV%"=="1" goto :erro_venv
if "%VIGENERE_ANTIGO%"=="1" goto :erro_versao
if "%VIGENERE_ENCONTRADO%"=="1" goto :erro_instalacao
echo Erro: Python nao foi encontrado nos comandos py, python ou python3.
echo Solucao: instale Python 3.9 ou superior e marque Add Python to PATH.
goto :orientar

:erro_versao
echo Erro: foi encontrado um Python anterior a versao 3.9.
echo Nenhuma instalacao compativel funcionou nos comandos testados.
echo Solucao: instale Python 3.9 ou superior e marque Add Python to PATH.
goto :orientar

:erro_venv
echo Erro: o Python iniciou, mas o componente venv nao esta disponivel.
echo Solucao: repare ou reinstale o Python com os componentes padrao.
goto :orientar

:erro_instalacao
echo Erro: o comando do Python existe, mas nao conseguiu iniciar o Python.
echo Isso pode ocorrer quando aponta para um arquivo removido, como
echo C:\Python314\python.exe - erro Unable to create process.
echo Solucao: repare ou reinstale Python 3.9 ou superior.
echo Marque Add Python to PATH durante a instalacao.
goto :orientar

:orientar
echo.
echo Download: https://www.python.org/downloads/windows/
echo Apos corrigir, feche este terminal e execute o instalador novamente.
pause
exit /b 1

:registrar_falha
set "VIGENERE_CODIGO=%errorlevel%"
if "%VIGENERE_CODIGO%"=="20" set "VIGENERE_ANTIGO=1"
if "%VIGENERE_CODIGO%"=="21" set "VIGENERE_SEM_VENV=1"
exit /b 1

:terminar
if errorlevel 1 (
    echo.
    echo O Python iniciou, mas a preparacao do programa falhou. Confira o erro acima.
    pause
    exit /b 1
)
exit /b 0
