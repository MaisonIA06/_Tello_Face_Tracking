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
    )
)

echo.
echo [IMPORTANT] Assurez-vous que :
echo 1. VcXsrv (XLaunch) est lance avec "Disable access control" coche.
echo 2. Vous etes connecte au Wi-Fi du Tello.
echo.
pause

echo [INFO] Lancement du conteneur...

REM Lancement du conteneur
REM --rm : supprime le conteneur après l'arrêt
REM -it : mode interactif
REM --net=host : utilise le réseau de l'hôte (souvent nécessaire pour le drone, mais ne fonctionne pas toujours bien sur Windows/Mac)
REM Alternative : mapping de ports UDP
REM 8889 : Commandes Tello
REM 11111 : Flux vidéo Tello
REM DISPLAY=host.docker.internal:0.0 : Pour l'affichage X11 sur Windows

docker run --rm -it ^
    -e DISPLAY=host.docker.internal:0.0 ^
    -p 8889:8889/udp ^
    -p 11111:11111/udp ^
    %IMAGE_NAME%

if %errorlevel% neq 0 (
    echo [ERREUR] Une erreur est survenue lors de l'execution.
)

echo.
echo Fin du programme.
pause
