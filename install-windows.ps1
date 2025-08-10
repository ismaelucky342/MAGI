# MAGI Windows Installer Script
# Ejecuta esto desde PowerShell en la raíz del repositorio MAGI

Write-Host "[MAGI] Instalando dependencias del frontend..." -ForegroundColor Cyan
cd frontend
npm install
npm install --save-dev electron electron-builder concurrently cross-env wait-on

Write-Host "[MAGI] Instalando dependencias del backend..." -ForegroundColor Cyan
cd ../backend
npm install

Write-Host "[MAGI] Instalación completada. Puedes iniciar la app con:" -ForegroundColor Green
Write-Host "    cd frontend; npm run electron:start" -ForegroundColor Yellow
