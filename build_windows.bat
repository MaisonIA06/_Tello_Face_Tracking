@echo off
REM Script batch pour builder l'executable Windows facilement
REM Double-cliquez sur ce fichier pour lancer le build

echo.
echo ========================================================================
echo   TELLO FACE TRACKING - BUILD WINDOWS
echo   Script de build automatique
echo ========================================================================
echo.

REM Verification que Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Installez Python depuis : https://www.python.org/downloads/
    echo Assurez-vous de cocher "Add Python to PATH" lors de l'installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python est installe
python --version
echo.

REM Verification de pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] pip n'est pas disponible
    echo.
    pause
    exit /b 1
)

echo [OK] pip est disponible
echo.

REM Demander confirmation
echo Ce script va :
echo   1. Verifier les dependances Python
echo   2. Nettoyer les builds precedents
echo   3. Generer l'executable Windows
echo   4. Creer les fichiers d'instructions
echo.
set /p confirm="Continuer ? (O/N) : "
if /i not "%confirm%"=="O" (
    echo.
    echo Build annule.
    pause
    exit /b 0
)

echo.
echo ========================================================================
echo   LANCEMENT DU BUILD
echo ========================================================================
echo.

REM Lancer le script Python de build
python build_windows.py

REM Verifier le resultat
if errorlevel 1 (
    echo.
    echo ========================================================================
    echo   [ERREUR] Le build a echoue
    echo ========================================================================
    echo.
    echo Consultez les messages d'erreur ci-dessus.
    echo.
    echo Solutions possibles :
    echo   - Installer les dependances : pip install -r requirements.txt
    echo   - Installer PyInstaller : pip install pyinstaller
    echo   - Consulter BUILD_INSTRUCTIONS.md pour plus de details
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo   [SUCCES] Build termine !
echo ========================================================================
echo.
echo L'executable a ete cree dans le dossier dist\
echo.
echo Prochaines etapes :
echo   1. Testez l'executable : dist\TelloFaceTracking.exe
echo   2. Placez yolov8n-face.pt dans dist\ pour tester completement
echo   3. Creez un ZIP du dossier dist\ pour distribution
echo.
echo Fichiers crees :
echo   - dist\TelloFaceTracking.exe
echo   - dist\LISEZMOI.txt
echo   - dist\BUILD_INFO.txt
echo.

REM Demander si on veut ouvrir le dossier dist
set /p opendist="Voulez-vous ouvrir le dossier dist\ ? (O/N) : "
if /i "%opendist%"=="O" (
    explorer dist
)

echo.
echo Merci d'utiliser Tello Face Tracking !
echo.
pause

