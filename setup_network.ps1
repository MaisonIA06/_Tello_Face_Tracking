# Script PowerShell pour configurer le réseau Docker pour Tello
# À exécuter en tant qu'administrateur
# Usage: .\setup_network.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration du réseau pour Docker Tello" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier les privilèges administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERREUR] Ce script doit être exécuté en tant qu'administrateur!" -ForegroundColor Red
    Write-Host "Clic droit sur PowerShell > Exécuter en tant qu'administrateur" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Ajout des règles de pare-feu pour Docker Tello..." -ForegroundColor Yellow
Write-Host ""

# Règle pour le port 8889 (commandes Tello)
Write-Host "Configuration du port 8889 (commandes Tello)..." -ForegroundColor White
$rule8889 = Get-NetFirewallRule -Name "Docker Tello UDP 8889" -ErrorAction SilentlyContinue
if ($rule8889) {
    Write-Host "  [INFO] Règle 8889 déjà existante" -ForegroundColor Yellow
} else {
    New-NetFirewallRule -DisplayName "Docker Tello UDP 8889" -Name "Docker Tello UDP 8889" -Direction Inbound -Protocol UDP -LocalPort 8889 -Action Allow -ErrorAction SilentlyContinue | Out-Null
    if ($LASTEXITCODE -eq 0 -or $?) {
        Write-Host "  [OK] Port 8889 UDP autorisé" -ForegroundColor Green
    } else {
        # Essayer avec netsh si New-NetFirewallRule échoue
        netsh advfirewall firewall add rule name="Docker Tello UDP 8889" dir=in action=allow protocol=UDP localport=8889 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Port 8889 UDP autorisé (via netsh)" -ForegroundColor Green
        } else {
            Write-Host "  [ERREUR] Impossible d'ajouter la règle 8889" -ForegroundColor Red
        }
    }
}

# Règle pour le port 11111 (flux vidéo et état Tello)
Write-Host "Configuration du port 11111 (flux vidéo et état Tello)..." -ForegroundColor White
$rule11111 = Get-NetFirewallRule -Name "Docker Tello UDP 11111" -ErrorAction SilentlyContinue
if ($rule11111) {
    Write-Host "  [INFO] Règle 11111 déjà existante" -ForegroundColor Yellow
} else {
    New-NetFirewallRule -DisplayName "Docker Tello UDP 11111" -Name "Docker Tello UDP 11111" -Direction Inbound -Protocol UDP -LocalPort 11111 -Action Allow -ErrorAction SilentlyContinue | Out-Null
    if ($LASTEXITCODE -eq 0 -or $?) {
        Write-Host "  [OK] Port 11111 UDP autorisé" -ForegroundColor Green
    } else {
        # Essayer avec netsh si New-NetFirewallRule échoue
        netsh advfirewall firewall add rule name="Docker Tello UDP 11111" dir=in action=allow protocol=UDP localport=11111 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Port 11111 UDP autorisé (via netsh)" -ForegroundColor Green
        } else {
            Write-Host "  [ERREUR] Impossible d'ajouter la règle 11111" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration terminée!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Prochaines étapes:" -ForegroundColor Yellow
Write-Host "1. Assurez-vous d'être connecté au Wi-Fi du Tello" -ForegroundColor White
Write-Host "2. Vérifiez que Docker Desktop est lancé" -ForegroundColor White
Write-Host "3. Dans Docker Desktop: Settings > General > WSL Integration" -ForegroundColor White
Write-Host "   Activez l'intégration WSL2 si disponible" -ForegroundColor White
Write-Host "4. Lancez le conteneur avec run_tello.bat" -ForegroundColor White
Write-Host ""
pause

