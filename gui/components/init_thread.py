#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thread d'initialisation pour créer le FaceTracker dans un thread séparé.
Évite de bloquer l'interface GUI pendant la connexion au drone.
"""

from PyQt6.QtCore import QThread, pyqtSignal, QObject
from typing import Optional, Dict, Any
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tello_face_tracking import FaceTracker


class InitializationThread(QThread):
    """
    Thread pour initialiser le FaceTracker dans un thread séparé.
    Évite de bloquer l'interface GUI pendant la connexion au drone.
    """
    
    # Signaux pour communiquer avec la GUI
    progress_update = pyqtSignal(str, str)  # (message, niveau: "info", "warning", "error")
    initialization_complete = pyqtSignal(object)  # FaceTracker initialisé
    initialization_failed = pyqtSignal(str)  # Message d'erreur
    
    def __init__(self, config: Dict[str, Any], parent: Optional[QObject] = None):
        """
        Initialise le thread d'initialisation.
        
        Args:
            config: Dictionnaire de configuration pour le FaceTracker
            parent: Parent QObject (optionnel)
        """
        super().__init__(parent)
        self.config = config
        self._cancel_requested = False
    
    def run(self):
        """
        Exécute l'initialisation du FaceTracker dans le thread.
        """
        try:
            self.progress_update.emit("Démarrage de l'initialisation...", "info")
            
            # Récupération de la configuration
            model_path = self.config.get('model_path', 'yolov8n-face.pt')
            conf_threshold = self.config.get('conf_threshold', 0.25)
            auto_wifi = self.config.get('auto_wifi', False)
            tello_ssid = self.config.get('tello_ssid', None)
            
            self.progress_update.emit("Chargement du modèle YOLO...", "info")
            
            # Création du tracker (cela peut prendre du temps)
            # La connexion au drone se fait dans le constructeur
            tracker = FaceTracker(
                model_path=model_path,
                conf_threshold=conf_threshold,
                auto_wifi=auto_wifi,
                tello_ssid=tello_ssid,
                gui_mode=True
            )
            
            if self._cancel_requested:
                # Si l'initialisation a été annulée, nettoyer et quitter
                try:
                    tracker.cleanup()
                except Exception:
                    pass
                return
            
            self.progress_update.emit("Application des paramètres avancés...", "info")
            
            # Application des paramètres avancés
            tracker.kp_x = self.config.get('kp_x', 0.15)
            tracker.kp_y = self.config.get('kp_y', 0.12)
            tracker.kd_x = self.config.get('kd_x', 0.25)
            tracker.kd_y = self.config.get('kd_y', 0.2)
            tracker.max_speed_yaw = self.config.get('max_speed_yaw', 30)
            tracker.max_speed_vertical = self.config.get('max_speed_vertical', 30)
            tracker.max_speed_horizontal = self.config.get('max_speed_horizontal', 40)
            tracker.max_speed_forward = self.config.get('max_speed_forward', 50)
            tracker.dead_zone = self.config.get('dead_zone', 40)
            tracker.target_face_size = self.config.get('target_face_size', 150)
            
            if self._cancel_requested:
                try:
                    tracker.cleanup()
                except Exception:
                    pass
                return
            
            self.progress_update.emit("Initialisation terminée avec succès", "info")
            
            # Émettre le signal de succès avec le tracker initialisé
            self.initialization_complete.emit(tracker)
            
        except Exception as e:
            error_msg = str(e)
            self.progress_update.emit(f"Erreur lors de l'initialisation: {error_msg}", "error")
            self.initialization_failed.emit(error_msg)
    
    def cancel(self):
        """
        Annule l'initialisation en cours.
        """
        self._cancel_requested = True

