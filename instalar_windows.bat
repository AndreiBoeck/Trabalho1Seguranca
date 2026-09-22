@echo off
setlocal
cd /d "%~dp0"
rem Verifica se o interpretador realmente inicia, nao apenas se o launcher existe.
set "VIGENERE_CHECK=import sys, venv; sys.exit(0 if sys.version_info >= (3, 9) else 1)"

where py >nul 2>nul
if errorlevel 1 goto :testar_python
py -3 -c "%VIGENERE_CHECK%" >nul 2>nul
if not errorlevel 1 goto :executar_py

:testar_python
where python >nul 2>nul
if errorlevel 1 goto :testar_python3
python -c "%VIGENERE_CHECK%" >nul 2>nul
if not errorlevel 1 goto :executar_python

:testar_python3
where python3 >nul 2>nul
if errorlevel 1 goto :testar_versoes
python3 -c "%VIGENERE_CHECK%" >nul 2>nul
if not errorlevel 1 goto :executar_python3

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
echo Nao foi encontrado um Python 3.9 ou superior funcionando.
echo O launcher pode apontar para uma instalacao removida ou incompleta.
echo Instale ou repare o Python em https://www.python.org/downloads/windows/
echo Marque Add Python to PATH e depois execute este arquivo novamente.
pause
exit /b 1

:terminar
if errorlevel 1 (
    echo.
    echo O Python iniciou, mas a preparacao do programa falhou. Confira o erro acima.
    pause
    exit /b 1
)
exit /b 0
