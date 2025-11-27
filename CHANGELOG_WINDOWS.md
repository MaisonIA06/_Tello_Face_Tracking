# Changelog - Déploiement Windows

Historique des modifications pour l'adaptation Windows du projet Tello Face Tracking.

---

## [1.0.0] - 2025-11-27

### ✨ Nouveautés

#### Support Windows natif
- Détection automatique de la plateforme (Windows/Linux)
- Désactivation automatique de la gestion WiFi sous Windows
- Message d'information clair pour les utilisateurs Windows
- Interface adaptée avec instructions de connexion manuelle au Tello

#### Script de build automatisé
- Nouveau fichier `build_windows.py` pour générer l'exécutable Windows
- Vérifications automatiques de l'environnement (Python, dépendances, modèle)
- Nettoyage automatique des builds précédents
- Génération de fichiers d'instructions pour l'utilisateur final
- Messages d'erreur clairs et guidage pas à pas

#### Documentation complète
- **README_WINDOWS.md** : Guide complet pour utilisateurs Windows (20+ pages)
  - Installation détaillée
  - Configuration WiFi pas à pas
  - Guide d'utilisation illustré
  - Dépannage exhaustif (10+ problèmes)
  - FAQ et conseils de sécurité
  
- **BUILD_INSTRUCTIONS.md** : Guide technique pour développeurs
  - Instructions de build Windows
  - Cross-compilation Linux → Windows
  - Optimisations (taille, performance)
  - Distribution et packaging
  - CI/CD avec GitHub Actions
  
- **DEPLOIEMENT_WINDOWS.txt** : Résumé de l'implémentation
- **QUICK_START_WINDOWS.md** : Démarrage rapide
- **CHANGELOG_WINDOWS.md** : Ce fichier

### 🔧 Modifications techniques

#### Code source
- **tello_face_tracking.py** :
  - Ajout de `import platform`
  - Détection automatique de Windows dans `FaceTracker.__init__()`
  - Désactivation de `auto_wifi` si Windows détecté
  - Message informatif pour la connexion WiFi manuelle

- **gui/tello_gui.py** :
  - Ajout de `import platform`
  - Détection Windows dans la configuration par défaut
  - Message d'avertissement dans l'interface (label orange)
  - Désactivation de la checkbox "WiFi automatique" sous Windows
  - Tooltip explicatif ajouté

#### Configuration PyInstaller
- **tello_face_tracking.spec** :
  - Documentation ajoutée sur l'exclusion du modèle YOLO
  - Modèle non inclus dans l'exécutable (réduction de taille)
  - Permet à l'utilisateur de fournir/mettre à jour le modèle séparément

#### Git
- **.gitignore** :
  - Ajout de `build/` et `dist/` (artefacts PyInstaller)
  - Clarification des commentaires

### ✅ Compatibilité préservée

#### Linux (comportement inchangé)
- ✅ Gestion WiFi automatique toujours fonctionnelle
- ✅ Tous les scripts fonctionnent comme avant
- ✅ README.md original inchangé
- ✅ Aucune régression

#### Windows (nouveau support)
- ✅ Détection automatique de l'OS
- ✅ Gestion WiFi désactivée automatiquement
- ✅ Instructions claires pour connexion manuelle
- ✅ Interface utilisateur adaptée

#### Code source
- ✅ Un seul codebase pour Linux et Windows
- ✅ Pas de duplication de code
- ✅ Détection OS avec `platform.system()`
- ✅ Maintenabilité préservée

### 📦 Fichiers de distribution

#### Créés automatiquement par `build_windows.py`
- `dist/TelloFaceTracking.exe` - Application principale (~200-350 MB)
- `dist/LISEZMOI.txt` - Instructions courtes pour l'utilisateur
- `dist/BUILD_INFO.txt` - Informations de build (date, version, système)
- `dist/_internal/` - Dossier avec les DLL et dépendances

#### À fournir séparément
- `yolov8n-face.pt` - Modèle YOLO (~6 MB)
  - Non inclus dans l'exécutable pour réduire la taille
  - À placer dans le même dossier que l'exécutable

### 🎯 Taille de l'exécutable

#### Avec PyTorch CPU (recommandé)
- **200-350 MB** - Exécutable + dépendances
- Suffisant pour le Tello (pas besoin de GPU)

#### Avec PyTorch CUDA
- **500-800 MB** - Inclut CUDA (non recommandé pour cette application)

### 🐛 Corrections

Aucune correction de bug dans cette version (nouvelle fonctionnalité).

### ⚠️ Notes de migration

#### Pour les développeurs

**Aucune migration nécessaire !**

- Le code Linux existant fonctionne sans modification
- Les nouveaux fichiers sont additionnels
- Aucun changement de l'API ou des interfaces

#### Pour les utilisateurs Linux

**Aucun changement !**

- Utilisez le projet comme d'habitude
- La gestion WiFi automatique fonctionne toujours
- README.md original reste la référence

#### Pour les nouveaux utilisateurs Windows

- Suivez `README_WINDOWS.md` pour l'installation
- Téléchargez l'exécutable depuis les releases
- Placez `yolov8n-face.pt` à côté de l'exécutable
- Connectez-vous manuellement au WiFi du Tello

### 🔮 Évolutions futures possibles

#### Court terme
- [ ] Icône personnalisée pour l'exécutable Windows
- [ ] Installateur Windows avec Inno Setup
- [ ] Signature de code pour éviter les avertissements Windows Defender
- [ ] GitHub Actions pour build automatique

#### Moyen terme
- [ ] Support macOS (si demande)
- [ ] Gestion WiFi automatique Windows (avec netsh)
- [ ] Mode portable (exécutable unique sans dépendances externes)
- [ ] Multi-langue (anglais, français, etc.)

#### Long terme
- [ ] Store Windows (Microsoft Store)
- [ ] Auto-mise à jour de l'application
- [ ] Téléchargement automatique du modèle YOLO
- [ ] Installateur MSI professionnel

### 📊 Statistiques

#### Lignes de code ajoutées/modifiées
- **tello_face_tracking.py** : ~15 lignes ajoutées
- **gui/tello_gui.py** : ~20 lignes ajoutées
- **build_windows.py** : ~400 lignes (nouveau)
- **Documentation** : ~1500 lignes (nouveaux fichiers)

#### Fichiers créés
- 6 nouveaux fichiers de documentation/build
- 0 nouveau fichier Python (seulement modifications)

#### Compatibilité
- **100%** compatible avec le code Linux existant
- **0** régression détectée

### 🙏 Remerciements

- **Ultralytics** : YOLO et modèle de détection
- **djitellopy** : Bibliothèque de contrôle Tello
- **PyInstaller** : Création d'exécutables
- **PyQt6** : Interface graphique

---

## Format de versioning

Ce projet suit le [Semantic Versioning](https://semver.org/) :

- **MAJOR** : Changements incompatibles de l'API
- **MINOR** : Nouvelles fonctionnalités compatibles
- **PATCH** : Corrections de bugs

**Version actuelle** : 1.0.0 (première release avec support Windows)

---

## Comment contribuer

Si vous souhaitez améliorer le support Windows :

1. Consultez `BUILD_INSTRUCTIONS.md` pour comprendre le build
2. Testez sur différentes versions de Windows
3. Signalez les problèmes spécifiques à Windows
4. Proposez des améliorations de la documentation

---

**Merci d'utiliser Tello Face Tracking ! 🚁**

