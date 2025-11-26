@echo off
setlocal

echo ===================================================
echo    Lancement de Tello Face Tracking via Docker
echo ===================================================

REM Vérifier si Docker est en cours d'exécution
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Docker ne semble pas etre lance.
    echo Veuillez lancer Docker Desktop et reessayer.
    pause
    exit /b 1
)

REM Nom de l'image
set IMAGE_NAME=tello-face-tracking

REM Vérifier si l'image existe, sinon la construire
docker inspect %IMAGE_NAME% >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] L'image %IMAGE_NAME% n'existe pas. Construction en cours...
    echo Cela peut prendre quelques minutes la premiere fois.
    docker build -t %IMAGE_NAME% .
    if %errorlevel% neq 0 (
        echo [ERREUR] La construction de l'image a echoue.
        pause
        exit /b 1
    )
    echo [SUCCES] Image construite avec succes.
) else (
    echo [INFO] L'image %IMAGE_NAME% existe deja.
    set /p REBUILD="Voulez-vous la reconstruire ? (o/N) "
    if /i "%REBUILD%"=="o" (
        docker build -t %IMAGE_NAME% .
        if %errorlevel% neq 0 (
            echo [ERREUR] La reconstruction de l'image a echoue.
            pause
            exit /b 1
        )
    )
)

echo.
echo [IMPORTANT] Assurez-vous que :
echo 1. VcXsrv (XLaunch) est lance avec "Disable access control" coche.
echo 2. Vous etes connecte au Wi-Fi du Tello.
echo 3. Le pare-feu Windows autorise les ports 8889 et 11111 (UDP).
echo.
pause

echo [INFO] Lancement du conteneur...

REM Obtenir l'adresse IP de l'hôte Windows pour DISPLAY
REM Sur Windows, on peut utiliser host.docker.internal ou l'IP de la machine
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set LOCAL_IP=%%a
    goto :found_ip
)
:found_ip
set LOCAL_IP=%LOCAL_IP:~1%

echo [DEBUG] Utilisation de DISPLAY=%LOCAL_IP%:0.0
echo [DEBUG] Si cela ne fonctionne pas, essayez host.docker.internal:0.0

REM Lancement du conteneur avec configuration réseau améliorée pour Windows
REM Important pour Windows :
REM - Utiliser --network bridge (par défaut) mais avec les ports mappés
REM - Ajouter --add-host pour résoudre l'IP du Tello
REM - Mapper les ports UDP en mode publish (pas bind)
REM - Utiliser --privileged peut aider mais n'est pas nécessaire ici

docker run --rm -it ^
    -e DISPLAY=%LOCAL_IP%:0.0 ^
    -e QT_QPA_PLATFORM=xcb ^
    -e QT_X11_NO_MITSHM=1 ^
    --add-host=host.docker.internal:host-gateway ^
    -p 0.0.0.0:8889:8889/udp ^
    -p 0.0.0.0:11111:11111/udp ^
    --name tello-face-tracking-container ^
    %IMAGE_NAME%

set EXIT_CODE=%errorlevel%

if %EXIT_CODE% neq 0 (
    echo.
    echo [ERREUR] Le conteneur s'est arrete avec le code d'erreur: %EXIT_CODE%
    echo.
    echo [DEPANNAGE]
    echo 1. Verifiez que vous etes bien connecte au Wi-Fi du Tello
    echo 2. Verifiez que le pare-feu Windows autorise les ports 8889 et 11111 (UDP)
    echo 3. Essayez de desactiver temporairement le pare-feu pour tester
    echo 4. Verifiez que le drone Tello est allume et pret
    echo.
    echo Pour voir les logs du conteneur:
    echo   docker logs tello-face-tracking-container
)

echo.
echo Fin du programme.
pause
