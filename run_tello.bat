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
docker images %IMAGE_NAME% --format "{{.Repository}}:{{.Tag}}" | findstr /C:"%IMAGE_NAME%:latest" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] L'image %IMAGE_NAME% n'existe pas. Construction en cours...
    echo Cela peut prendre quelques minutes la premiere fois.
    docker build -t %IMAGE_NAME% .
    REM Vérifier si l'image a été créée avec succès
    docker images %IMAGE_NAME% --format "{{.Repository}}:{{.Tag}}" | findstr /C:"%IMAGE_NAME%:latest" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERREUR] La construction de l'image a echoue.
        echo Verifiez les messages d'erreur ci-dessus.
        pause
        exit /b 1
    )
    echo [SUCCES] Image construite avec succes.
) else (
    echo [INFO] L'image %IMAGE_NAME% existe deja.
    set /p REBUILD="Voulez-vous la reconstruire ? (o/N) "
    if /i "%REBUILD%"=="o" (
        docker build -t %IMAGE_NAME% .
        docker images %IMAGE_NAME% --format "{{.Repository}}:{{.Tag}}" | findstr /C:"%IMAGE_NAME%:latest" >nul 2>&1
        if %errorlevel% neq 0 (
            echo [ERREUR] La reconstruction de l'image a echoue.
            echo Verifiez les messages d'erreur ci-dessus.
            pause
            exit /b 1
        )
        echo [SUCCES] Image reconstruite avec succes.
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

REM Vérifier la connectivité avec le Tello
echo [INFO] Verification de la connexion au Tello...
ping -n 1 192.168.10.1 >nul 2>&1
if %errorlevel% neq 0 (
    echo [ATTENTION] Impossible de joindre 192.168.10.1
    echo Assurez-vous d'etre connecte au Wi-Fi du Tello
    pause
)

REM Lancement du conteneur avec configuration réseau améliorée pour Windows
REM Sur Windows avec Docker Desktop, on essaie d'abord --network host (si WSL2 backend)
REM Sinon on utilise le mode bridge avec mapping de ports

REM Vérifier si --network host est supporté (WSL2 backend)
echo [INFO] Test du mode reseau host (WSL2 backend)...
docker run --rm --network host alpine echo "test" >nul 2>&1
set HOST_MODE_AVAILABLE=%errorlevel%

if %HOST_MODE_AVAILABLE% equ 0 (
    echo [INFO] Mode host disponible, utilisation du reseau de l'hote...
    docker run --rm -it ^
        --network host ^
        -e DISPLAY=%LOCAL_IP%:0.0 ^
        -e QT_QPA_PLATFORM=xcb ^
        -e QT_X11_NO_MITSHM=1 ^
        -e PYTHONPATH=/app ^
        --name tello-face-tracking-container ^
        %IMAGE_NAME%
) else (
    echo [INFO] Mode host non disponible, utilisation du mode bridge...
    echo [INFO] Note: Le mode bridge peut avoir des problemes avec UDP sur Windows
    echo [INFO] Assurez-vous d'avoir execute setup_network.ps1 pour configurer le pare-feu
    
    REM Mode bridge avec mapping de ports explicite
    docker run --rm -it ^
        -e DISPLAY=%LOCAL_IP%:0.0 ^
        -e QT_QPA_PLATFORM=xcb ^
        -e QT_X11_NO_MITSHM=1 ^
        -e PYTHONPATH=/app ^
        -p 8889:8889/udp ^
        -p 11111:11111/udp ^
        --name tello-face-tracking-container ^
        %IMAGE_NAME%
)

set EXIT_CODE=%errorlevel%

if %EXIT_CODE% neq 0 (
    echo.
    echo [ERREUR] Le conteneur s'est arrete avec le code d'erreur: %EXIT_CODE%
    echo.
    echo [DEPANNAGE]
    echo 1. Verifiez que vous etes bien connecte au Wi-Fi du Tello (192.168.10.1)
    echo 2. Testez la connexion: ping 192.168.10.1
    echo 3. Verifiez que le pare-feu Windows autorise les ports 8889 et 11111 (UDP)
    echo 4. Dans Docker Desktop: Settings ^> General ^> WSL Integration
    echo    Activez l'integration WSL2 si disponible
    echo 5. Essayez de desactiver temporairement le pare-feu pour tester
    echo 6. Verifiez que le drone Tello est allume et pret
    echo 7. Si le probleme persiste, redemarrez Docker Desktop
    echo.
    echo Pour voir les logs du conteneur:
    echo   docker logs tello-face-tracking-container
)

echo.
echo Fin du programme.
pause