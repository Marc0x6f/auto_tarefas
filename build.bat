@echo off
echo Finalizando qualquer .exe aberto...
taskkill /F /IM LancaNotas.exe >nul 2>&1
taskkill /F /IM app_gui.exe >nul 2>&1

echo Limpando arquivos antigos...
rmdir /s /q dist
rmdir /s /q build
del *.spec

echo Compilando .exe novamente...
python -m PyInstaller ^
  --name "LancaNotas" ^
  --onefile ^
  --noconsole ^
  --icon=icone.ico ^
  --collect-all pandas ^
  --collect-all selenium ^
  --hidden-import psutil ^
  --hidden-import unicodedata ^
  --hidden-import selenium.webdriver.chrome.webdriver ^
  --hidden-import selenium.webdriver.chrome.options ^
  --hidden-import selenium.webdriver.chrome.service ^
  --hidden-import selenium.webdriver.common.by ^
  --hidden-import selenium.webdriver.support.ui ^
  --hidden-import selenium.webdriver.support.expected_conditions ^
  --hidden-import selenium.webdriver.remote.webdriver ^
  --hidden-import selenium.webdriver.remote.webelement ^
  app_gui.py

echo.
echo ✅ Se não deu erro acima, o build foi feito com sucesso.
pause
