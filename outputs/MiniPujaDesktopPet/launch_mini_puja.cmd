@echo off
setlocal
set "HERE=%~dp0"
set "BUNDLED_PY=C:\Users\admi\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%BUNDLED_PY%" (
  start "Mini Puja" /B "%BUNDLED_PY%" "%HERE%mini_puja.py"
) else (
  start "Mini Puja" /B py -3 "%HERE%mini_puja.py"
)
