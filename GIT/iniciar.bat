@echo off
cd /d "%~dp0"
if not exist .env (
  echo Configure o arquivo .env a partir de .env.example. Consulte README.md.
  pause
  exit /b 1
)
if not exist data\IOT-temp.csv (
  echo Baixe IOT-temp.csv do Kaggle e coloque na pasta data. Consulte README.md.
  pause
  exit /b 1
)
docker compose up -d --build
if errorlevel 1 (
  echo Verifique se Docker Desktop esta iniciado. Consulte README.md.
  pause
  exit /b 1
)
echo Aguarde a importacao terminar. Dashboard: http://localhost:8501
pause
