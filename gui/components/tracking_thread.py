#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thread de tracking pour exécuter la boucle de tracking dans un thread séparé.
"""

from PyQt6.QtCore import QThread, pyqtSignal, QObject
from typing import Optional, Dict, Any
import sys
import os
import time

# Ajouter le répertoire parent au path pour importer tello_face_tracking
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tello_face_tracking import FaceTracker


class TrackingThread(QThread):
    """
    Thread pour exécuter la boucle de tracking du drone Tello.
    Utilise des signaux PyQt6 pour communiquer avec la GUI de manière thread-safe.
    """
    
    # Signaux pour communiquer avec la GUI
    frame_ready = pyqtSignal(object)  # QImage
    stats_updated = pyqtSignal(dict)  # Dictionnaire de statistiques
    status_changed = pyqtSignal(str)  # "flying" ou "landed"
    error_occurred = pyqtSignal(str)  # Message d'erreur
    log_message = pyqtSignal(str, str)  # (message, niveau: "info", "warning", "error")
    tracking_finished = pyqtSignal()  # Signal quand le tracking est terminé
    
    def __init__(self, tracker: FaceTracker, parent: Optional[QObject] = None):
        """
        Initialise le thread de tracking.
        
        Args:
            tracker: Instance de FaceTracker configurée
            parent: Parent QObject (optionnel)
        """
        super().__init__(parent)
        self.tracker = tracker
        self._stop_requested = False
        self._is_flying = False
        self._tracker_initialized = False
        
        # Throttling pour limiter le taux d'émission des frames (max 30 FPS pour l'affichage)
        self._last_frame_time = 0
        self._min_frame_interval = 1.0 / 30.0  # 30 FPS max pour l'affichage
        
    def run(self):
        """
        Exécute la boucle de tracking dans le thread.
        """
        try:
            self.log_message.emit("=== Démarrage du tracking ===", "info")
            
            # Vérifier que le tracker est initialisé
            if not self.tracker:
                self.error_occurred.emit("Tracker non initialisé.")
                return
            
            # Initialisation du centre de l'image
            frame = self.tracker.get_frame()
            if frame is None:
                self.error_occurred.emit("Impossible de recevoir des frames du drone.")
                return
            
            h, w = frame.shape[:2]
            self.tracker.center_x = w // 2
            self.tracker.center_y = h // 2
            
            self._tracker_initialized = True
            self.log_message.emit("Tracking démarré avec succès", "info")
            
            while not self._stop_requested:
                # Vérifier que le tracker existe toujours
                if not self.tracker or not hasattr(self.tracker, 'tello') or self.tracker.tello is None:
                    self.log_message.emit("Tracker non disponible, arrêt du tracking", "warning")
                    break
                
                # Récupération de la frame
                frame = self.tracker.get_frame()
                if frame is None:
                    continue
                
                # Détection du visage
                face_info = self.tracker.detect_face(frame)
                
                # Calcul des commandes de contrôle
                if face_info is not None:
                    x_center, y_center, width, height, confidence = face_info
                    left_right, forward_backward, up_down, yaw = self.tracker.calculate_control(
                        (x_center, y_center, width, height)
                    )
                    self.tracker.no_detection_count = 0
                else:
                    # Aucun visage détecté - arrêter le mouvement
                    left_right, forward_backward, up_down, yaw = 0, 0, 0, 0
                    self.tracker.no_detection_count += 1
                
                # Application des commandes si le drone vole
                if self._is_flying and self.tracker and hasattr(self.tracker, 'tello') and self.tracker.tello is not None:
                    try:
                        self.tracker.rc_command_counter += 1
                        if self.tracker.rc_command_counter >= self.tracker.rc_command_interval:
                            if left_right != 0 or forward_backward != 0 or up_down != 0 or yaw != 0:
                                self.tracker.tello.send_rc_control(
                                    left_right_velocity=left_right,
                                    forward_backward_velocity=forward_backward,
                                    up_down_velocity=-up_down,
                                    yaw_velocity=yaw
                                )
                                self.tracker.rc_command_counter = 0
                    except Exception as e:
                        # Si la connexion est perdue, arrêter le tracking
                        self.log_message.emit(f"Erreur de communication avec le drone: {e}", "error")
                        break
                
                # Dessin de l'overlay
                frame = self.tracker.draw_overlay(
                    frame, 
                    face_info, 
                    (left_right, forward_backward, up_down, yaw)
                )
                
                # Throttling : ne pas émettre plus de 30 FPS pour éviter de saturer l'interface
                current_time = time.time()
                if current_time - self._last_frame_time >= self._min_frame_interval:
                    # Conversion de la frame OpenCV (BGR) en QImage (RGB)
                    from PyQt6.QtGui import QImage
                    rgb_image = self.tracker._convert_frame_to_qimage(frame)
                    
                    # Émission de la frame seulement si la conversion a réussi
                    if rgb_image is not None:
                        self.frame_ready.emit(rgb_image)
                        self._last_frame_time = current_time
                
                # Petit délai pour éviter de saturer le CPU
                # Cela permet aussi à l'interface de traiter les signaux
                time.sleep(0.01)  # 10ms de délai = ~100 FPS max pour le traitement
                
                # Préparation des statistiques
                try:
                    battery = self.tracker.tello.get_battery() if (self.tracker and hasattr(self.tracker, 'tello') and self.tracker.tello) else 0
                except Exception:
                    battery = 0
                
                stats = {
                    'fps': self.tracker.fps if self.tracker else 0.0,
                    'battery': battery,
                    'face_detected': face_info is not None,
                    'left_right': left_right,
                    'forward_backward': forward_backward,
                    'up_down': up_down,
                    'yaw': yaw,
                    'is_flying': self._is_flying
                }
                
                if face_info is not None:
                    x_center, y_center, width, height, confidence = face_info
                    stats['face_size'] = (width + height) / 2
                    stats['confidence'] = float(confidence)
                else:
                    stats['face_size'] = 0
                    stats['confidence'] = 0.0
                
                # Émission des statistiques (limiter à ~10 Hz pour éviter la saturation)
                # On émet les stats seulement toutes les 10 frames environ
                if self.tracker.frame_count % 10 == 0:
                    self.stats_updated.emit(stats)
                
                # Calcul du FPS
                self.tracker.frame_count += 1
                elapsed_time = time.time() - self.tracker.start_time
                if elapsed_time > 0:
                    self.tracker.fps = self.tracker.frame_count / elapsed_time
                
        except Exception as e:
            self.error_occurred.emit(f"Erreur dans la boucle de tracking: {str(e)}")
            import traceback
            self.log_message.emit(traceback.format_exc(), "error")
        finally:
            # Nettoyage final
            try:
                if self.tracker:
                    # S'assurer que le drone est arrêté
                    if self._is_flying:
                        try:
                            self.tracker.tello.send_rc_control(0, 0, 0, 0)
                            time.sleep(0.5)
                            self.tracker.tello.land()
                        except Exception:
                            pass
                    
                    # Nettoyer le tracker
                    self.tracker.cleanup()
            except Exception as e:
                self.log_message.emit(f"Erreur lors du nettoyage final: {e}", "warning")
            
            self.tracking_finished.emit()
    
    def request_takeoff(self):
        """
        Demande un décollage du drone.
        """
        if not self._is_flying:
            try:
                self.log_message.emit("Décollage...", "info")
                self.tracker.tello.takeoff()
                self._is_flying = True
                self.status_changed.emit("flying")
                time.sleep(3)
                self.log_message.emit("Drone en vol", "info")
            except Exception as e:
                self.error_occurred.emit(f"Erreur lors du décollage: {str(e)}")
    
    def request_land(self):
        """
        Demande un atterrissage du drone.
        """
        if self._is_flying:
            try:
                self.log_message.emit("Atterrissage...", "info")
                self.tracker.tello.send_rc_control(0, 0, 0, 0)
                time.sleep(1)
                self.tracker.tello.land()
                self._is_flying = False
                self.status_changed.emit("landed")
                self.log_message.emit("Drone au sol", "info")
            except Exception as e:
                self.error_occurred.emit(f"Erreur lors de l'atterrissage: {str(e)}")
    
    def emergency_stop(self):
        """
        Arrêt d'urgence : atterrit immédiatement le drone.
        """
        try:
            self.log_message.emit("ARRÊT D'URGENCE!", "warning")
            self.tracker.tello.send_rc_control(0, 0, 0, 0)
            time.sleep(0.5)
            if self._is_flying:
                self.tracker.tello.land()
                self._is_flying = False
                self.status_changed.emit("landed")
            self.log_message.emit("Arrêt d'urgence effectué", "warning")
        except Exception as e:
            self.error_occurred.emit(f"Erreur lors de l'arrêt d'urgence: {str(e)}")
    
    def stop(self):
        """
        Demande l'arrêt du thread de tracking.
        """
        self._stop_requested = True
        
        # Arrêter le drone si nécessaire
        if self._is_flying:
            try:
                self.request_land()
                # Attendre un peu pour que l'atterrissage se termine
                time.sleep(2)
            except Exception as e:
                self.log_message.emit(f"Erreur lors de l'arrêt: {e}", "warning")
        
        # Nettoyer le tracker
        if self.tracker:
            try:
                self.tracker.cleanup()
            except Exception as e:
                self.log_message.emit(f"Erreur lors du nettoyage: {e}", "warning")

