@echo off
echo ================================================
echo   FormUL Analyzer — Build
echo ================================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel introuvable (.venv)
    echo Cree-le avec: python -m venv .venv
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo [1/4] Mise a jour de PyInstaller...
pip install pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo [ERREUR] Installation de PyInstaller echouee
    pause
    exit /b 1
)

echo [2/4] Nettoyage des anciens builds...
if exist "dist\FormUL_Analyzer.exe" del /f "dist\FormUL_Analyzer.exe"
if exist "build" rmdir /s /q "build" 2>nul

echo [3/4] Compilation...
pyinstaller --noconfirm --onefile ^
    --name "FormUL_Analyzer" ^
    --add-data "views;views" ^
    --add-data "utils;utils" ^
    --add-data "constants.py;." ^
    --add-data "ui.py;." ^
    --add-data "callbacks.py;." ^
    --add-data "fault_detection.py;." ^
    --add-data "math_channels.py;." ^
    --add-data "config.yaml;." ^
    --hidden-import "asammdf" ^
    --hidden-import "asammdf.blocks" ^
    --hidden-import "asammdf.blocks.mdf_v3" ^
    --hidden-import "asammdf.blocks.mdf_v4" ^
    --hidden-import "plotly" ^
    --hidden-import "plotly.graph_objects" ^
    --hidden-import "plotly.subplots" ^
    --hidden-import "dash" ^
    --hidden-import "dash.dcc" ^
    --hidden-import "dash.html" ^
    --hidden-import "flask" ^
    --hidden-import "pandas" ^
    --hidden-import "numpy" ^
    --hidden-import "yaml" ^
    --hidden-import "webview" ^
    --hidden-import "webview.platforms.winforms" ^
    --hidden-import "clr" ^
    --collect-all "webview" ^
    --collect-all "dash" ^
    --collect-all "plotly" ^
    launcher.py

if errorlevel 1 (
    echo.
    echo [ERREUR] Compilation echouee - verifiez les erreurs ci-dessus
    pause
    exit /b 1
)

echo [4/4] Copie des fichiers de configuration...
if exist "dist\FormUL_Analyzer.exe" (
    copy /y config.yaml dist\config.yaml >nul
    if not exist "dist\layouts" mkdir dist\layouts
    echo.
    echo ================================================
    echo   Build reussi !
    echo   Executable: dist\FormUL_Analyzer.exe
    echo ================================================
) else (
    echo [ERREUR] Executable introuvable apres compilation
    pause
    exit /b 1
)

echo.
pause
