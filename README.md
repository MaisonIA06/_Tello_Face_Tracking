# 🚁 Tello Face Tracking

[![Python](https://img.shields.io/badge/Python-3.7--3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL--3.0-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey.svg)]()

Application de suivi de visage automatique pour le drone DJI Tello utilisant YOLO pour détecter et suivre les visages en temps réel.

## 📖 Description

Tello Face Tracking est une application multiplateforme qui permet de contrôler automatiquement un drone DJI Tello pour suivre un visage. L'application utilise le modèle YOLO-face pour détecter les visages dans le flux vidéo du drone et ajuste automatiquement la position du drone pour maintenir le visage au centre de l'image.

### ✨ Fonctionnalités principales

- 🎯 **Détection de visage en temps réel** avec YOLO
- 🚁 **Contrôle automatique du drone** pour suivre le visage
- 🖥️ **Interface graphique moderne** (PyQt6) pour un contrôle facile
- 🔄 **Gestion WiFi automatique** sous Linux (connexion/restauration)
- ⚙️ **Paramètres ajustables** (PID, vitesse, zone morte)
- 📊 **Affichage en temps réel** des informations (FPS, batterie, hauteur)
- 🎮 **Contrôles manuels** optionnels (avancer, reculer, rotation)
- 🪟 **Support Windows** avec exécutable prêt à l'emploi

## 🎬 Captures d'écran

> *Note : Ajoutez vos captures d'écran ici*

## 📋 Prérequis

### Matériel
- Un drone DJI Tello
- Ordinateur avec connexion WiFi
- Batterie du Tello chargée (>50% recommandé)

### Logiciel

#### Linux
- Python 3.7-3.11
- NetworkManager (pour la gestion WiFi automatique)
- Le modèle `yolov8n-face.pt`

#### Windows
- Windows 7, 8, 10 ou 11
- Exécutable Windows (téléchargeable depuis les [releases](../../releases))
- Le modèle `yolov8n-face.pt`

## 🚀 Installation rapide

### Linux (développement)

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-repo/yolo-face.git
   cd yolo-face
   ```

2. **Créer un environnement virtuel** (recommandé)
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Télécharger le modèle YOLO**
   - Placez `yolov8n-face.pt` dans le répertoire du projet
   - Ou téléchargez-le depuis les releases

### Windows (utilisateur final)

1. **Télécharger la release**
   - Allez sur la [page des releases](../../releases)
   - Téléchargez `TelloFaceTracking-v1.0-Windows-x64.zip`

2. **Extraire l'archive**
   - Extrayez le contenu dans un dossier de votre choix

3. **Placer le modèle YOLO**
   - Téléchargez `yolov8n-face.pt` (si non inclus)
   - Placez-le dans le même dossier que `TelloFaceTracking.exe`

4. **C'est prêt !** Consultez [README_WINDOWS.md](README_WINDOWS.md) pour les instructions détaillées.

## 🎮 Utilisation

### Linux

#### Interface graphique (recommandé)
```bash
python run_gui.py
```

#### Ligne de commande
```bash
python tello_face_tracking.py
```

**Options disponibles :**
```bash
# Spécifier un modèle personnalisé
python tello_face_tracking.py --model yolov8n-face.pt

# Ajuster le seuil de confiance
python tello_face_tracking.py --conf 0.3

# Désactiver la gestion Wi-Fi automatique
python tello_face_tracking.py --no-auto-wifi

# Spécifier le SSID du Tello
python tello_face_tracking.py --tello-ssid "TELLO-XXXXXX"
```

### Windows

1. **Connecter au WiFi du Tello**
   - Allumez le drone Tello
   - Connectez-vous au réseau WiFi `TELLO-XXXXXX` depuis Windows

2. **Lancer l'application**
   - Double-cliquez sur `TelloFaceTracking.exe`
   - L'interface graphique s'ouvre automatiquement

3. **Utiliser l'application**
   - Cliquez sur "Initialiser" pour connecter au drone
   - Cliquez sur "Décoller" pour faire décoller le drone
   - Le tracking démarre automatiquement

> 📖 **Guide complet Windows** : Consultez [README_WINDOWS.md](README_WINDOWS.md) pour des instructions détaillées.

### Contrôles clavier (mode CLI)

- **`t`** : Décoller / Atterrir
- **`q`** : Quitter le programme
- **`w`** / **`s`** : Avancer / Reculer (contrôle manuel)
- **`a`** / **`d`** : Aller à gauche / droite (contrôle manuel)

## ⚙️ Configuration

### Paramètres PID

Vous pouvez ajuster les paramètres de contrôle dans `tello_face_tracking.py` :

```python
self.kp_x = 0.15   # Gain proportionnel horizontal
self.kp_y = 0.12   # Gain proportionnel vertical
self.kd_x = 0.25   # Gain dérivé horizontal (réduit les oscillations)
self.kd_y = 0.2    # Gain dérivé vertical
```

### Vitesse maximale

```python
self.max_speed_yaw = 30      # deg/s pour la rotation
self.max_speed_vertical = 30  # cm/s pour le mouvement vertical
```

### Zone morte

```python
self.dead_zone = 40  # pixels (évite les micro-mouvements)
```

## 🔧 Dépannage

### Problèmes courants

#### Le drone ne se connecte pas
- **Linux** : Vérifiez que NetworkManager est installé (`sudo apt-get install network-manager`)
- **Windows** : Connectez-vous manuellement au WiFi du Tello avant de lancer l'application
- Vérifiez que le drone est allumé et à proximité (< 10 mètres)

#### Détection de visage instable
- Ajustez les paramètres PID (réduire `kp_x` et `kp_y` pour plus de stabilité)
- Augmentez la `dead_zone` pour éviter les micro-mouvements
- Vérifiez l'éclairage de la pièce

#### Performance faible (FPS bas)
- Réduisez la résolution de détection dans le code
- Utilisez un modèle plus petit (yolov8n)
- Fermez les autres applications

> 📖 **Dépannage détaillé** : Consultez [README_WINDOWS.md](README_WINDOWS.md) pour plus de solutions.

## 📚 Documentation

- **[README_WINDOWS.md](README_WINDOWS.md)** - Guide complet pour utilisateurs Windows
- **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)** - Guide de build pour développeurs
- **[CHANGELOG.md](CHANGELOG.md)** - Historique des versions

## 🛠️ Développement

### Build pour Windows

Pour créer l'exécutable Windows :

```bash
python build_windows.py
```

L'exécutable sera créé dans `dist/TelloFaceTracking.exe`.

> 📖 **Instructions détaillées** : Consultez [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md).

### Structure du projet

```
yolo-face/
├── tello_face_tracking.py    # Script principal
├── run_gui.py                 # Point d'entrée GUI
├── build_windows.py           # Script de build Windows
├── requirements.txt           # Dépendances Python
├── gui/                       # Interface graphique
│   ├── tello_gui.py
│   └── components/
└── ultralytics/               # Module YOLO
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Guidelines

- Suivez le style de code existant
- Ajoutez des tests si possible
- Mettez à jour la documentation si nécessaire
- Respectez le [Semantic Versioning](https://semver.org/)

## 📄 Licence

Ce projet est sous licence GPL-3.0. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **[Ultralytics](https://github.com/ultralytics/ultralytics)** - YOLO et modèle de détection
- **[djitellopy](https://github.com/damiafuentes/DJITelloPy)** - Bibliothèque de contrôle Tello
- **[PyInstaller](https://www.pyinstaller.org/)** - Création d'exécutables
- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)** - Interface graphique

## 📞 Support

- 🐛 **Signaler un bug** : [Ouvrir une issue](../../issues)
- 💡 **Suggérer une fonctionnalité** : [Ouvrir une issue](../../issues)
- 📖 **Documentation** : Consultez les fichiers README dans le dépôt

---

**Fait avec ❤️ pour la communauté drone**
