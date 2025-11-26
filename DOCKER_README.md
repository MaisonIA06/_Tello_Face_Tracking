# Guide d'installation et d'utilisation - Tello Face Tracking (Docker)

Ce guide vous explique comment lancer l'application de tracking de visage pour drone Tello en utilisant Docker sous Windows.

## Prérequis

1.  **Docker Desktop** : Doit être installé et lancé.
    *   Téléchargement : [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2.  **VcXsrv (Serveur X)** : Nécessaire pour afficher l'interface graphique depuis Docker.
    *   Téléchargement : [https://sourceforge.net/projects/vcxsrv/](https://sourceforge.net/projects/vcxsrv/)

## Configuration Initiale (À faire une seule fois)

### 1. Configurer VcXsrv (XLaunch)
Pour que la fenêtre vidéo s'affiche sur votre Windows :
1.  Lancez **XLaunch** depuis le menu Démarrer.
2.  Sur la première page ("Display settings"), laissez les choix par défaut et cliquez sur **Suivant**.
3.  Sur la deuxième page ("Client startup"), laissez "Start no client" et cliquez sur **Suivant**.
4.  Sur la troisième page ("Extra settings") :
    *   **Cochez** la case **"Disable access control"** (Très important !).
    *   Cliquez sur **Suivant**.
5.  Cliquez sur **Terminer**.
    *   *Astuce : Vous pouvez sauvegarder cette configuration ("Save configuration") pour la relancer rapidement plus tard.*

### 2. Configurer le réseau Docker (Recommandé)
Pour que Docker puisse communiquer avec le drone Tello via UDP :
1.  Ouvrez **PowerShell en tant qu'administrateur** (clic droit > Exécuter en tant qu'administrateur).
2.  Naviguez vers le dossier du projet.
3.  Exécutez : `.\setup_network.ps1`
4.  Ce script configure automatiquement le pare-feu Windows pour autoriser les ports UDP nécessaires (8889 et 11111).

**Alternative manuelle** : Si le script ne fonctionne pas, ajoutez manuellement dans le Pare-feu Windows :
- Port 8889 (UDP) - Commandes Tello
- Port 11111 (UDP) - Flux vidéo et état Tello

### 3. Configurer Docker Desktop (Optionnel mais recommandé)
Pour améliorer les performances réseau avec Docker sur Windows :
1.  Ouvrez **Docker Desktop**.
2.  Allez dans **Settings** > **General** > **WSL Integration**.
3.  Activez l'intégration WSL2 si disponible.
4.  Cela permet d'utiliser le mode `--network host` qui fonctionne mieux avec UDP.

## Utilisation Quotidienne

1.  **Allumez votre drone Tello**.
2.  Connectez votre PC au **réseau Wi-Fi du Tello** (ex: `TELLO-XXXXXX`).
3.  Assurez-vous que **Docker Desktop** est lancé.
4.  Assurez-vous que **XLaunch** est lancé (voir ci-dessus).
5.  Double-cliquez sur le fichier **`run_tello.bat`**.

Le script va :
*   Construire l'image Docker (la première fois seulement).
*   Lancer l'application.
*   Se connecter au drone et afficher la vidéo.

## Dépannage

*   **Erreur "Can't connect to X11 window server"** :
    *   Vérifiez que XLaunch est bien lancé.
    *   Vérifiez que "Disable access control" a bien été coché dans XLaunch.
    *   Vérifiez que votre pare-feu Windows autorise VcXsrv.

*   **Erreur "Did not receive a state packet from the Tello"** :
    *   **C'est le problème le plus courant sur Windows avec Docker.**
    *   Vérifiez que vous êtes bien connecté au Wi-Fi du Tello (testez avec `ping 192.168.10.1`).
    *   Exécutez `setup_network.ps1` en tant qu'administrateur pour configurer le pare-feu.
    *   Dans Docker Desktop, activez l'intégration WSL2 (Settings > General > WSL Integration).
    *   Le script `run_tello.bat` essaie automatiquement le mode `--network host` si disponible.
    *   Si le problème persiste, redémarrez Docker Desktop.
    *   Vérifiez que le drone Tello est allumé et prêt.

*   **Pas de vidéo / Pas de connexion au drone** :
    *   Vérifiez que vous êtes bien connecté au Wi-Fi du Tello.
    *   Vérifiez que les ports UDP 8889 et 11111 sont autorisés dans le pare-feu Windows.
    *   Testez la connectivité : `ping 192.168.10.1`

*   **Erreur "PYTHONPATH not found"** :
    *   Reconstruisez l'image Docker : `docker build -t tello-face-tracking .`
    *   Le Dockerfile a été corrigé pour définir correctement PYTHONPATH.

*   **Problèmes généraux** :
    *   Vérifiez les logs du conteneur : `docker logs tello-face-tracking-container`
    *   Redémarrez Docker Desktop si les problèmes persistent.
    *   Assurez-vous que Docker Desktop est à jour.
