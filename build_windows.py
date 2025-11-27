#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de build automatisé pour créer l'exécutable Windows de Tello Face Tracking.
Ce script doit être exécuté depuis Windows avec toutes les dépendances installées.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_header(text):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_python_version():
    """Vérifie que la version de Python est compatible"""
    print_header("Vérification de la version Python")
    version = sys.version_info
    print(f"Version Python détectée : {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 8:
        print("❌ ERREUR : Python 3.8 ou supérieur est requis")
        print(f"   Version actuelle : {version.major}.{version.minor}")
        return False
    
    print("✓ Version Python compatible")
    return True


def check_platform():
    """Vérifie que le script est exécuté sous Windows"""
    print_header("Vérification de la plateforme")
    import platform
    system = platform.system()
    print(f"Système d'exploitation : {system}")
    
    if system != "Windows":
        print("⚠ ATTENTION : Ce script est conçu pour être exécuté sous Windows")
        print("   Vous pouvez continuer, mais l'exécutable généré sera pour votre plateforme actuelle.")
        response = input("\nContinuer quand même ? (o/n) : ")
        if response.lower() != 'o':
            return False
    else:
        print("✓ Plateforme Windows détectée")
    
    return True


def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    print_header("Vérification des dépendances")
    
    required_modules = [
        'PyInstaller',
        'PyQt6',
        'cv2',
        'numpy',
        'torch',
        'torchvision',
        'ultralytics',
        'djitellopy'
    ]
    
    missing = []
    for module in required_modules:
        try:
            if module == 'cv2':
                __import__('cv2')
            else:
                __import__(module.lower())
            print(f"✓ {module}")
        except ImportError:
            print(f"❌ {module} - MANQUANT")
            missing.append(module)
    
    if missing:
        print(f"\n❌ Dépendances manquantes : {', '.join(missing)}")
        print("\nInstallez-les avec :")
        print("  pip install -r requirements.txt")
        if 'PyInstaller' in missing:
            print("  pip install pyinstaller")
        return False
    
    print("\n✓ Toutes les dépendances sont installées")
    return True


def check_model_file():
    """Vérifie la présence du modèle YOLO (optionnel pour le build)"""
    print_header("Vérification du modèle YOLO")
    
    model_path = Path("yolov8n-face.pt")
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✓ Modèle trouvé : {model_path}")
        print(f"  Taille : {size_mb:.2f} MB")
        print("\n⚠ NOTE : Le modèle ne sera PAS inclus dans l'exécutable.")
        print("  L'utilisateur devra le placer manuellement à côté de l'exécutable.")
    else:
        print("⚠ Modèle non trouvé : yolov8n-face.pt")
        print("  Ce n'est pas un problème pour le build.")
        print("  L'utilisateur devra fournir le modèle séparément.")
    
    return True


def clean_build_directories():
    """Nettoie les répertoires de build précédents"""
    print_header("Nettoyage des builds précédents")
    
    dirs_to_clean = ['build', 'dist']
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"Suppression de {dir_name}/...")
            shutil.rmtree(dir_path)
            print(f"✓ {dir_name}/ supprimé")
        else:
            print(f"  {dir_name}/ n'existe pas (OK)")
    
    print("\n✓ Nettoyage terminé")
    return True


def run_pyinstaller():
    """Lance PyInstaller avec le fichier .spec"""
    print_header("Génération de l'exécutable avec PyInstaller")
    
    spec_file = "tello_face_tracking.spec"
    
    if not Path(spec_file).exists():
        print(f"❌ ERREUR : Fichier {spec_file} introuvable")
        return False
    
    print(f"Utilisation du fichier de configuration : {spec_file}")
    print("\nLancement de PyInstaller...")
    print("Cela peut prendre plusieurs minutes, veuillez patienter...\n")
    
    try:
        result = subprocess.run(
            ['pyinstaller', '--clean', spec_file],
            check=True,
            capture_output=False,
            text=True
        )
        
        print("\n✓ PyInstaller terminé avec succès")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERREUR lors de l'exécution de PyInstaller")
        print(f"   Code de retour : {e.returncode}")
        return False
    except FileNotFoundError:
        print("\n❌ ERREUR : PyInstaller n'est pas installé ou n'est pas dans le PATH")
        print("   Installez-le avec : pip install pyinstaller")
        return False


