# Face Tracking avec Drone DJI Tello

Ce script permet de faire du face tracking automatique avec un drone DJI Tello en utilisant le modèle YOLO-face pour détecter les visages et ajuster la position du drone pour garder le visage au centre de l'image.

## 📋 Prérequis

- Un drone DJI Tello
- Un ordinateur portable avec Python 3.7-3.11
- Connexion WiFi pour le drone Tello
- Le modèle `yolov8n-face.pt` dans le répertoire du projet

## 🚀 Installation

### 1. Installation des dépendances Python

```bash
# Installer les dépendances de base du projet YOLO-face
pip install -r requirements.txt

# Installer les dépendances spécifiques pour le Tello
pip install -r requirements_tello.txt
```

**Note importante pour PyTorch (CPU uniquement):**

Si vous n'avez pas de GPU, installez PyTorch en version CPU uniquement pour réduire la taille et améliorer les performances:

```bash
# Pour Linux/Mac
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Pour Windows
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 2. Vérification du modèle YOLO-face

Assurez-vous que le fichier `yolov8n-face.pt` est présent dans le répertoire du projet. Si ce n'est pas le cas, téléchargez-le depuis les releases du projet ou utilisez un autre modèle YOLO-face disponible.

## 📱 Configuration du Drone Tello

### 1. Connexion WiFi (Automatique)

**✨ Nouvelle fonctionnalité :** Le script gère maintenant automatiquement la connexion WiFi au drone Tello !

Le script peut :
- Détecter automatiquement le réseau WiFi du Tello
- Se connecter automatiquement au réseau
- Restaurer votre connexion WiFi précédente après utilisation

**Prérequis pour la gestion automatique :**
- NetworkManager doit être installé (généralement déjà présent sur Linux)
- Si ce n'est pas le cas : `sudo apt-get install network-manager`

**Utilisation :**

1. **Mode automatique (par défaut)** : Le script se connecte automatiquement au réseau Tello
   ```bash
   python tello_face_tracking.py
   ```

2. **Désactiver la gestion automatique** : Si vous préférez vous connecter manuellement
   ```bash
   python tello_face_tracking.py --no-auto-wifi
   ```

3. **Spécifier le SSID du Tello** : Si vous connaissez le nom exact du réseau
   ```bash
   python tello_face_tracking.py --tello-ssid "TELLO-XXXXXX"
   ```

**Note :** Si la connexion automatique échoue, le script vous demandera si vous souhaitez continuer (utile si vous êtes déjà connecté manuellement).

### 2. Vérification de la batterie

Assurez-vous que la batterie du drone est suffisamment chargée (recommandé: >50%). Le script affichera le niveau de batterie au démarrage.

## 🎮 Utilisation

### Test de connexion (recommandé avant le tracking)

Avant de lancer le tracking, testez la connexion au drone:

```bash
python test_tello_connection.py
```

Ce script vérifie:
- La connexion au drone
- Le niveau de batterie
- Le flux vidéo

Appuyez sur `q` pour quitter le test.

### Lancement du script de tracking

**Utilisation de base :**
```bash
python tello_face_tracking.py
```

**Options disponibles :**

```bash
# Spécifier un modèle personnalisé
python tello_face_tracking.py --model yolov11n-face.pt

# Ajuster le seuil de confiance
python tello_face_tracking.py --conf 0.3

# Désactiver la gestion Wi-Fi automatique
python tello_face_tracking.py --no-auto-wifi

# Spécifier le SSID du Tello
python tello_face_tracking.py --tello-ssid "TELLO-XXXXXX"

