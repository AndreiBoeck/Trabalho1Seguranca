@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 instalar.py %*
    goto :terminar
)
where python >nul 2>nul
if not errorlevel 1 (
    python instalar.py %*
    goto :terminar
)
echo Instale Python 3.9 ou superior em https://www.python.org/downloads/
echo Marque a opcao Add Python to PATH durante a instalacao.
pause
exit /b 1
:terminar
if errorlevel 1 (
    pause
    exit /b 1
)
exit /b 0
