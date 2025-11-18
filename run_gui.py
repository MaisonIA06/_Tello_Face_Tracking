#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement rapide pour l'interface graphique.
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from gui.tello_gui import main
    main()
except ImportError as e:
    print(f"Erreur: {e}")
    print("\nAssurez-vous que PyQt6 est installé:")
    print("  pip install PyQt6")
    sys.exit(1)