# Combinaison d'options
python tello_face_tracking.py --model yolov11n-face.pt --conf 0.3
```

**Aide complète :**
```bash
python tello_face_tracking.py --help
```

### Contrôles

Une fois le script lancé, vous pouvez utiliser les touches suivantes:

- **`t`** : Décoller / Atterrir
- **`q`** : Quitter le programme
- **`w`** : Avancer (contrôle manuel)
- **`s`** : Reculer (contrôle manuel)
- **`a`** : Aller à gauche (contrôle manuel)
- **`d`** : Aller à droite (contrôle manuel)

### Fonctionnement

1. **Décollage**: Appuyez sur `t` pour faire décoller le drone
2. **Détection**: Le script détecte automatiquement les visages dans le flux vidéo
3. **Tracking**: Le drone ajuste automatiquement sa position pour garder le visage au centre
4. **Atterrissage**: Appuyez sur `t` à nouveau pour atterrir, ou le drone atterrira automatiquement si aucun visage n'est détecté pendant 30 frames

## ⚙️ Paramètres de configuration

Vous pouvez modifier les paramètres dans le script `tello_face_tracking.py`:

### Paramètres PID (lignes ~81-84)

```python
self.kp_x = 0.5    # Gain proportionnel horizontal (yaw) - augmenter = plus réactif
self.kp_y = 0.3    # Gain proportionnel vertical
self.kd_x = 0.15   # Gain dérivé horizontal (réduit les oscillations)
self.kd_y = 0.1    # Gain dérivé vertical
```

### Vitesse maximale (lignes ~91-92)

```python
self.max_speed_yaw = 50      # Vitesse maximale de rotation en deg/s
self.max_speed_vertical = 30  # Vitesse maximale verticale en cm/s
```

### Zone morte (ligne ~71)

```python
self.dead_zone = 20  # Zone morte en pixels (évite les micro-mouvements)
```

### Seuil de confiance (dans `main()`)

```python
tracker = FaceTracker(model_path=model_path, conf_threshold=0.25)
```

## 🔧 Dépannage

### Le drone ne se connecte pas

**Problèmes de connexion Wi-Fi automatique :**

1. **NetworkManager non disponible**
   ```bash
   sudo apt-get install network-manager
   ```

2. **Le réseau Tello n'est pas détecté**
   - Assurez-vous que le drone est allumé et en mode Wi-Fi
   - Vérifiez que le drone est à proximité (moins de 10 mètres)
   - Essayez de spécifier manuellement le SSID : `--tello-ssid "TELLO-XXXXXX"`
   - Désactivez la gestion automatique : `--no-auto-wifi` et connectez-vous manuellement

3. **Permissions insuffisantes**
   - La gestion Wi-Fi nécessite parfois des permissions système
   - Si cela échoue, utilisez `--no-auto-wifi` et connectez-vous manuellement

**Problèmes généraux :**

- Vérifiez que vous êtes bien connecté au WiFi du Tello
- Assurez-vous que le drone est allumé et que les LED clignotent
- Essayez de redémarrer le drone et votre ordinateur
- Vérifiez que le firewall ne bloque pas la communication avec le drone

### Détection de visage instable

- Ajustez les paramètres PID (réduire `kp_x` et `kp_y` pour plus de stabilité)
- Augmentez la `dead_zone` pour éviter les micro-mouvements
- Vérifiez l'éclairage de la pièce

### Performance faible (FPS bas)

- Réduisez la taille de l'image dans le code (ajoutez un `cv2.resize()`)
- Utilisez un modèle plus petit (yolov8n au lieu de yolov11s)
- Fermez les autres applications qui utilisent le CPU

### Erreur "Module not found"

Assurez-vous d'avoir installé toutes les dépendances:

```bash
pip install -r requirements.txt
pip install -r requirements_tello.txt
```

## 📝 Notes importantes

- **Sécurité**: Assurez-vous d'avoir suffisamment d'espace libre autour du drone
- **Batterie**: Surveillez le niveau de batterie affiché à l'écran
- **Stabilité**: Le tracking fonctionne mieux avec un bon éclairage et un fond contrasté
- **Latence**: Il peut y avoir un léger délai entre la détection et le mouvement du drone

## 🎯 Améliorations possibles

- Ajout d'un contrôle de la distance (altitude) basé sur la taille du visage
- Implémentation d'un filtre de Kalman pour un tracking plus fluide
- Support de plusieurs visages avec sélection du plus proche
- Enregistrement vidéo du tracking
- Interface graphique pour ajuster les paramètres en temps réel

## 📄 Licence

Ce script utilise le projet YOLO-face qui est sous licence GPL-3.0.

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou une pull request.

