@echo off
title FileZen Launcher
echo Iniciando FileZen...
if not exist "logs" mkdir logs
start "" pythonw src/main.py
echo FileZen esta rodando em segundo plano.
echo Verifique a pasta 'logs' para detalhes.
timeout /t 3
exit
