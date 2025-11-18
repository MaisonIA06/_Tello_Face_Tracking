#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de build automatisé pour créer l'exécutable Windows.
Usage: python build_windows.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Couleurs pour la sortie console (Windows compatible)
try:
    import colorama
    colorama.init()
    GREEN = colorama.Fore.GREEN
    RED = colorama.Fore.RED
    YELLOW = colorama.Fore.YELLOW
    RESET = colorama.Fore.RESET
except ImportError:
    GREEN = RED = YELLOW = RESET = ""

def print_status(message, status="info"):
    """Affiche un message avec un préfixe coloré."""
    if status == "success":
        print(f"{GREEN}✓{RESET} {message}")
    elif status == "error":
        print(f"{RED}✗{RESET} {message}")
    elif status == "warning":
        print(f"{YELLOW}⚠{RESET} {message}")
    else:
        print(f"  {message}")

def check_python_version():
    """Vérifie que la version de Python est compatible."""
    version = sys.version_info
    if version.major != 3 or version.minor < 7:
        print_status(
            f"Version Python non supportée: {version.major}.{version.minor}",
            "error"
        )
        print_status("Python 3.7+ requis", "error")
        return False
    
    # Avertissement pour les versions très récentes
    if version.minor >= 13:
        print_status(
            f"Python {version.major}.{version.minor} détecté - version très récente",
            "warning"
        )
    
    print_status(f"Python {version.major}.{version.minor}.{version.micro} détecté", "success")
    return True

def check_dependencies():
    """Vérifie que les dépendances nécessaires sont installées."""
    required = ['PyInstaller', 'PyQt6', 'ultralytics', 'torch', 'cv2', 'djitellopy']
    missing = []
    
    for dep in required:
        try:
            if dep == 'cv2':
                __import__('cv2')
            elif dep == 'PyInstaller':
                import PyInstaller
            else:
                __import__(dep)
            print_status(f"{dep} installé", "success")
        except ImportError:
            print_status(f"{dep} manquant", "error")
            missing.append(dep)
    
    if missing:
        print_status("Installez les dépendances manquantes:", "warning")
        print_status("  pip install PyInstaller", "warning")
        print_status("  pip install -r requirements.txt", "warning")
        print_status("  pip install -r requirements_tello.txt", "warning")
        return False
    
    return True

def check_model_file():
    """Vérifie que le modèle YOLO est présent."""
    model_path = Path('yolov8n-face.pt')
    if not model_path.exists():
        print_status("Fichier yolov8n-face.pt introuvable", "error")
        print_status("Assurez-vous que le modèle est dans le répertoire du projet", "warning")
        return False
    print_status(f"Modèle trouvé: {model_path}", "success")
    return True

def clean_build_dirs():
    """Nettoie les répertoires de build précédents."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print_status(f"Nettoyage de {dir_name}...", "info")
            try:
                shutil.rmtree(dir_name)
                print_status(f"{dir_name} supprimé", "success")
            except Exception as e:
                print_status(f"Erreur lors de la suppression de {dir_name}: {e}", "warning")

def build_executable():
    """Construit l'exécutable avec PyInstaller."""
    print_status("Démarrage de la construction de l'exécutable...", "info")
    
    # Vérifier que le fichier .spec existe
    spec_file = Path('tello_face_tracking.spec')
    if not spec_file.exists():
        print_status("Fichier tello_face_tracking.spec introuvable", "error")
        return False
    
    try:
        # Exécuter PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'tello_face_tracking.spec']
        print_status(f"Exécution: {' '.join(cmd)}", "info")
        
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        
        print_status("Construction terminée avec succès!", "success")
        return True
        
    except subprocess.CalledProcessError as e:
        print_status(f"Erreur lors de la construction: {e}", "error")
        return False
    except FileNotFoundError:
        print_status("PyInstaller non trouvé. Installez-le avec: pip install PyInstaller", "error")
        return False

def verify_executable():
    """Vérifie que l'exécutable a été créé."""
    exe_path = Path('dist') / 'TelloFaceTracking.exe'
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print_status(f"Exécutable créé: {exe_path}", "success")
        print_status(f"Taille: {size_mb:.1f} MB", "info")
        return True
    else:
        print_status("Exécutable non trouvé dans dist/", "error")
        return False

def main():
    """Fonction principale."""
    print("=" * 60)
    print("Build Windows - Tello Face Tracking")
    print("=" * 60)
    print()
    
    # Vérifications préliminaires
    print_status("Vérification de l'environnement...", "info")
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_model_file():
        sys.exit(1)
    
    print()
    
    # Nettoyage
    print_status("Nettoyage des builds précédents...", "info")
    clean_build_dirs()
    print()
    
    # Construction
    if not build_executable():
        sys.exit(1)
    
    print()
    
    # Vérification
    if verify_executable():
        print()
        print_status("Build terminé avec succès!", "success")
        print_status("L'exécutable se trouve dans le dossier 'dist/'", "info")
        print_status("Vous pouvez maintenant créer l'installateur avec Inno Setup", "info")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()

