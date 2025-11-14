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

### 1. Connexion WiFi

1. Allumez le drone Tello
2. Connectez votre ordinateur au réseau WiFi du Tello (généralement nommé "TELLO-XXXXXX")
3. Attendez que la connexion soit établie

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

```bash
python tello_face_tracking.py
```

Ou avec un modèle personnalisé:

```bash
python tello_face_tracking.py yolov11n-face.pt
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

- Vérifiez que vous êtes bien connecté au WiFi du Tello
- Assurez-vous que le drone est allumé et que les LED clignotent
- Essayez de redémarrer le drone et votre ordinateur

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

