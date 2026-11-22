@echo off
rem notapad - avvia l app di prova in locale (serve Python) e la apre in Edge
cd /d "%~dp0"
start "" msedge http://localhost:8787/
python -m http.server 8787 --bind 127.0.0.1
