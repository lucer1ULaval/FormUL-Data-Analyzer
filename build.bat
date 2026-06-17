@echo off
echo === FormUL Analyzer - Build ===
echo.

cd /d "%~dp0"

call .venv\Scripts\activate.bat

echo Installation de PyInstaller...
pip install pyinstaller --quiet

echo.
echo Compilation...
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
    launcher.py

echo.
if exist "dist\FormUL_Analyzer.exe" (
    echo Copie des fichiers de configuration...
    copy config.yaml dist\config.yaml
    mkdir dist\layouts 2>nul
    echo.
    echo === Build reussi ===
    echo Executable: dist\FormUL_Analyzer.exe
) else (
    echo === ERREUR - Build echoue ===
)
pause