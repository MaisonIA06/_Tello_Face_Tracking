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

*   **Pas de vidéo / Pas de connexion au drone** :
    *   Vérifiez que vous êtes bien connecté au Wi-Fi du Tello.
    *   Désactivez temporairement votre pare-feu ou antivirus si les ports UDP 8889 et 11111 sont bloqués.
