# 🔧 Build Instructions - Tello Face Tracking

Guide pour développeurs : comment compiler l'application Windows à partir du code source.

---

## 📋 Sommaire

- [Prérequis](#prérequis)
- [Préparation de l'environnement](#préparation-de-lenvironnement)
- [Build sur Windows](#build-sur-windows)
- [Build cross-platform (Linux → Windows)](#build-cross-platform-linux--windows)
- [Structure du build](#structure-du-build)
- [Dépannage du build](#dépannage-du-build)
- [Distribution](#distribution)

---

## Prérequis

### Système d'exploitation

**Recommandé** : Build sur Windows pour un exécutable Windows
- Windows 7, 8, 10, ou 11
- Windows Server 2016+ (non testé)

**Alternatif** : Cross-compilation depuis Linux (plus complexe, résultats variables)

### Logiciels requis

- **Python 3.8 - 3.11** (recommandé : 3.10)
  - Python 3.12+ peut avoir des problèmes de compatibilité avec PyInstaller
- **pip** (gestionnaire de paquets Python)
- **git** (optionnel, pour cloner le dépôt)

### Espace disque

- **~2 GB** pour l'environnement Python + dépendances
- **~500 MB** pour le build final (exécutable + fichiers temporaires)

---

## Préparation de l'environnement

### 1. Cloner le dépôt (ou télécharger le code source)

```bash
git clone https://github.com/votre-repo/yolo-face.git
cd yolo-face
```

Ou téléchargez et extrayez l'archive ZIP du code source.

### 2. Créer un environnement virtuel (recommandé)

**Sur Windows** :

```cmd
# Créer l'environnement virtuel
python -m venv venv_build

# Activer l'environnement
venv_build\Scripts\activate
```

**Sur Linux** :

```bash
# Créer l'environnement virtuel
python3 -m venv venv_build

# Activer l'environnement
source venv_build/bin/activate
```

### 3. Mettre à jour pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 4. Installer les dépendances du projet

```bash
pip install -r requirements.txt
```

### 5. Installer PyInstaller

```bash
pip install pyinstaller
```

**Version recommandée** : PyInstaller 5.13+ (testé avec 6.0+)

---

## Build sur Windows

### Méthode automatique (recommandée)

Le script `build_windows.py` automatise tout le processus :

```cmd
python build_windows.py
```

Le script effectue les étapes suivantes :
1. ✅ Vérification de Python (version 3.8+)
2. ✅ Vérification de la plateforme (Windows attendu)
3. ✅ Vérification des dépendances (PyQt6, torch, etc.)
4. ✅ Vérification du modèle YOLO (optionnel)
5. 🧹 Nettoyage des builds précédents
6. 🔨 Génération de l'exécutable avec PyInstaller
7. ✅ Vérification de l'exécutable généré
8. 📝 Création des fichiers d'instructions

**Résultat** : Exécutable dans `dist/TelloFaceTracking.exe`

### Méthode manuelle

Si vous préférez construire manuellement :

```cmd
# Nettoyer les builds précédents
rmdir /s /q build dist

# Lancer PyInstaller avec le fichier .spec
pyinstaller --clean tello_face_tracking.spec
```

L'exécutable sera créé dans `dist/TelloFaceTracking.exe`.

### Vérification du build

Testez l'exécutable :

```cmd
cd dist
TelloFaceTracking.exe
```

**Note** : Placez `yolov8n-face.pt` dans `dist/` pour un test complet.

---

## Build cross-platform (Linux → Windows)

⚠️ **Attention** : La cross-compilation n'est **pas officiellement supportée** par PyInstaller.

### Option 1 : Utiliser Wine (résultats variables)

**Installer Wine et Python Windows** :

```bash
# Sur Ubuntu/Debian
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install wine64 wine32

# Télécharger Python pour Windows
wget https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

# Installer Python dans Wine
wine python-3.10.11-amd64.exe
```

**Installer les dépendances et builder** :

```bash
wine python -m pip install -r requirements.txt
wine python -m pip install pyinstaller
wine pyinstaller --clean tello_face_tracking.spec
```

⚠️ **Limitations** :
- Peut ne pas fonctionner avec toutes les dépendances (PyQt6, torch)
- L'exécutable généré peut avoir des bugs
- Performances de build très lentes

### Option 2 : Machine virtuelle Windows

**Recommandé** pour un build fiable :

1. Installer VirtualBox ou VMware
2. Créer une VM Windows 10/11
3. Installer Python et les dépendances dans la VM
4. Builder depuis la VM

### Option 3 : GitHub Actions (CI/CD)

Créez un workflow GitHub Actions pour builder automatiquement :

```yaml
# .github/workflows/build-windows.yml
name: Build Windows

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build with PyInstaller
      run: python build_windows.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: TelloFaceTracking-Windows
        path: dist/
```

---

## Structure du build

### Fichier de configuration : `tello_face_tracking.spec`

Le fichier `.spec` configure PyInstaller :

```python
# Paramètres principaux
a = Analysis(
    ['run_gui.py'],              # Point d'entrée
    pathex=[...],                # Chemins de recherche
    hiddenimports=[...],         # Imports cachés à inclure
    datas=[...],                 # Données à inclure (optionnel pour le modèle)
    excludes=[...],              # Modules à exclure
)

exe = EXE(
    name='TelloFaceTracking',    # Nom de l'exécutable
    console=False,               # Pas de console (GUI)
    icon=None,                   # Icône (optionnel)
)
```

### Modules inclus

**Dépendances principales** :
- `PyQt6` : Interface graphique
- `torch` + `torchvision` : Deep learning
- `ultralytics` : YOLO
- `djitellopy` : Contrôle du Tello
- `opencv-python` (cv2) : Traitement d'image
- `numpy`, `pillow`, `matplotlib` : Utilitaires

**Modules cachés** (imports dynamiques) :
- Tous les sous-modules de `ultralytics.yolo`
- Plugins PyQt6
- Backends torch

### Fichiers de données

**Inclus dans l'exécutable** :
- Code Python (compilé)
- Bibliothèques partagées (.dll)
- Configuration PyQt6

**NON inclus** (fourni séparément) :
- `yolov8n-face.pt` : Modèle YOLO (~6 MB)
  - Raison : Taille importante, mises à jour possibles

### Exclusions

Pour réduire la taille de l'exécutable :
- Tests : `*.tests`, `test_*`
- Documentation : `docs/`, `*.md` (sauf essentiels)
- Exemples : `examples/`, `samples/`
- Tkinter (non utilisé)

---

## Dépannage du build

### Erreur : "Module not found"

**Cause** : Import caché non détecté par PyInstaller

**Solution** :
1. Identifiez le module manquant dans l'erreur
2. Ajoutez-le à `hiddenimports` dans `tello_face_tracking.spec` :

```python
hiddenimports=[
    ...,
    'nom_du_module_manquant',
],
```

3. Relancez le build

### Erreur : "Failed to execute script"

**Cause** : Erreur dans le code au runtime

**Solution** :
1. Activez la console pour voir les erreurs :
   ```python
   # Dans tello_face_tracking.spec
   exe = EXE(
       ...,
       console=True,  # Changer False → True
   )
   ```
2. Relancez le build et lisez les messages d'erreur
3. Corrigez l'erreur dans le code source
4. Remettez `console=False` après correction

### L'exécutable est très gros (>500 MB)

**Cause** : Inclusion de PyTorch avec CUDA

**Solution** : Utiliser PyTorch CPU uniquement

```bash
# Désinstaller torch
pip uninstall torch torchvision

# Réinstaller version CPU
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Rebuild
python build_windows.py
```

**Tailles typiques** :
- Avec PyTorch CPU : ~200-350 MB
- Avec PyTorch CUDA : ~500-800 MB

### Erreur : "ImportError: DLL load failed"

**Cause** : Dépendances système manquantes

**Solution sur Windows** :
1. Installez Microsoft Visual C++ Redistributable :
   - [VC++ 2015-2022 (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Installez Windows SDK (si nécessaire)

### PyInstaller ne trouve pas les modules

**Solution** : Vérifiez l'environnement virtuel

```bash
# Vérifier que vous êtes dans le bon environnement
python -c "import sys; print(sys.prefix)"

# Vérifier les modules installés
pip list

# Réinstaller si nécessaire
pip install -r requirements.txt --force-reinstall
```

---

## Optimisations

### Réduire la taille de l'exécutable

1. **Utiliser UPX** (compresseur d'exécutables) :

```bash
# Installer UPX
# Windows : télécharger depuis https://upx.github.io/

# Dans tello_face_tracking.spec
exe = EXE(
    ...,
    upx=True,  # Activer la compression UPX
)
```

2. **Exclure les tests et docs** :

```python
excludes=[
    'test',
    'tests',
    'testing',
    'unittest',
    '*.tests',
],
```

3. **Utiliser PyTorch CPU** (voir ci-dessus)

### Améliorer le temps de démarrage

**Option 1** : Un seul fichier (plus lent au démarrage) :

```python
exe = EXE(
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    ...,
    name='TelloFaceTracking',
    # Un seul fichier .exe
)
```

**Option 2** : Dossier (démarrage plus rapide, utilisé actuellement) :

```python
# EXE + dossier _internal/
# Plus rapide car pas besoin de décompresser
```

---

## Distribution

### Créer un package de distribution

#### Méthode 1 : Archive ZIP (simple)

```bash
# Copier le modèle dans dist/
copy yolov8n-face.pt dist\

# Créer l'archive
# Windows (PowerShell)
Compress-Archive -Path dist\* -DestinationPath TelloFaceTracking-v1.0-Windows.zip

# Linux
zip -r TelloFaceTracking-v1.0-Windows.zip dist/
```

**Contenu du ZIP** :
```
TelloFaceTracking-v1.0-Windows.zip
├── TelloFaceTracking.exe
├── yolov8n-face.pt
├── LISEZMOI.txt
├── BUILD_INFO.txt
└── _internal/ (dossier avec les DLL)
```

#### Méthode 2 : Installateur avec Inno Setup (avancé)

**Installer Inno Setup** :
- Télécharger : https://jrsoftware.org/isdl.php

**Créer un script Inno Setup** (`installer.iss`) :

```ini
[Setup]
AppName=Tello Face Tracking
AppVersion=1.0
DefaultDirName={autopf}\TelloFaceTracking
DefaultGroupName=Tello Face Tracking
OutputBaseFilename=TelloFaceTracking-Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\TelloFaceTracking.exe"; DestDir: "{app}"
Source: "dist\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs
Source: "yolov8n-face.pt"; DestDir: "{app}"
Source: "dist\LISEZMOI.txt"; DestDir: "{app}"

[Icons]
Name: "{group}\Tello Face Tracking"; Filename: "{app}\TelloFaceTracking.exe"
Name: "{autodesktop}\Tello Face Tracking"; Filename: "{app}\TelloFaceTracking.exe"
```

**Compiler l'installateur** :
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

### Checksum et vérification

Générez un fichier de checksums pour la vérification d'intégrité :

**Windows (PowerShell)** :
```powershell
Get-FileHash TelloFaceTracking.exe -Algorithm SHA256 | Format-List
```

**Linux** :
```bash
sha256sum dist/TelloFaceTracking.exe > checksums.txt
```

---

## Versioning

### Marquer une version

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Nommer les releases

Format recommandé :
```
TelloFaceTracking-v1.0.0-Windows-x64.zip
TelloFaceTracking-v1.0.0-Setup.exe
```

---

## Ressources supplémentaires

### Documentation PyInstaller

- [PyInstaller Manual](https://pyinstaller.org/en/stable/)
- [Spec Files](https://pyinstaller.org/en/stable/spec-files.html)
- [Hooks](https://pyinstaller.org/en/stable/hooks.html)

### Outils utiles

- **Resource Hacker** : Éditer l'icône/métadonnées de l'exe
- **Dependency Walker** : Analyser les DLL manquantes
- **Process Monitor** : Déboguer les problèmes de fichiers

---

## Checklist avant release

Avant de distribuer l'exécutable :

- [ ] Testé sur Windows 10 et Windows 11
- [ ] Testé avec connexion au Tello réel
- [ ] Niveau de batterie affiché correctement
- [ ] Flux vidéo fonctionnel
- [ ] Contrôles (décoller/atterrir) fonctionnels
- [ ] Arrêt d'urgence fonctionne
- [ ] Pas d'erreurs dans les logs
- [ ] Fichier README_WINDOWS.md inclus
- [ ] Fichier LISEZMOI.txt créé
- [ ] Modèle yolov8n-face.pt fourni ou lien de téléchargement
- [ ] Checksum SHA256 calculé
- [ ] Notes de version rédigées

---

## Support

Pour toute question sur le build :
1. Vérifiez cette documentation
2. Consultez la documentation PyInstaller
3. Ouvrez une issue sur GitHub

---

**Bonne compilation ! 🔨**