def verify_executable():
    """Vérifie que l'exécutable a bien été créé"""
    print_header("Vérification de l'exécutable généré")
    
    exe_path = Path("dist/TelloFaceTracking.exe")
    
    if not exe_path.exists():
        print("❌ ERREUR : L'exécutable n'a pas été créé")
        print(f"   Chemin attendu : {exe_path}")
        return False
    
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"✓ Exécutable créé : {exe_path}")
    print(f"  Taille : {size_mb:.2f} MB")
    
    return True


def create_instructions_file():
    """Crée un fichier d'instructions pour l'utilisateur final"""
    print_header("Création du fichier d'instructions")
    
    instructions = """╔══════════════════════════════════════════════════════════════════════╗
║         TELLO FACE TRACKING - INSTRUCTIONS D'UTILISATION            ║
╚══════════════════════════════════════════════════════════════════════╝

Merci d'avoir téléchargé Tello Face Tracking !

Ce logiciel permet de contrôler un drone DJI Tello pour suivre
automatiquement un visage détecté par caméra.

═══════════════════════════════════════════════════════════════════════
  PRÉREQUIS
═══════════════════════════════════════════════════════════════════════

1. Un drone DJI Tello (chargé et allumé)
2. Le modèle de détection : yolov8n-face.pt (~6 MB)
3. Windows 7 ou supérieur
4. Une connexion WiFi

═══════════════════════════════════════════════════════════════════════
  INSTALLATION
═══════════════════════════════════════════════════════════════════════

1. PLACER LE MODÈLE YOLO
   ─────────────────────
   • Téléchargez le fichier yolov8n-face.pt
   • Placez-le dans le MÊME DOSSIER que TelloFaceTracking.exe
   
   Votre dossier doit contenir :
     📁 TelloFaceTracking/
       ├── TelloFaceTracking.exe      ← L'application
       └── yolov8n-face.pt            ← Le modèle (REQUIS)

2. VÉRIFIER LE PARE-FEU WINDOWS
   ────────────────────────────
   • Au premier lancement, Windows peut demander l'autorisation
   • Autorisez l'accès réseau pour l'application
   • Ports utilisés : UDP 8889 (commandes) et 11111 (vidéo)

═══════════════════════════════════════════════════════════════════════
  UTILISATION
═══════════════════════════════════════════════════════════════════════

1. PRÉPARATION
   ───────────
   • Allumez le drone Tello
   • Attendez que la LED clignote (mode WiFi actif)

2. CONNEXION AU DRONE
   ──────────────────
   • Ouvrez les paramètres WiFi de Windows
   • Connectez-vous au réseau du Tello (TELLO-XXXXXX)
   • Le mot de passe est vide (connexion directe)

3. LANCER L'APPLICATION
   ────────────────────
   • Double-cliquez sur TelloFaceTracking.exe
   • L'interface graphique s'ouvre
   • Vérifiez que la connexion au drone est établie

4. DÉMARRAGE DU TRACKING
   ──────────────────────
   • Cliquez sur "Démarrer le tracking"
   • Le flux vidéo apparaît
   • Cliquez sur "Décoller" pour faire décoller le drone
   • Le drone suivra automatiquement le visage détecté

5. ARRÊT
   ─────
   • Cliquez sur "Atterrir" pour faire atterrir le drone
   • Cliquez sur "Arrêter le tracking" pour fermer la connexion
   • En cas d'urgence, utilisez le bouton "ARRÊT D'URGENCE"

═══════════════════════════════════════════════════════════════════════
  DÉPANNAGE
═══════════════════════════════════════════════════════════════════════

❌ "Le modèle n'est pas trouvé"
   → Vérifiez que yolov8n-face.pt est dans le même dossier que l'exe

❌ "Impossible de se connecter au drone"
   → Vérifiez que vous êtes connecté au WiFi du Tello
   → Redémarrez le drone et réessayez
   → Vérifiez le pare-feu Windows

❌ "Pas de flux vidéo"
   → Attendez quelques secondes après la connexion
   → Redémarrez l'application
   → Vérifiez que le port UDP 11111 n'est pas bloqué

❌ Le drone ne décolle pas
   → Vérifiez le niveau de batterie (min 20%)
   → Assurez-vous d'être dans un espace dégagé
   → Placez le drone sur une surface plane

═══════════════════════════════════════════════════════════════════════
  SÉCURITÉ
═══════════════════════════════════════════════════════════════════════

⚠ IMPORTANT :
  • Utilisez le drone dans un espace dégagé
  • Gardez une distance de sécurité avec les personnes
  • Surveillez constamment le niveau de batterie
  • Ayez toujours accès au bouton d'arrêt d'urgence

═══════════════════════════════════════════════════════════════════════
  SUPPORT
═══════════════════════════════════════════════════════════════════════

Pour plus d'informations, consultez :
  • README.md (documentation technique)
  • README_WINDOWS.md (guide détaillé Windows)
  • GitHub : [URL du projet]

═══════════════════════════════════════════════════════════════════════

Version : 1.0
Licence : GPL-3.0

Bon vol ! 🚁
"""
    
    output_path = Path("dist/LISEZMOI.txt")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"✓ Fichier d'instructions créé : {output_path}")
        return True
        
    except Exception as e:
        print(f"⚠ Impossible de créer le fichier d'instructions : {e}")
        return False


