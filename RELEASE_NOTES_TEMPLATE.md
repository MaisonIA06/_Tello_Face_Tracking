# Tello Face Tracking v1.0.0 - Windows Release

> **Template de release notes** - Copiez ce contenu lors de la création d'une release GitHub

---

## 🎉 Première release Windows !

Tello Face Tracking est maintenant disponible pour **Windows** avec un exécutable autonome facile à utiliser.

### 🆕 Nouveautés

- ✅ **Exécutable Windows** : Plus besoin d'installer Python !
- ✅ **Installation simplifiée** : Télécharger, extraire, lancer
- ✅ **Guide complet** : Documentation détaillée pour débutants
- ✅ **Interface graphique** : PyQt6 moderne et intuitive
- ✅ **Détection automatique** : YOLO-face pour tracking précis

### 📦 Téléchargements

| Fichier | Taille | Description |
|---------|--------|-------------|
| **TelloFaceTracking-v1.0.0-Windows.zip** | ~250 MB | Application complète (exécutable + modèle) |
| **yolov8n-face.pt** | ~6 MB | Modèle de détection (si séparé) |
| **README_WINDOWS.md** | - | Guide d'utilisation complet |

> ⚠️ **Important** : Téléchargez TOUS les fichiers nécessaires

### 🚀 Installation rapide

1. **Télécharger** `TelloFaceTracking-v1.0.0-Windows.zip`
2. **Extraire** l'archive dans un dossier
3. **Placer** le fichier `yolov8n-face.pt` dans le même dossier que l'exécutable
4. **Connecter** au WiFi du drone Tello (réseau TELLO-XXXXXX)
5. **Lancer** `TelloFaceTracking.exe`

📖 **Guide complet** : Voir [README_WINDOWS.md](./README_WINDOWS.md)

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

### 🔧 Dépannage

**Problème** : "Le modèle n'est pas trouvé"
→ Vérifiez que `yolov8n-face.pt` est dans le même dossier que l'exécutable

**Problème** : "Impossible de se connecter au drone"
→ Vérifiez que vous êtes connecté au WiFi TELLO-XXXXXX

**Problème** : Pas de flux vidéo
→ Attendez 5-10 secondes après avoir cliqué sur "Démarrer"

📖 **Guide de dépannage complet** : Voir [README_WINDOWS.md](./README_WINDOWS.md#dépannage)

### 📝 Notes importantes

#### Pour les utilisateurs Linux
Cette release est spécifique à Windows. Les utilisateurs Linux peuvent continuer à utiliser le code source Python directement avec les fonctionnalités natives (gestion WiFi automatique incluse).

#### À propos du modèle YOLO
Le modèle `yolov8n-face.pt` est fourni séparément pour :
- Réduire la taille de téléchargement
- Permettre des mises à jour indépendantes
- Respecter les licences

### 📚 Documentation

- **[README_WINDOWS.md](./README_WINDOWS.md)** - Guide complet utilisateur Windows
- **[BUILD_INSTRUCTIONS.md](./BUILD_INSTRUCTIONS.md)** - Guide pour développeurs
- **[CHANGELOG_WINDOWS.md](./CHANGELOG_WINDOWS.md)** - Historique des modifications

### 🤝 Contribution

Vous avez trouvé un bug ? Une suggestion d'amélioration ?
- Ouvrez une [issue](../../issues)
- Consultez le [guide de contribution](./CONTRIBUTING.md) (si existant)

### 📄 Licence

Ce projet utilise la licence **GPL-3.0**.

Le modèle YOLO-face est sous licence GPL-3.0 également.

### 🙏 Crédits

- **YOLO (Ultralytics)** - Détection d'objets
- **djitellopy** - Contrôle du Tello
- **PyQt6** - Interface graphique
- **OpenCV** - Traitement d'image
- **PyTorch** - Deep learning

---

## 📸 Captures d'écran

> ℹ️ Ajoutez des captures d'écran ici lors de la publication

![Interface principale](./docs/screenshots/main-interface.png)
![Tracking en action](./docs/screenshots/tracking.png)
![Paramètres avancés](./docs/screenshots/settings.png)

---

## 🔐 Checksums (SHA256)

> ℹ️ Générez et ajoutez les checksums lors de la publication

```
TelloFaceTracking.exe: [checksum]
yolov8n-face.pt: [checksum]
```

Pour vérifier :
```powershell
Get-FileHash TelloFaceTracking.exe -Algorithm SHA256
```

---

## 📞 Support

**Questions ?** Consultez d'abord :
1. [README_WINDOWS.md](./README_WINDOWS.md) - Guide complet
2. [Issues](../../issues) - Problèmes connus et solutions
3. [Discussions](../../discussions) - Forum communautaire

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

*Release créée le : [DATE]*
*Testé sur : Windows 10 22H2, Windows 11 23H2*

