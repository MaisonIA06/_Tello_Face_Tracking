# Interface Graphique - Tello Face Tracking

Interface graphique PyQt6 pour le programme de tracking de visage avec le drone DJI Tello.

## Installation

Assurez-vous que PyQt6 est installé :

```bash
pip install PyQt6
```

Ou installez toutes les dépendances :

```bash
pip install -r requirements.txt
```

## Utilisation

### Lancement de l'interface graphique

Plusieurs méthodes pour lancer l'interface :

1. **Script de lancement dédié** :
   ```bash
   python run_gui.py
   ```

2. **Via le script principal avec l'option --gui** :
   ```bash
   python tello_face_tracking.py --gui
   ```

3. **Lancement automatique** (si PyQt6 est disponible) :
   ```bash
   python tello_face_tracking.py
   ```

4. **Forcer le mode CLI** :
   ```bash
   python tello_face_tracking.py --cli
   ```

## Fonctionnalités

### Panneau de Configuration

- **Modèle YOLO** : Sélection du fichier modèle (.pt) via un dialogue de fichier
- **Seuil de confiance** : Slider pour ajuster le seuil de détection (0.0 - 1.0)
- **Configuration Wi-Fi** :
  - Option de connexion automatique au réseau Tello
  - Champ pour spécifier manuellement le SSID du réseau Tello

### Panneau de Contrôle

- **Indicateur d'état** : LED visuelle (vert = en vol, rouge = au sol)
- **Bouton Décollage/Atterrissage** : Contrôle du drone
- **Bouton Arrêt d'urgence** : Arrêt immédiat et atterrissage du drone

### Panneau Paramètres Avancés

- **Paramètres PID** :
  - `kp_x`, `kp_y` : Gains proportionnels (horizontal et vertical)
  - `kd_x`, `kd_y` : Gains dérivés (horizontal et vertical)
- **Vitesses maximales** :
  - Rotation (deg/s)
  - Vertical (cm/s)
  - Latéral (cm/s)
  - Avant/Arrière (cm/s)
- **Autres paramètres** :
  - Zone morte (pixels)
  - Taille cible du visage (pixels)
- **Bouton de réinitialisation** : Restaure les valeurs par défaut

### Panneau Statistiques

Affichage en temps réel de :
- **Batterie** : Niveau avec barre de progression
- **FPS** : Images par seconde
- **Détection** :
  - Statut (visage détecté/non détecté)
  - Taille du visage (pixels)
  - Confiance de la détection
- **Vitesses de contrôle** :
  - Gauche/Droite (cm/s)
  - Avant/Arrière (cm/s)
  - Monter/Descendre (cm/s)
  - Rotation (deg/s)

### Panneau Logs

- Affichage des messages système avec horodatage
- Niveaux de log : Info, Warning, Error
- Bouton pour effacer les logs

### Zone d'affichage vidéo

- Affichage en temps réel du flux vidéo du drone
- Overlay avec les informations de tracking (détection, vitesses, etc.)

## Structure des fichiers

```
gui/
├── __init__.py
├── tello_gui.py          # Interface graphique principale
├── components/
│   ├── __init__.py
│   └── tracking_thread.py # Thread de tracking
└── README.md             # Ce fichier
```

## Notes techniques

- L'interface utilise **QThread** pour exécuter la boucle de tracking dans un thread séparé
- Communication thread-safe via les **signaux/slots** de PyQt6
- Conversion automatique des frames OpenCV (BGR) vers QImage (RGB) pour l'affichage
- Le mode GUI désactive les prompts interactifs en ligne de commande

## Dépannage

### L'interface ne se lance pas

- Vérifiez que PyQt6 est installé : `pip install PyQt6`
- Vérifiez les erreurs dans la console

### Le flux vidéo ne s'affiche pas

- Vérifiez que le drone Tello est allumé et connecté
- Vérifiez la connexion Wi-Fi au réseau du Tello
- Consultez les logs dans l'onglet "Logs" de l'interface

### Le tracking ne démarre pas

- Vérifiez que le fichier modèle (.pt) existe et est accessible
- Vérifiez les paramètres de configuration
- Consultez les messages d'erreur dans les logs

