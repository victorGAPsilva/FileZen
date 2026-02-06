@echo off
echo ==========================================
echo       Instalador Simples do FileZen
echo ==========================================
echo.
echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python nao encontrado! Por favor, instale o Python 3.
    pause
    exit
) else (
    echo [V] Python detectado.
)

echo.
echo Criando atalho na Area de Trabalho...
set SCRIPT="%TEMP%\CreateShortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\FileZen.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0Iniciar FileZen.bat" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "Iniciar FileZen Organizador" >> %SCRIPT%
echo oLink.IconLocation = "%SystemRoot%\System32\shell32.dll,3" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%
echo [V] Atalho criado.

echo.
echo Tudo pronto! Use o atalho na Area de Trabalho para iniciar.
pause
