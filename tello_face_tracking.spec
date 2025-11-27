# -*- mode: python ; coding: utf-8 -*-
"""
Fichier de configuration PyInstaller pour Tello Face Tracking
Compatibilité: Windows 7+
"""

import os
import sys
from pathlib import Path

block_cipher = None

# Chemin de base du projet
# Utiliser le répertoire courant (le script est exécuté depuis le répertoire du projet)
project_root = Path(os.getcwd()).absolute()

# Déterminer le chemin vers le modèle YOLO
model_path = project_root / 'yolov8n-face.pt'

# Préparer la liste des données à inclure
# NOTE: Le modèle YOLO n'est PAS inclus dans l'exécutable
# L'utilisateur doit le placer manuellement à côté de l'exécutable
# Cela réduit la taille de l'exécutable et permet des mises à jour du modèle
datas_list = []
# if model_path.exists():
#     # Option: inclure le modèle YOLO dans le répertoire racine du bundle
#     datas_list.append((str(model_path), '.'))

a = Analysis(
    ['run_gui.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        # Modules PyQt6
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        # Modules ultralytics/YOLO
        'ultralytics',
        'ultralytics.yolo',
        'ultralytics.yolo.v8',
        'ultralytics.yolo.v8.detect',
        'ultralytics.yolo.engine',
        'ultralytics.yolo.engine.model',
        'ultralytics.yolo.engine.predictor',
        'ultralytics.yolo.engine.results',
        'ultralytics.yolo.utils',
        'ultralytics.yolo.utils.plotting',
        'ultralytics.yolo.data',
        'ultralytics.yolo.nn',
        'ultralytics.yolo.nn.modules',
        'ultralytics.yolo.nn.tasks',
        'ultralytics.yolo.cfg',
        'ultralytics.yolo.data.augment',
        'ultralytics.yolo.data.build',
        'ultralytics.yolo.data.dataset',
        'ultralytics.yolo.data.dataloaders',
        'ultralytics.yolo.data.utils',
        # Modules torch
        'torch',
        'torchvision',
        'torch.nn',
        'torch.nn.functional',
        'torch.utils',
        'torch.utils.data',
        # Modules OpenCV
        'cv2',
        # Modules djitellopy
        'djitellopy',
        'djitellopy.tello',
        # Modules standards
        'numpy',
        'PIL',
        'PIL.Image',
        'matplotlib',
        'pandas',
        'scipy',
        'yaml',
        'tqdm',
        'psutil',
        'omegaconf',
        # Modules GUI
        'gui.tello_gui',
        'gui.components.tracking_thread',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib.tests',
        'numpy.tests',
        'pandas.tests',
        'scipy.tests',
        'PIL.tests',
        'torch.test',
        'torchvision.tests',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TelloFaceTracking',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Pas de console pour l'application GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Compatibilité Windows 7+
    uac_admin=False,  # Pas besoin d'admin par défaut
    icon=None,  # Optionnel: chemin vers une icône .ico
)

