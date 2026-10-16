@echo off
setlocal
cd /d "%~dp0"
start "Mini Puja" /B "%~dp0runtime\pythonw.exe" "%~dp0MiniPuja\mini_puja.py"
