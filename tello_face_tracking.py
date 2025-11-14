#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de face tracking pour drone DJI Tello
Utilise YOLO-face pour détecter les visages et ajuster la position du drone
pour garder le visage au centre de l'image.
"""

import cv2
import numpy as np
import time
from typing import Optional, Tuple
import sys
import os

# Import de YOLO depuis ultralytics
try:
    from ultralytics import YOLO
except ImportError:
    print("Erreur: Le module ultralytics n'est pas installé.")
    print("Installez-le avec: pip install ultralytics")
    sys.exit(1)

# Import de djitellopy pour contrôler le Tello
try:
    from djitellopy import Tello
except ImportError:
    print("Erreur: Le module djitellopy n'est pas installé.")
    print("Installez-le avec: pip install djitellopy")
    sys.exit(1)


class FaceTracker:
    """
    Classe principale pour le tracking de visage avec le drone Tello.
    """
    
    def __init__(self, model_path: str = "yolov8n-face.pt", conf_threshold: float = 0.25):
        """
        Initialise le tracker de visage.
        
        Args:
            model_path: Chemin vers le modèle YOLO-face (.pt)
            conf_threshold: Seuil de confiance pour la détection (0.0-1.0)
        """
        # Chargement du modèle YOLO
        print(f"Chargement du modèle YOLO depuis {model_path}...")
        if not os.path.exists(model_path):
            print(f"Erreur: Le fichier {model_path} n'existe pas.")
            print("Assurez-vous que le modèle est présent dans le répertoire courant.")
            sys.exit(1)
        
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        
        # Initialisation du drone Tello
        print("Connexion au drone Tello...")
        self.tello = Tello()
        self.tello.connect()
        
        # Vérification de la batterie
        battery = self.tello.get_battery()
        print(f"Niveau de batterie: {battery}%")
        if battery < 20:
            print("ATTENTION: Batterie faible! Chargez le drone avant de continuer.")
            response = input("Continuer quand même? (o/n): ")
            if response.lower() != 'o':
                self.tello.end()
                sys.exit(0)
        
        # Configuration du flux vidéo
        self.tello.streamon()
        self.frame_read = self.tello.get_frame_read()
        
        # Paramètres de contrôle
        self.center_x = 0  # Centre horizontal de l'image (sera mis à jour)
        self.center_y = 0  # Centre vertical de l'image (sera mis à jour)
        
        # Paramètres PID pour le contrôle du drone
        # Ces valeurs peuvent être ajustées selon les besoins
        self.kp_x = 0.5    # Gain proportionnel horizontal (yaw)
        self.kp_y = 0.3    # Gain proportionnel vertical
        self.kd_x = 0.15   # Gain dérivé horizontal (réduit les oscillations)
        self.kd_y = 0.1    # Gain dérivé vertical
        
        # Variables pour le contrôle PID
        self.last_error_x = 0
        self.last_error_y = 0
        
        # Vitesse maximale du drone
        self.max_speed_yaw = 50      # deg/s pour la rotation
        self.max_speed_vertical = 30  # cm/s pour le mouvement vertical
        
        # Zone morte (dead zone) pour éviter les micro-mouvements
        self.dead_zone = 20  # pixels
        
        # Compteur de frames sans détection
        self.no_detection_count = 0
        self.max_no_detection = 30  # Arrêter après 30 frames sans détection
        
        # Statistiques
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Récupère une frame du flux vidéo du Tello.
        
        Returns:
            Frame en format numpy array (BGR) ou None si erreur
        """
        try:
            frame = self.frame_read.frame
            if frame is not None:
                # Le Tello renvoie des frames en BGR
                return frame
        except Exception as e:
            print(f"Erreur lors de la récupération de la frame: {e}")
        return None
    
    def detect_face(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Détecte un visage dans la frame en utilisant YOLO.
        
        Args:
            frame: Image en format numpy array (BGR)
            
        Returns:
            Tuple (x_center, y_center, width, height) du visage détecté,
            ou None si aucun visage n'est détecté
        """
        # Exécution de la détection YOLO
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        
        # Extraction des détections
        if len(results) > 0 and len(results[0].boxes) > 0:
            # Prendre le visage le plus grand (le plus proche)
            boxes = results[0].boxes
            areas = []
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                area = (x2 - x1) * (y2 - y1)
                areas.append(area)
            
            # Index du visage le plus grand
            largest_idx = np.argmax(areas)
            box = boxes[largest_idx]
            
            # Coordonnées de la bounding box
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = box.conf[0].cpu().numpy()
            
            # Calcul du centre et des dimensions
            x_center = int((x1 + x2) / 2)
            y_center = int((y1 + y2) / 2)
            width = int(x2 - x1)
            height = int(y2 - y1)
            
            return (x_center, y_center, width, height, confidence)
        
        return None
    
    def calculate_control(self, face_center: Tuple[int, int]) -> Tuple[int, int]:
        """
        Calcule les commandes de contrôle du drone pour centrer le visage.
        
        Args:
            face_center: Tuple (x, y) du centre du visage détecté
            
        Returns:
            Tuple (velocity_x, velocity_y) en cm/s pour le contrôle du drone
        """
        face_x, face_y = face_center
        
        # Calcul de l'erreur (différence entre le centre du visage et le centre de l'image)
        error_x = face_x - self.center_x
        error_y = face_y - self.center_y
        
        # Application de la zone morte
        if abs(error_x) < self.dead_zone:
            error_x = 0
        if abs(error_y) < self.dead_zone:
            error_y = 0
        
        # Contrôle PID simplifié (sans terme intégral pour éviter l'instabilité)
        # Terme proportionnel
        p_x = self.kp_x * error_x
        p_y = self.kp_y * error_y
        
        # Terme dérivé
        d_x = self.kd_x * (error_x - self.last_error_x)
        d_y = self.kd_y * (error_y - self.last_error_y)
        
        # Commande totale
        velocity_x = int(p_x + d_x)
        velocity_y = int(p_y + d_y)
        
        # Limitation de la vitesse
        # velocity_x est pour le yaw (rotation) en deg/s
        # velocity_y est pour le mouvement vertical en cm/s
        velocity_x = np.clip(velocity_x, -self.max_speed_yaw, self.max_speed_yaw)
        velocity_y = np.clip(velocity_y, -self.max_speed_vertical, self.max_speed_vertical)
        
        # Mise à jour des erreurs précédentes
        self.last_error_x = error_x
        self.last_error_y = error_y
        
        return (velocity_x, velocity_y)
    
    def draw_overlay(self, frame: np.ndarray, face_info: Optional[Tuple], 
                     velocity: Tuple[int, int]) -> np.ndarray:
        """
        Dessine les informations de tracking sur la frame.
        
        Args:
            frame: Image à annoter
            face_info: Informations du visage détecté ou None
            velocity: Vitesse de contrôle (vx, vy)
            
        Returns:
            Frame annotée
        """
        h, w = frame.shape[:2]
        
        # Dessin du centre de l'image (cible)
        cv2.circle(frame, (self.center_x, self.center_y), 10, (0, 255, 0), 2)
        cv2.line(frame, (self.center_x - 20, self.center_y), 
                 (self.center_x + 20, self.center_y), (0, 255, 0), 1)
        cv2.line(frame, (self.center_x, self.center_y - 20), 
                 (self.center_x, self.center_y + 20), (0, 255, 0), 1)
        
        # Dessin du visage détecté
        if face_info is not None:
            x_center, y_center, width, height, confidence = face_info
            
            # Rectangle autour du visage
            x1 = x_center - width // 2
            y1 = y_center - height // 2
            x2 = x_center + width // 2
            y2 = y_center + height // 2
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            # Point au centre du visage
            cv2.circle(frame, (x_center, y_center), 5, (0, 0, 255), -1)
            
            # Ligne entre le centre de l'image et le centre du visage
            cv2.line(frame, (self.center_x, self.center_y), 
                     (x_center, y_center), (255, 0, 0), 2)
            
            # Texte avec la confiance
            cv2.putText(frame, f"Conf: {confidence:.2f}", 
                       (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (0, 255, 0), 2)
        else:
            # Aucun visage détecté
            cv2.putText(frame, "Aucun visage detecte", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (0, 0, 255), 2)
        
        # Affichage des informations de contrôle
        vx, vy = velocity
        info_text = [
            f"FPS: {self.fps:.1f}",
            f"Yaw: {vx} deg/s",
            f"Up/Down: {-vy} cm/s",
            f"Batterie: {self.tello.get_battery()}%"
        ]
        
        y_offset = 30
        for text in info_text:
            cv2.putText(frame, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 25
        
        return frame
    
    def run(self):
        """
        Boucle principale de tracking.
        """
        print("\n=== Demarrage du tracking ===")
        print("Appuyez sur 'q' pour quitter")
        print("Appuyez sur 't' pour decoller/atterrir")
        print("Appuyez sur 'w/a/s/d' pour controle manuel")
        print("Appuyez sur 'r' pour reset les parametres PID\n")
        
        # Initialisation du centre de l'image (sera mis à jour avec la première frame)
        frame = self.get_frame()
        if frame is None:
            print("Erreur: Impossible de recevoir des frames du drone.")
            self.cleanup()
            return
        
        h, w = frame.shape[:2]
        self.center_x = w // 2
        self.center_y = h // 2
        
        # État du drone
        is_flying = False
        
        try:
            while True:
                # Récupération de la frame
                frame = self.get_frame()
                if frame is None:
                    continue
                
                # Détection du visage
                face_info = self.detect_face(frame)
                
                # Calcul des commandes de contrôle
                if face_info is not None:
                    x_center, y_center, _, _, _ = face_info
                    velocity_x, velocity_y = self.calculate_control((x_center, y_center))
                    self.no_detection_count = 0
                else:
                    # Aucun visage détecté - arrêter le mouvement
                    velocity_x, velocity_y = 0, 0
                    self.no_detection_count += 1
                    
                    # Si aucun visage détecté pendant trop longtemps, atterrir
                    if self.no_detection_count > self.max_no_detection and is_flying:
                        print("Aucun visage detecte depuis trop longtemps. Atterrissage...")
                        self.tello.land()
                        is_flying = False
                
                # Application des commandes si le drone vole
                if is_flying:
                    # Le Tello utilise send_rc_control avec:
                    # left_right_velocity: mouvement latéral (cm/s)
                    # forward_backward_velocity: mouvement avant/arrière (cm/s)
                    # up_down_velocity: mouvement vertical (cm/s), positif = monter
                    # yaw_velocity: rotation (deg/s), positif = tourner à droite
                    
                    # Pour centrer le visage:
                    # - Horizontal: utiliser yaw (rotation) pour tourner vers le visage
                    # - Vertical: utiliser up_down pour monter/descendre
                    self.tello.send_rc_control(
                        left_right_velocity=0,           # Pas de mouvement latéral
                        forward_backward_velocity=0,     # Pas de mouvement avant/arrière
                        up_down_velocity=-velocity_y,     # Mouvement vertical (inversé: visage en haut = descendre)
                        yaw_velocity=velocity_x          # Rotation pour centrer horizontalement
                    )
                
                # Dessin de l'overlay
                frame = self.draw_overlay(frame, face_info, (velocity_x, velocity_y))
                
                # Affichage de la frame
                cv2.imshow("Tello Face Tracking", frame)
                
                # Gestion des touches clavier
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Arret demande par l'utilisateur...")
                    break
                elif key == ord('t'):
                    if not is_flying:
                        print("Decollage...")
                        self.tello.takeoff()
                        is_flying = True
                    else:
                        print("Atterrissage...")
                        self.tello.land()
                        is_flying = False
                elif key == ord('w') and is_flying:
                    self.tello.send_rc_control(0, 20, 0, 0)  # Avancer
                elif key == ord('s') and is_flying:
                    self.tello.send_rc_control(0, -20, 0, 0)  # Reculer
                elif key == ord('a') and is_flying:
                    self.tello.send_rc_control(-20, 0, 0, 0)  # Gauche
                elif key == ord('d') and is_flying:
                    self.tello.send_rc_control(20, 0, 0, 0)  # Droite
                
                # Calcul du FPS
                self.frame_count += 1
                elapsed = time.time() - self.start_time
                if elapsed > 0:
                    self.fps = self.frame_count / elapsed
                
        except KeyboardInterrupt:
            print("\nInterruption clavier detectee...")
        except Exception as e:
            print(f"Erreur dans la boucle principale: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        Nettoie les ressources et atterrit le drone.
        """
        print("\nNettoyage des ressources...")
        try:
            if self.tello.is_flying:
                print("Atterrissage du drone...")
                self.tello.land()
        except:
            pass
        
        try:
            self.tello.streamoff()
            self.tello.end()
        except:
            pass
        
        cv2.destroyAllWindows()
        print("Nettoyage termine.")


def main():
    """
    Fonction principale.
    """
    # Vérification des arguments
    model_path = "yolov8n-face.pt"
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    
    # Création et lancement du tracker
    tracker = FaceTracker(model_path=model_path, conf_threshold=0.25)
    tracker.run()


if __name__ == "__main__":
    main()

