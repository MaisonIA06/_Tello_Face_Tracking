# 🚀 Quick Start - Déploiement Windows

Guide de démarrage rapide pour créer et distribuer l'exécutable Windows.

---

## Pour vous (développeur Linux)

Votre workflow Linux **n'a pas changé** ! Continuez à utiliser :

```bash
# Lancer l'interface graphique
python run_gui.py

# Ou en ligne de commande
python tello_face_tracking.py
```

La gestion WiFi automatique fonctionne toujours sous Linux.

---

## Pour créer l'exécutable Windows

### Option 1 : Build sur Windows (recommandé)

**Sur une machine Windows ou VM Windows :**

```cmd
# 1. Installer Python 3.10 (https://www.python.org/downloads/)

# 2. Cloner le projet
git clone [votre-repo]
cd yolo-face

# 3. Créer un environnement virtuel
python -m venv venv_build
venv_build\Scripts\activate

# 4. Installer les dépendances
pip install -r requirements.txt
pip install pyinstaller

# 5. Lancer le build automatique
python build_windows.py

# 6. L'exécutable est dans dist/
cd dist
TelloFaceTracking.exe
```

**Résultat** : `dist/TelloFaceTracking.exe` + fichiers d'accompagnement

### Option 2 : GitHub Actions (automatique)

Créez `.github/workflows/build-windows.yml` :

```yaml
name: Build Windows
on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - run: |
        pip install -r requirements.txt
        pip install pyinstaller
        python build_windows.py
    - uses: actions/upload-artifact@v3
      with:
        name: Windows-Build
        path: dist/
```

Puis : `git tag v1.0.0 && git push --tags`

---

## Distribuer aux utilisateurs Windows

### 1. Préparer le package

```bash
# Dans le dossier dist/
# Ajouter le modèle YOLO
cp ../yolov8n-face.pt .

# Créer un ZIP
zip -r TelloFaceTracking-v1.0-Windows.zip *
# Ou sur Windows : clic droit → Compresser
```

### 2. Fichiers à fournir

Donnez aux utilisateurs :
- ✅ `TelloFaceTracking-v1.0-Windows.zip` (l'application)
- ✅ `README_WINDOWS.md` (le guide)
- ✅ Lien pour télécharger `yolov8n-face.pt` (si pas inclus dans le ZIP)

### 3. Instructions pour l'utilisateur

Renvoyez-le vers **README_WINDOWS.md** qui contient :
- ✅ Installation complète
- ✅ Configuration WiFi
- ✅ Guide d'utilisation pas à pas
- ✅ Dépannage complet

---

## Que faire en cas de problème ?

### Pour vous (développeur)

- **Problème de build** → Consultez `BUILD_INSTRUCTIONS.md`
- **Erreur PyInstaller** → Voir section "Dépannage du build"
- **Questions techniques** → `BUILD_INSTRUCTIONS.md` est très détaillé

### Pour les utilisateurs Windows

- **Toutes les réponses** → `README_WINDOWS.md`
- **Section dépannage** → 10+ problèmes courants avec solutions
- **FAQ** → Questions fréquentes

---

## Récapitulatif des fichiers créés

| Fichier | Pour qui ? | Description |
|---------|-----------|-------------|
| `README_WINDOWS.md` | 👤 Utilisateurs Windows | Guide complet d'installation et d'utilisation |
| `BUILD_INSTRUCTIONS.md` | 👨‍💻 Développeurs | Guide de build et compilation |
| `build_windows.py` | 👨‍💻 Développeurs | Script de build automatisé |
| `DEPLOIEMENT_WINDOWS.txt` | 👨‍💻 Vous | Résumé de l'implémentation |
| `QUICK_START_WINDOWS.md` | 👨‍💻 Vous | Ce fichier (démarrage rapide) |

---

## Checklist avant distribution

Avant de distribuer l'exécutable aux utilisateurs :

- [ ] Testé sur Windows 10
- [ ] Testé sur Windows 11
- [ ] Connexion au Tello fonctionne
- [ ] Flux vidéo s'affiche
- [ ] Contrôles (décoller/atterrir) fonctionnent
- [ ] Tracking de visage fonctionne
- [ ] Arrêt d'urgence fonctionne
- [ ] `README_WINDOWS.md` mis à jour avec liens de téléchargement
- [ ] Modèle `yolov8n-face.pt` disponible
- [ ] Numéro de version défini
- [ ] Release notes écrites

---

## Que faire maintenant ?

### Si vous voulez tester rapidement

1. **Sur votre Linux** : Tout fonctionne comme avant
   ```bash
   python run_gui.py
   ```

2. **Pour créer l'exe Windows** : Utilisez une VM Windows ou GitHub Actions

### Si vous voulez distribuer

1. Créez l'exécutable (voir "Pour créer l'exécutable Windows" ci-dessus)
2. Testez sur Windows 10/11
3. Créez un ZIP avec l'exe + modèle
4. Partagez avec `README_WINDOWS.md`

### Si vous avez des questions

Consultez les documentations détaillées :
- **Pour builder** : `BUILD_INSTRUCTIONS.md`
- **Pour comprendre les changements** : `DEPLOIEMENT_WINDOWS.txt`

---

**C'est tout ! Votre projet est prêt pour Windows. 🎉**

*Questions ? Toutes les réponses sont dans les fichiers de documentation créés.*

