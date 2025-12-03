# Tello Face Tracking v1.0.0 - Windows Release

## 🎉 Première release Windows !

Tello Face Tracking est maintenant disponible pour **Windows** avec un exécutable autonome facile à utiliser.

### 🆕 Nouveautés

- ✅ **Exécutable Windows** : Plus besoin d'installer Python !
- ✅ **Installation simplifiée** : Télécharger, extraire, lancer
- ✅ **Guide complet** : Documentation détaillée pour débutants
- ✅ **Interface graphique** : PyQt6 moderne et intuitive
- ✅ **Détection automatique** : YOLO-face pour tracking précis
- ✅ **Support multiplateforme** : Linux (code source) et Windows (exécutable)

### 📦 Téléchargements

| Fichier | Taille | Description |
|---------|--------|-------------|
| **TelloFaceTracking-v1.0.0-Windows-x64.zip** | ~250 MB | Application complète (exécutable + dépendances) |
| **yolov8n-face.pt** | ~6 MB | Modèle de détection (inclus ou séparé selon le ZIP) |
| **README_WINDOWS.md** | - | Guide d'utilisation complet |

> ⚠️ **Important** : Assurez-vous d'avoir le modèle YOLO (`yolov8n-face.pt`) dans le même dossier que l'exécutable

### 🚀 Installation rapide

1. **Télécharger** `TelloFaceTracking-v1.0.0-Windows-x64.zip`
2. **Extraire** l'archive dans un dossier
3. **Placer** le fichier `yolov8n-face.pt` dans le même dossier que l'exécutable (si non inclus)
4. **Connecter** au WiFi du drone Tello (réseau TELLO-XXXXXX)
5. **Lancer** `TelloFaceTracking.exe`

📖 **Guide complet** : Voir [README_WINDOWS.md](README_WINDOWS.md)

### 📋 Prérequis

- **OS** : Windows 7 / 8 / 10 / 11 (64-bit)
- **Matériel** : Drone DJI Tello
- **Connexion** : WiFi pour se connecter au drone
- **Espace disque** : ~300 MB libres

### ✨ Fonctionnalités

#### Détection et tracking
- 🎯 Détection automatique de visage avec YOLO
- 🔄 Suivi en temps réel (ajustement horizontal/vertical/distance)
- 📊 Affichage du flux vidéo en direct
- 📈 Statistiques en temps réel (FPS, batterie, vitesses)

#### Contrôles
- 🎮 Interface graphique intuitive
- 🚁 Décollage/atterrissage automatique
- 🛑 Bouton d'arrêt d'urgence
- ⚙️ Paramètres ajustables (vitesse, sensibilité)

#### Sécurité
- 🔋 Surveillance de la batterie en temps réel
- ⚠️ Alertes de sécurité
- 📝 Logs détaillés des opérations

### 🐛 Problèmes connus

- Le pare-feu Windows peut demander une autorisation au premier lancement (normal)
- Sur Windows 7, certaines animations de l'interface peuvent être lentes
- Le drone doit être à moins de 10 mètres pour une connexion stable
- La gestion WiFi automatique n'est pas disponible sous Windows (connexion manuelle requise)

### 🔧 Dépannage

**Problème** : "Le modèle n'est pas trouvé"
→ Vérifiez que `yolov8n-face.pt` est dans le même dossier que l'exécutable

**Problème** : "Impossible de se connecter au drone"
→ Vérifiez que vous êtes connecté au WiFi TELLO-XXXXXX avant de lancer l'application

**Problème** : Pas de flux vidéo
→ Attendez 5-10 secondes après avoir cliqué sur "Démarrer"

📖 **Guide de dépannage complet** : Voir [README_WINDOWS.md](README_WINDOWS.md#dépannage)

### 📝 Notes importantes

#### Pour les utilisateurs Linux
Cette release est spécifique à Windows. Les utilisateurs Linux peuvent continuer à utiliser le code source Python directement avec les fonctionnalités natives (gestion WiFi automatique incluse).

#### À propos du modèle YOLO
Le modèle `yolov8n-face.pt` peut être fourni séparément pour :
- Réduire la taille de téléchargement
- Permettre des mises à jour indépendantes
- Respecter les licences

### 📚 Documentation

- **[README.md](README.md)** - Documentation principale du projet
- **[README_WINDOWS.md](README_WINDOWS.md)** - Guide complet utilisateur Windows
- **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)** - Guide pour développeurs
- **[CHANGELOG.md](CHANGELOG.md)** - Historique des modifications

### 🤝 Contribution

Vous avez trouvé un bug ? Une suggestion d'amélioration ?
- Ouvrez une [issue](../../issues)
- Consultez le guide de contribution dans le README

### 📄 Licence

Ce projet utilise la licence **GPL-3.0**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

Le modèle YOLO-face est sous licence GPL-3.0 également.

### 🙏 Crédits

- **YOLO (Ultralytics)** - Détection d'objets
- **djitellopy** - Contrôle du Tello
- **PyQt6** - Interface graphique
- **OpenCV** - Traitement d'image
- **PyTorch** - Deep learning

---

## 🔐 Checksums (SHA256)

> ⚠️ Les checksums seront générés automatiquement par le script `create_release.py`

Pour vérifier l'intégrité du fichier téléchargé :
```powershell
Get-FileHash TelloFaceTracking-v1.0.0-Windows-x64.zip -Algorithm SHA256
```

---

## ⚠️ Avertissements de sécurité

- Utilisez le drone dans un espace dégagé
- Surveillez toujours le niveau de batterie
- Gardez une distance de sécurité avec les personnes
- Ne volez pas au-dessus de personnes ou d'objets fragiles
- Respectez les lois locales sur les drones

---

**Bon vol ! 🚁✨**

*Si cette application vous est utile, pensez à mettre une ⭐ sur le projet !*

---

*Release créée le : 2024-12-XX*  
*Testé sur : Windows 10 22H2, Windows 11 23H2*

