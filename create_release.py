#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer un package de release Windows prêt à être distribué.
Génère un ZIP contenant l'exécutable, les dépendances et la documentation.
"""

import os
import sys
import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime


def print_header(text):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_executable_exists(dist_path):
    """Vérifie que l'exécutable existe dans dist/"""
    exe_path = dist_path / "TelloFaceTracking.exe"
    if not exe_path.exists():
        print(f"❌ ERREUR : L'exécutable n'existe pas : {exe_path}")
        print("   Exécutez d'abord : python build_windows.py")
        return False
    print(f"✓ Exécutable trouvé : {exe_path}")
    return True


def check_internal_folder(dist_path):
    """Vérifie que le dossier _internal existe"""
    internal_path = dist_path / "_internal"
    if not internal_path.exists():
        print(f"⚠ ATTENTION : Le dossier _internal n'existe pas : {internal_path}")
        print("   L'exécutable pourrait ne pas fonctionner correctement")
        return False
    print(f"✓ Dossier _internal trouvé : {internal_path}")
    return True


def check_model_file(project_root):
    """Vérifie si le modèle YOLO existe"""
    model_path = project_root / "yolov8n-face.pt"
    if model_path.exists():
        print(f"✓ Modèle YOLO trouvé : {model_path}")
        return True, model_path
    else:
        print(f"⚠ Modèle YOLO non trouvé : {model_path}")
        print("   Le modèle ne sera pas inclus dans le ZIP")
        print("   Les utilisateurs devront le télécharger séparément")
        return False, None


def check_readme_windows(project_root):
    """Vérifie que README_WINDOWS.md existe"""
    readme_path = project_root / "README_WINDOWS.md"
    if not readme_path.exists():
        print(f"⚠ ATTENTION : README_WINDOWS.md n'existe pas : {readme_path}")
        return False
    print(f"✓ README_WINDOWS.md trouvé : {readme_path}")
    return True


def get_version():
    """Détermine la version depuis les arguments ou demande à l'utilisateur"""
    if len(sys.argv) > 1:
        version = sys.argv[1]
        # Nettoyer la version (enlever 'v' si présent)
        if version.startswith('v'):
            version = version[1:]
        return version
    else:
        print("Version non spécifiée. Utilisation de '1.0.0' par défaut.")
        print("Pour spécifier une version : python create_release.py 1.0.0")
        return "1.0.0"


def create_release_zip(dist_path, project_root, version, include_model=False, model_path=None):
    """Crée le ZIP de release"""
    print_header("Création du ZIP de release")
    
    # Nom du fichier ZIP
    zip_name = f"TelloFaceTracking-v{version}-Windows-x64.zip"
    zip_path = project_root / zip_name
    
    # Supprimer l'ancien ZIP s'il existe
    if zip_path.exists():
        print(f"Suppression de l'ancien ZIP : {zip_path}")
        zip_path.unlink()
    
    print(f"Création du ZIP : {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Ajouter l'exécutable
        exe_path = dist_path / "TelloFaceTracking.exe"
        print(f"  Ajout : {exe_path.name}")
        zipf.write(exe_path, exe_path.name)
        
        # Ajouter le dossier _internal
        internal_path = dist_path / "_internal"
        if internal_path.exists():
            print(f"  Ajout : {internal_path.name}/")
            for root, dirs, files in os.walk(internal_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(dist_path)
                    zipf.write(file_path, arcname)
        
        # Ajouter LISEZMOI.txt s'il existe
        lisezmoi_path = dist_path / "LISEZMOI.txt"
        if lisezmoi_path.exists():
            print(f"  Ajout : {lisezmoi_path.name}")
            zipf.write(lisezmoi_path, lisezmoi_path.name)
        
        # Ajouter BUILD_INFO.txt s'il existe
        build_info_path = dist_path / "BUILD_INFO.txt"
        if build_info_path.exists():
            print(f"  Ajout : {build_info_path.name}")
            zipf.write(build_info_path, build_info_path.name)
        
        # Ajouter README_WINDOWS.md
        readme_path = project_root / "README_WINDOWS.md"
        if readme_path.exists():
            print(f"  Ajout : {readme_path.name}")
            zipf.write(readme_path, readme_path.name)
        
        # Ajouter le modèle YOLO si demandé et disponible
        if include_model and model_path:
            print(f"  Ajout : {model_path.name}")
            zipf.write(model_path, model_path.name)
        
        # Ajouter CHANGELOG.md
        changelog_path = project_root / "CHANGELOG.md"
        if changelog_path.exists():
            print(f"  Ajout : {changelog_path.name}")
            zipf.write(changelog_path, changelog_path.name)
    
    # Afficher la taille du ZIP
    zip_size = zip_path.stat().st_size
    zip_size_mb = zip_size / (1024 * 1024)
    print(f"\n✓ ZIP créé avec succès : {zip_path}")
    print(f"  Taille : {zip_size_mb:.2f} MB ({zip_size:,} octets)")
    
    return zip_path


def calculate_checksum(file_path):
    """Calcule le checksum SHA256 d'un fichier"""
    print_header("Calcul du checksum SHA256")
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def create_checksum_file(zip_path, checksum):
    """Crée un fichier avec le checksum"""
    checksum_file = zip_path.parent / f"{zip_path.stem}.sha256"
    with open(checksum_file, 'w') as f:
        f.write(f"{checksum}  {zip_path.name}\n")
    print(f"✓ Fichier de checksum créé : {checksum_file}")
    return checksum_file


def main():
    """Fonction principale"""
    print_header("Création du package de release Windows")
    
    # Déterminer les chemins
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir
    dist_path = project_root / "dist"
    
    # Vérifications
    print_header("Vérifications préalables")
    
    if not check_executable_exists(dist_path):
        sys.exit(1)
    
    if not check_internal_folder(dist_path):
        print("⚠ Continuons quand même...")
    
    model_exists, model_path = check_model_file(project_root)
    
    if not check_readme_windows(project_root):
        print("⚠ Continuons quand même...")
    
    # Demander si on doit inclure le modèle
    include_model = False
    if model_exists:
        response = input("\nInclure le modèle YOLO dans le ZIP ? (o/n) [n] : ")
        include_model = (response.lower() == 'o')
    
    # Obtenir la version
    version = get_version()
    print(f"\nVersion de la release : v{version}")
    
    # Créer le ZIP
    zip_path = create_release_zip(dist_path, project_root, version, include_model, model_path)
    
    # Calculer le checksum
    checksum = calculate_checksum(zip_path)
    print(f"Checksum SHA256 : {checksum}")
    
    # Créer le fichier de checksum
    checksum_file = create_checksum_file(zip_path, checksum)
    
    # Résumé
    print_header("Résumé")
    print(f"✓ ZIP de release créé : {zip_path.name}")
    print(f"✓ Checksum SHA256 : {checksum_file.name}")
    print(f"\n📦 Contenu du ZIP :")
    print(f"  - TelloFaceTracking.exe")
    print(f"  - _internal/ (dépendances)")
    if include_model and model_path:
        print(f"  - {model_path.name}")
    print(f"  - README_WINDOWS.md")
    print(f"  - LISEZMOI.txt")
    print(f"  - CHANGELOG.md")
    print(f"\n🚀 Prêt pour la distribution !")
    print(f"\nPour publier sur GitHub :")
    print(f"  1. Créez un tag : git tag -a v{version} -m 'Release v{version}'")
    print(f"  2. Push le tag : git push origin v{version}")
    print(f"  3. Créez une release sur GitHub et uploadez {zip_path.name}")


if __name__ == "__main__":
    main()