def create_package_info():
    """Crée un fichier récapitulatif du package"""
    print_header("Création du récapitulatif du package")
    
    info = """PACKAGE TELLO FACE TRACKING - BUILD WINDOWS
════════════════════════════════════════════

Contenu du package :
  • TelloFaceTracking.exe - Application principale
  • LISEZMOI.txt - Instructions d'utilisation

IMPORTANT - À FOURNIR SÉPARÉMENT :
  • yolov8n-face.pt - Modèle de détection (~6 MB)
    → Doit être placé dans le même dossier que l'exécutable

Distribution :
  1. Compressez le dossier dist/ en ZIP
  2. Incluez le fichier yolov8n-face.pt séparément ou dans le ZIP
  3. Distribuez aux utilisateurs finaux

Instructions pour les utilisateurs :
  → Voir LISEZMOI.txt
  → Voir README_WINDOWS.md pour le guide complet

Note pour les développeurs :
  → Voir BUILD_INSTRUCTIONS.md pour recompiler

════════════════════════════════════════════
Build créé le : {date}
Système de build : {system}
Version Python : {python_version}
════════════════════════════════════════════
"""
    
    import datetime
    import platform
    
    info = info.format(
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        system=platform.system() + " " + platform.release(),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    
    output_path = Path("dist/BUILD_INFO.txt")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(info)
        
        print(f"✓ Récapitulatif créé : {output_path}")
        return True
        
    except Exception as e:
        print(f"⚠ Impossible de créer le récapitulatif : {e}")
        return False


def main():
    """Fonction principale du script de build"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              TELLO FACE TRACKING - BUILD WINDOWS                     ║
║              Script de génération d'exécutable                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Étape 1 : Vérifications préalables
    checks = [
        ("Version Python", check_python_version),
        ("Plateforme", check_platform),
        ("Dépendances", check_dependencies),
        ("Modèle YOLO (optionnel)", check_model_file),
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            print(f"\n❌ Échec de la vérification : {check_name}")
            print("\n⚠ Le build ne peut pas continuer.")
            return 1
    
    # Étape 2 : Nettoyage
    if not clean_build_directories():
        print("\n⚠ Échec du nettoyage, mais on continue...")
    
    # Étape 3 : Génération de l'exécutable
    if not run_pyinstaller():
        print("\n❌ ÉCHEC : Impossible de générer l'exécutable")
        return 1
    
    # Étape 4 : Vérification
    if not verify_executable():
        print("\n❌ ÉCHEC : L'exécutable n'a pas été créé correctement")
        return 1
    
    # Étape 5 : Création des fichiers d'accompagnement
    create_instructions_file()
    create_package_info()
    
    # Résumé final
    print_header("BUILD TERMINÉ AVEC SUCCÈS")
    
    print("✓ L'exécutable a été créé dans le dossier dist/")
    print("\nProchaines étapes :")
    print("  1. Testez l'exécutable : dist/TelloFaceTracking.exe")
    print("  2. Placez yolov8n-face.pt dans dist/ pour tester")
    print("  3. Créez un fichier ZIP du dossier dist/ pour distribution")
    print("\nFichiers créés :")
    print("  • dist/TelloFaceTracking.exe - Application principale")
    print("  • dist/LISEZMOI.txt - Instructions utilisateur")
    print("  • dist/BUILD_INFO.txt - Informations de build")
    
    print("\n" + "=" * 70)
    print("  Merci d'utiliser Tello Face Tracking !")
    print("=" * 70 + "\n")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Build interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

