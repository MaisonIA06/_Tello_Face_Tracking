# Guide de build Windows pour Tello Face Tracking

Ce guide explique comment créer un exécutable Windows (.exe) et un installateur pour l'application Tello Face Tracking.

## 📋 Prérequis

### Pour créer l'exécutable

- **Windows 7 ou supérieur** (le build doit être effectué sur Windows)
- **Python 3.7 à 3.11** (recommandé: Python 3.10)
- **Toutes les dépendances du projet** installées

### Installation des dépendances

```bash
# Installer PyInstaller
pip install PyInstaller

# Installer les dépendances du projet
pip install -r requirements.txt
pip install -r requirements_tello.txt
```

### Pour créer l'installateur (optionnel)

- **Inno Setup** (gratuit, téléchargeable sur https://jrsoftware.org/isdl.php)
  - Version recommandée: 6.2 ou supérieure

## 🚀 Processus de build

### Étape 1: Préparation

1. Assurez-vous que le fichier `yolov8n-face.pt` est présent dans le répertoire du projet
2. Vérifiez que toutes les dépendances sont installées

### Étape 2: Build automatisé (recommandé)

Utilisez le script de build automatisé :

```bash
python build_windows.py
```

Ce script :
- ✅ Vérifie la version de Python
- ✅ Vérifie que toutes les dépendances sont installées
- ✅ Vérifie que le modèle YOLO est présent
- ✅ Nettoie les builds précédents
- ✅ Construit l'exécutable
- ✅ Vérifie que l'exécutable a été créé

### Étape 3: Build manuel (alternative)

Si vous préférez construire manuellement :

```bash
# Nettoyer les builds précédents
rmdir /s /q build dist

# Construire l'exécutable
pyinstaller --clean tello_face_tracking.spec
```

L'exécutable sera créé dans le dossier `dist/TelloFaceTracking.exe`.

## 📦 Création de l'installateur

### Étape 1: Installer Inno Setup

1. Téléchargez Inno Setup depuis https://jrsoftware.org/isdl.php
2. Installez-le avec les options par défaut

### Étape 2: Compiler le script d'installation

1. Ouvrez Inno Setup Compiler
2. Ouvrez le fichier `installer.iss`
3. Cliquez sur "Build" > "Compile" (ou appuyez sur F9)
4. L'installateur sera créé dans le dossier `installer/`

### Étape 3: Personnalisation (optionnel)

Vous pouvez personnaliser l'installateur en modifiant `installer.iss` :

- **Icône de l'application** : Ajoutez le chemin vers un fichier `.ico` dans `SetupIconFile`
- **Version** : Modifiez `MyAppVersion`
- **Informations du développeur** : Modifiez `MyAppPublisher` et `MyAppURL`

## 📁 Structure des fichiers

Après le build, vous devriez avoir :

```
yolo-face/
├── build/              # Fichiers temporaires de build (peut être supprimé)
├── dist/               # Exécutable final
│   └── TelloFaceTracking.exe
├── installer/          # Installateur (après compilation Inno Setup)
│   └── TelloFaceTracking-Setup.exe
├── tello_face_tracking.spec
├── build_windows.py
├── installer.iss
└── BUILD_WINDOWS.md
```

## ⚠️ Notes importantes

### Taille de l'exécutable

L'exécutable sera volumineux (probablement 500MB-1GB) à cause de :
- PyTorch (bibliothèque de deep learning)
- OpenCV (traitement d'images)
- PyQt6 (interface graphique)
- Toutes les dépendances incluses

C'est normal et attendu pour une application avec ces dépendances.

### Compatibilité Windows

- **Windows 7+** : L'application est configurée pour fonctionner sur Windows 7 et supérieur
- **Architecture** : 64-bit uniquement (PyTorch nécessite 64-bit)

### Modèle YOLO

Le modèle `yolov8n-face.pt` est inclus dans l'exécutable. Si vous modifiez le modèle, vous devrez reconstruire l'exécutable.

### Dépendances système

L'exécutable est autonome et ne nécessite pas :
- ❌ Installation de Python
- ❌ Installation manuelle de dépendances
- ❌ Configuration spéciale

Cependant, il peut nécessiter :
- ✅ Visual C++ Redistributable (généralement déjà installé sur Windows)
- ✅ Connexion Wi-Fi pour utiliser le drone Tello

## 🔧 Dépannage

### Erreur: "PyInstaller not found"

```bash
pip install PyInstaller
```

### Erreur: "Module not found" lors de l'exécution

Vérifiez que tous les modules sont dans `hiddenimports` dans le fichier `.spec`.

### L'exécutable ne démarre pas

1. Vérifiez que vous êtes sur Windows
2. Essayez de lancer depuis la ligne de commande pour voir les erreurs :
   ```bash
   dist\TelloFaceTracking.exe
   ```
3. Vérifiez les dépendances système (Visual C++ Redistributable)

### L'application ne trouve pas le modèle YOLO

Le modèle est inclus dans l'exécutable. Si le problème persiste :
1. Vérifiez que `yolov8n-face.pt` existe dans le répertoire du projet avant le build
2. Vérifiez que le modèle est bien listé dans `datas` du fichier `.spec`

### Erreur lors de la compilation Inno Setup

1. Vérifiez que le fichier `dist/TelloFaceTracking.exe` existe
2. Vérifiez que tous les chemins dans `installer.iss` sont corrects
3. Assurez-vous d'avoir les permissions d'écriture dans le dossier `installer/`

## 📝 Distribution

### Pour distribuer l'application

1. **Option 1: Installateur (recommandé)**
   - Distribuez uniquement `installer/TelloFaceTracking-Setup.exe`
   - Les utilisateurs n'ont qu'à double-cliquer pour installer

2. **Option 2: Exécutable portable**
   - Distribuez `dist/TelloFaceTracking.exe`
   - Les utilisateurs peuvent l'exécuter directement sans installation

### Recommandations

- Testez l'exécutable sur une machine Windows propre (sans Python installé)
- Vérifiez que toutes les fonctionnalités fonctionnent
- Incluez un fichier README avec les instructions d'utilisation

## 🎯 Prochaines étapes

Après avoir créé l'exécutable et l'installateur :

1. ✅ Tester sur une machine Windows propre
2. ✅ Vérifier toutes les fonctionnalités
3. ✅ Créer un guide d'utilisation pour les utilisateurs finaux
4. ✅ Préparer la distribution (GitHub Releases, site web, etc.)

## 📞 Support

Si vous rencontrez des problèmes lors du build, vérifiez :
- La version de Python (3.7-3.11)
- Que toutes les dépendances sont installées
- Que le modèle YOLO est présent
- Les logs de PyInstaller pour les erreurs détaillées

