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
from typing import Optional, Tuple, Dict, Any
import sys
import os
import subprocess
import platform
import threading

# Ne pas forcer xcb ici car cela peut causer des conflits avec PyQt6
# La configuration Qt sera gérée par PyQt6 si nécessaire

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


def get_resource_path(relative_path: str) -> str:
    """
    Obtient le chemin absolu vers une ressource, fonctionne pour le dev et PyInstaller.
    
    Args:
        relative_path: Chemin relatif vers la ressource
        
    Returns:
        Chemin absolu vers la ressource
    """
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # En mode développement, utiliser le répertoire du script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


class WindowsFrameRead:
    """
    Wrapper optimisé pour la lecture de frames sous Windows.
    Utilise un thread en arrière-plan pour lire les frames dans un buffer,
    évitant ainsi les appels bloquants et améliorant les performances.
    """
    def __init__(self, cap, timeout: float = 5.0):
        """
        Initialise le lecteur de frames avec buffer.
        
        Args:
            cap: Objet cv2.VideoCapture
            timeout: Timeout en secondes pour l'initialisation
        """
        self.cap = cap
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.running = True
        self.frame_available = threading.Event()
        
        # Thread pour lire les frames en arrière-plan
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()
        
        # Attendre que la première frame soit disponible
        if self.frame_available.wait(timeout=timeout):
            print("✓ Buffer de frames Windows initialisé")
        else:
            print("⚠ Attention: Timeout lors de l'initialisation du buffer")
    
    def _read_loop(self):
        """Boucle de lecture des frames en arrière-plan"""
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    with self.frame_lock:
                        self.latest_frame = frame
                        self.frame_available.set()
                else:
                    # Si la lecture échoue, attendre un peu avant de réessayer
                    time.sleep(0.01)
            except Exception as e:
                # En cas d'erreur, continuer la boucle
                time.sleep(0.01)
                continue
    
    @property
    def frame(self):
        """Retourne la dernière frame disponible (non-bloquant)"""
        with self.frame_lock:
            if self.latest_frame is not None:
                # Retourner une copie pour éviter les problèmes de concurrence
                return self.latest_frame.copy()
            return None
    
    def stop(self):
        """Arrête le thread de lecture"""
        self.running = False
        if self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)


class TelloWiFiManager:
    """
    Gestionnaire Wi-Fi automatique pour se connecter au drone Tello.
    Détecte et se connecte automatiquement au réseau Wi-Fi du Tello,
    puis restaure la connexion précédente après utilisation.
    """
    
    def __init__(self, tello_ssid_pattern: str = "TELLO"):
        """
        Initialise le gestionnaire Wi-Fi.
        
        Args:
            tello_ssid_pattern: Motif pour identifier le réseau Tello (par défaut: "TELLO")
        """
        self.tello_ssid_pattern = tello_ssid_pattern.upper()
        self.original_connection = None
        self.tello_ssid = None
        self.is_connected_to_tello = False
        
    def check_network_manager(self) -> bool:
        """
        Vérifie si NetworkManager (nmcli) est disponible.
        
        Returns:
            True si nmcli est disponible, False sinon
        """
        try:
            result = subprocess.run(
                ['which', 'nmcli'],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except:
            return False
    
    def get_current_connection(self) -> Optional[str]:
        """
        Récupère le nom de la connexion Wi-Fi actuelle.
        
        Returns:
            Nom de la connexion actuelle ou None
        """
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'NAME,DEVICE,TYPE', 'connection', 'show', '--active'],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.strip().split('\n'):
                if line and 'wifi' in line.lower():
                    parts = line.split(':')
                    if len(parts) >= 2:
                        return parts[0]
            return None
        except subprocess.CalledProcessError:
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de la connexion actuelle: {e}")
            return None
    
    def scan_for_tello(self, timeout: int = 30) -> Optional[str]:
        """
        Scanne les réseaux Wi-Fi disponibles pour trouver le Tello.
        
        Args:
            timeout: Temps maximum d'attente en secondes
            
        Returns:
            SSID du réseau Tello trouvé ou None
        """
        print(f"Recherche du réseau Tello (motif: {self.tello_ssid_pattern})...")
        print("Assurez-vous que le drone Tello est allumé et en mode Wi-Fi.")
        
        start_time = time.time()
        attempts = 0
        max_attempts = timeout // 5
        
        while time.time() - start_time < timeout:
            attempts += 1
            print(f"Tentative {attempts}/{max_attempts}...")
            
            try:
                # Scanner les réseaux Wi-Fi
                result = subprocess.run(
                    ['nmcli', '-t', '-f', 'SSID,SIGNAL', 'device', 'wifi', 'list'],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10
                )
                
                # Chercher le réseau Tello
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 1:
                            ssid = parts[0].strip()
                            if self.tello_ssid_pattern in ssid.upper():
                                print(f"✓ Réseau Tello trouvé: {ssid}")
                                return ssid
                
                time.sleep(5)
                
            except subprocess.TimeoutExpired:
                print("Timeout lors du scan, nouvelle tentative...")
                continue
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors du scan: {e}")
                time.sleep(5)
                continue
            except Exception as e:
                print(f"Erreur inattendue: {e}")
                time.sleep(5)
                continue
        
        print("✗ Réseau Tello non trouvé après le timeout.")
        return None
    
    def connect_to_tello(self, ssid: Optional[str] = None) -> bool:
        """
        Se connecte au réseau Wi-Fi du Tello.
        
        Args:
            ssid: SSID du réseau Tello (si None, scanne d'abord)
            
        Returns:
            True si la connexion réussit, False sinon
        """
        if not self.check_network_manager():
            print("✗ Erreur: NetworkManager (nmcli) n'est pas disponible.")
            print("  Installez NetworkManager avec: sudo apt-get install network-manager")
            return False
        
        # Sauvegarder la connexion actuelle
        self.original_connection = self.get_current_connection()
        if self.original_connection:
            print(f"Connexion actuelle sauvegardée: {self.original_connection}")
        
        # Trouver le SSID du Tello si non fourni
        if ssid is None:
            ssid = self.scan_for_tello()
            if ssid is None:
                return False
        
        self.tello_ssid = ssid
        
        # Se connecter au réseau Tello
        print(f"Connexion au réseau {ssid}...")
        try:
            # Essayer de se connecter au réseau
            result = subprocess.run(
                ['nmcli', 'device', 'wifi', 'connect', ssid],
                capture_output=True,
                text=True,
                check=False,
                timeout=30
            )
            
            if result.returncode == 0:
                # Attendre que la connexion soit établie
                print("Attente de l'établissement de la connexion...")
                time.sleep(5)
                
                # Vérifier la connexion
                current = self.get_current_connection()
                if current and ssid in current:
                    print(f"✓ Connecté au réseau {ssid}")
                    self.is_connected_to_tello = True
                    return True
                else:
                    print("✗ La connexion n'a pas pu être établie.")
                    return False
            else:
                print(f"✗ Erreur lors de la connexion: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ Timeout lors de la connexion.")
            return False
        except Exception as e:
            print(f"✗ Erreur lors de la connexion: {e}")
            return False
    
    def restore_connection(self) -> bool:
        """
        Restaure la connexion Wi-Fi précédente.
        
        Returns:
            True si la restauration réussit, False sinon
        """
        if not self.is_connected_to_tello:
            return True  # Rien à restaurer
        
        if self.original_connection is None:
            print("Aucune connexion précédente à restaurer.")
            return True
        
        print(f"Restauration de la connexion: {self.original_connection}...")
        
        try:
            result = subprocess.run(
                ['nmcli', 'connection', 'up', self.original_connection],
                capture_output=True,
                text=True,
                check=False,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✓ Connexion restaurée: {self.original_connection}")
                self.is_connected_to_tello = False
                return True
            else:
                print(f"✗ Erreur lors de la restauration: {result.stderr}")
                print("  Vous devrez peut-être vous reconnecter manuellement.")
                return False
                
        except Exception as e:
            print(f"✗ Erreur lors de la restauration: {e}")
            return False
    
    def auto_connect(self) -> bool:
        """
        Méthode principale pour se connecter automatiquement au Tello.
        Scanne, se connecte et sauvegarde l'état.
        
        Returns:
            True si la connexion réussit, False sinon
        """
        return self.connect_to_tello()
    
    def cleanup(self):
        """
        Nettoie et restaure la connexion précédente.
        """
        if self.is_connected_to_tello:
            self.restore_connection()


class FaceTracker:
    """
    Classe principale pour le tracking de visage avec le drone Tello.
    """
    
    def __init__(self, model_path: str = "yolov8n-face.pt", conf_threshold: float = 0.25, 
                 auto_wifi: bool = True, tello_ssid: Optional[str] = None,
                 gui_mode: bool = False, detection_resolution: Tuple[int, int] = (640, 480)):
        """
        Initialise le tracker de visage.
        
        Args:
            model_path: Chemin vers le modèle YOLO-face (.pt)
            conf_threshold: Seuil de confiance pour la détection (0.0-1.0)
            auto_wifi: Active la gestion automatique Wi-Fi (True par défaut, forcé à False sous Windows)
            tello_ssid: SSID du réseau Tello (si None, sera détecté automatiquement)
            gui_mode: Active le mode GUI (désactive les prompts interactifs)
            detection_resolution: Résolution pour la détection YOLO (largeur, hauteur). Plus petit = plus rapide.
        """
        self.gui_mode = gui_mode
        
        # Détection automatique de Windows : désactiver la gestion WiFi automatique
        # La gestion WiFi automatique utilise nmcli (Linux uniquement)
        if platform.system() == "Windows" and auto_wifi:
            print("\n=== Plateforme Windows détectée ===")
            print("La gestion automatique Wi-Fi est désactivée sous Windows.")
            print("Veuillez vous connecter manuellement au réseau Wi-Fi du Tello avant de continuer.")
            print("=" * 50 + "\n")
            auto_wifi = False
        # Gestionnaire Wi-Fi automatique
        self.wifi_manager = None
        if auto_wifi:
            print("\n=== Gestion automatique Wi-Fi ===")
            self.wifi_manager = TelloWiFiManager()
            if tello_ssid:
                print(f"Connexion au réseau spécifié: {tello_ssid}")
                if not self.wifi_manager.connect_to_tello(tello_ssid):
                    print("\n⚠ ATTENTION: Échec de la connexion Wi-Fi automatique.")
                    print("  Vous pouvez continuer si vous êtes déjà connecté manuellement au réseau Tello.")
                    if not self.gui_mode:
                        response = input("Continuer quand même? (o/n): ")
                        if response.lower() != 'o':
                            sys.exit(0)
            else:
                if not self.wifi_manager.auto_connect():
                    print("\n⚠ ATTENTION: Échec de la connexion Wi-Fi automatique.")
                    print("  Vous pouvez continuer si vous êtes déjà connecté manuellement au réseau Tello.")
                    if not self.gui_mode:
                        response = input("Continuer quand même? (o/n): ")
                        if response.lower() != 'o':
                            sys.exit(0)
            print("=" * 40 + "\n")
        
        # Chargement du modèle YOLO
        # Si le chemin est relatif, essayer de le trouver dans les ressources PyInstaller
        if not os.path.isabs(model_path) and not os.path.exists(model_path):
            # Essayer de trouver le modèle dans les ressources PyInstaller
            resource_path = get_resource_path(model_path)
            if os.path.exists(resource_path):
                model_path = resource_path
        
        print(f"Chargement du modèle YOLO depuis {model_path}...")
        if not os.path.exists(model_path):
            print(f"Erreur: Le fichier {model_path} n'existe pas.")
            print("Assurez-vous que le modèle est présent dans le répertoire courant.")
            if self.wifi_manager:
                self.wifi_manager.cleanup()
            sys.exit(1)
        
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        
        # Initialisation du drone Tello
        print("Connexion au drone Tello...")
        
        # Vérifier la connectivité réseau avant de se connecter
        import socket
        tello_ip = "192.168.10.1"
        tello_port = 8889
        
        print(f"Vérification de l'accessibilité du Tello ({tello_ip})...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            # Essayer de se connecter (UDP est connectionless, mais on peut tester)
            sock.connect((tello_ip, tello_port))
            sock.close()
            print(f"✓ IP du Tello accessible: {tello_ip}")
        except Exception as e:
            print(f"⚠ ATTENTION: Problème de connectivité réseau: {e}")
            print("Vérifiez que vous êtes connecté au Wi-Fi du Tello")
        
        self.tello = Tello(host=tello_ip)
        
        # Tentative de connexion avec gestion d'erreur améliorée
        try:
            print("Tentative de connexion au Tello...")
            self.tello.connect()
            print("✓ Connexion établie avec succès")
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Erreur de connexion: {error_msg}")
            
            if self.wifi_manager:
                self.wifi_manager.cleanup()
            sys.exit(1)
        
        # Vérification de la batterie
        try:
            battery = self.tello.get_battery()
            print(f"Niveau de batterie: {battery}%")
            if battery < 20:
                print("ATTENTION: Batterie faible! Chargez le drone avant de continuer.")
                if not self.gui_mode:
                    response = input("Continuer quand même? (o/n): ")
                    if response.lower() != 'o':
                        self.tello.end()
                        sys.exit(0)
        except Exception as e:
            print(f"⚠ Impossible de lire le niveau de batterie: {e}")
            print("Continuons quand même...")
        
        # Configuration du flux vidéo
        # Initialisation d'une variable pour stocker le VideoCapture Windows si nécessaire
        self._windows_video_cap = None
        
        try:
            self.tello.streamon()
            
            # Correction pour Windows : contourner le problème de bind() [Errno 10014]
            if platform.system() == "Windows":
                print("Mode compatibilité Windows activé pour le flux vidéo...")
                tello_ip = "192.168.10.1"
                
                # Essayer différents formats compatibles Windows
                formats_to_try = [
                    f"udp://{tello_ip}:11111",
                    f"udp://@{tello_ip}:11111",
                    f"udp://0.0.0.0:11111",
                ]
                
                cap = None
                for fmt in formats_to_try:
                    try:
                        cap = cv2.VideoCapture(fmt, cv2.CAP_FFMPEG)
                        if cap.isOpened():
                            # Tester en lisant une frame
                            ret, test_frame = cap.read()
                            if ret and test_frame is not None:
                                print(f"✓ Flux vidéo ouvert avec le format: {fmt}")
                                break
                        if cap:
                            cap.release()
                        cap = None
                    except Exception as fmt_error:
                        if cap:
                            cap.release()
                        cap = None
                        continue
                
                if cap and cap.isOpened():
                    # OPTIMISATION : Utiliser un thread pour lire les frames en arrière-plan
                    # Cela évite les appels bloquants et améliore considérablement les performances
                    self.frame_read = WindowsFrameRead(cap)
                    self._windows_video_cap = cap  # Garder une référence pour le cleanup
                else:
                    # Fallback : utiliser la méthode standard (peut échouer)
                    print("⚠ Tentative avec la méthode standard djitellopy...")
                    self.frame_read = self.tello.get_frame_read()
            else:
                # Linux/Mac : méthode standard
                self.frame_read = self.tello.get_frame_read()
                
        except Exception as e:
            error_str = str(e).lower()
            print(f"Erreur lors du démarrage du flux vidéo: {e}")
            
            # Détecter les erreurs de bind (Windows Errno 10014 ou Linux "bind failed")
            if "bind failed" in error_str or "adresse déjà utilisée" in error_str or "10014" in str(e) or "wsaefault" in error_str:
                print("Le port du flux vidéo est déjà utilisé ou format d'adresse incompatible.")
                print("Tentative de correction pour Windows...")
                
                # Essayer de nettoyer d'abord
                try:
                    self.tello.streamoff()
                    time.sleep(1)
                    self.tello.streamon()
                    
                    # Réessayer avec la méthode Windows si on est sous Windows
                    if platform.system() == "Windows":
                        tello_ip = "192.168.10.1"
                        formats_to_try = [
                            f"udp://{tello_ip}:11111",
                            f"udp://@{tello_ip}:11111",
                            f"udp://0.0.0.0:11111",
                        ]
                        
                        cap = None
                        for fmt in formats_to_try:
                            try:
                                cap = cv2.VideoCapture(fmt, cv2.CAP_FFMPEG)
                                if cap.isOpened():
                                    ret, test_frame = cap.read()
                                    if ret and test_frame is not None:
                                        print(f"✓ Flux vidéo redémarré avec le format: {fmt}")
                                        break
                                if cap:
                                    cap.release()
                                cap = None
                            except Exception:
                                if cap:
                                    cap.release()
                                cap = None
                                continue
                        
                        if cap and cap.isOpened():
                            # Utiliser la classe WindowsFrameRead optimisée avec thread
                            self.frame_read = WindowsFrameRead(cap, timeout=3.0)
                            self._windows_video_cap = cap
                            print("Flux vidéo redémarré avec succès (mode Windows).")
                        else:
                            raise Exception("Impossible d'ouvrir le flux vidéo avec OpenCV")
                    else:
                        # Linux/Mac : réessayer la méthode standard
                        self.frame_read = self.tello.get_frame_read()
                        print("Flux vidéo redémarré avec succès.")
                        
                except Exception as e2:
                    print(f"Impossible de redémarrer le flux: {e2}")
                    if not self.gui_mode:
                        response = input("Continuer sans flux vidéo? (o/n): ")
                        if response.lower() != 'o':
                            self.tello.end()
                            sys.exit(0)
            else:
                raise
        
        # Paramètres de contrôle
        self.center_x = 0  # Centre horizontal de l'image (sera mis à jour)
        self.center_y = 0  # Centre vertical de l'image (sera mis à jour)

        # Hauteur maximale du drone
        self.max_height_cm = 180
        
        # Paramètres PID pour le contrôle du drone
        # Ces valeurs peuvent être ajustées selon les besoins
        # Réduits pour éviter les oscillations
        self.kp_x = 0.15   # Gain proportionnel horizontal (yaw) - réduit pour mouvements plus doux
        self.kp_y = 0.12   # Gain proportionnel vertical - réduit pour mouvements plus doux
        self.kd_x = 0.25   # Gain dérivé horizontal (réduit les oscillations) - augmenté pour mieux amortir
        self.kd_y = 0.2    # Gain dérivé vertical - augmenté pour mieux amortir
        
        # Variables pour le contrôle PID
        self.last_error_x = 0
        self.last_error_y = 0
        
        # Variables pour la gestion des latences
        self.last_control_time = time.time() # Temps de la dernière commande de contrôle
        self.expected_frame_time = 1.0 / 30.0 # Temps attendu pour une frame
        self.max_dt = 0.5 # Temps maximal de latence accepté

        # Vitesse maximale du drone
        self.max_speed_yaw = 30      # deg/s pour la rotation
        self.max_speed_vertical = 30  # cm/s pour le mouvement vertical
        self.max_speed_horizontal = 40  # cm/s pour le mouvement latéral (gauche/droite) - augmenté
        self.max_speed_forward = 50     # cm/s pour le mouvement avant/arrière - augmenté significativement
        
        # Zone morte (dead zone) pour éviter les micro-mouvements
        self.dead_zone = 40  # pixels 
        
        # Taille cible du visage (en pixels) pour le contrôle avant/arrière
        self.target_face_size = 150  # Taille cible du visage en pixels (ajustable)
        self.face_size_tolerance = 30  # Tolérance autour de la taille cible
        
        # Compteur de frames sans détection
        self.no_detection_count = 0
        self.max_no_detection = 1800000  # Arrêter après 180 frames sans détection
        
        # Statistiques
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()

        # Envoi des commandes RC toutes les 3 frames
        self.rc_command_counter = 0
        self.rc_command_interval = 3
        
        # OPTIMISATION : Résolution pour la détection YOLO (plus petit = plus rapide)
        self.detection_width, self.detection_height = detection_resolution
        self.frame_skip_interval = 2  # Traiter 1 frame sur 2 pour améliorer les performances
        self._last_face_info = None  # Cache pour la dernière détection
        
        # Flag pour éviter les appels multiples de cleanup
        self._cleaning = False
        
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Récupère une frame du flux vidéo du Tello.
        
        Returns:
            Frame en format numpy array (BGR) ou None si erreur
        """
        try:
            frame = self.frame_read.frame
            if frame is not None:
                if not hasattr(self, 'last_frame_hash'):
                    self.last_frame_hash = hash(frame.tobytes())
                    return frame
                
                current_frame_hash = hash(frame.tobytes())
                if current_frame_hash != self.last_frame_hash:
                    self.last_frame_hash = current_frame_hash
                    return frame
                else:
                    return None

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
        # OPTIMISATION : Redimensionner la frame pour accélérer YOLO
        # Garder les dimensions originales pour le calcul des coordonnées
        original_h, original_w = frame.shape[:2]
        
        # Redimensionner à une résolution plus petite pour YOLO
        # Cela accélère considérablement la détection (4x plus rapide pour 640x480 vs 1280x720)
        target_width = self.detection_width
        target_height = self.detection_height
        
        # Calculer le ratio de redimensionnement
        scale_x = original_w / target_width
        scale_y = original_h / target_height
        
        # Redimensionner la frame pour YOLO
        small_frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
        
        # Exécution de la détection YOLO sur la frame réduite
        # Utiliser imgsz pour correspondre à notre redimensionnement
        results = self.model(small_frame, conf=self.conf_threshold, imgsz=target_width, verbose=False)
        
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
            
            # Coordonnées de la bounding box (sur la frame réduite)
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = box.conf[0].cpu().numpy()
            
            # Convertir les coordonnées de la frame réduite vers la frame originale
            x_center = int((x1 + x2) / 2 * scale_x)
            y_center = int((y1 + y2) / 2 * scale_y)
            width = int((x2 - x1) * scale_x)
            height = int((y2 - y1) * scale_y)
            
            return (x_center, y_center, width, height, confidence)
        
        return None
    
    def calculate_control(self, face_info: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """
        Calcule les commandes de contrôle du drone pour centrer le visage.
        
        Args:
            face_info: Tuple (x_center, y_center, width, height) du visage détecté
            
        Returns:
            Tuple (left_right, forward_backward, up_down, yaw) en cm/s ou deg/s
        """
        x_center, y_center, width, height = face_info
        
        # Calcul de l'erreur (différence entre le centre du visage et le centre de l'image)
        error_x = x_center - self.center_x
        error_y = y_center - self.center_y
        
        # Calcul de la taille du visage (utiliser la moyenne de width et height)
        face_size = (width + height) / 2
        error_size = face_size - self.target_face_size
        
        # Application de la zone morte
        if abs(error_x) < self.dead_zone:
            error_x = 0
        if abs(error_y) < self.dead_zone:
            error_y = 0
        if abs(error_size) < self.face_size_tolerance:
            error_size = 0
        
        # Calcul du temps écoulé depuis la dernière commande
        current_time = time.time()
        dt = current_time - self.last_control_time
        
        # Protection contre les valeurs aberrantes (première frame ou latence excessive)
        if dt <= 0 or dt > self.max_dt:
            dt = self.expected_frame_time  # Utiliser le temps attendu par défaut
        
        # Normaliser le temps pour un FPS de référence (30 FPS)
        dt_normalized = dt / self.expected_frame_time
        
        # Détection d'oscillations : si l'erreur change de signe rapidement, réduire la réactivité
        oscillation_x = (error_x * self.last_error_x < 0) if self.last_error_x != 0 else False
        oscillation_y = (error_y * self.last_error_y < 0) if self.last_error_y != 0 else False
        
        # Facteur de réduction si oscillation détectée
        damping_factor = 0.5 if (oscillation_x or oscillation_y) else 1.0
        
        # Facteur de réduction supplémentaire si latence élevée détectée
        # Plus la latence est élevée, plus on réduit la réactivité pour éviter les sur-corrections
        latency_factor = 1.0
        if dt > self.expected_frame_time * 2:  # Si latence > 2x le temps attendu
            latency_factor = min(1.0, self.expected_frame_time * 2 / dt)
        
        # Contrôle PID pour le mouvement horizontal (gauche/droite)
        p_x = self.kp_x * error_x * damping_factor * latency_factor
        # Dérivée normalisée par le temps écoulé
        d_x = self.kd_x * (error_x - self.last_error_x) / dt_normalized
        left_right = int(p_x + d_x)
        
        # Contrôle PID pour le mouvement vertical (monter/descendre)
        p_y = self.kp_y * error_y * damping_factor * latency_factor
        # Dérivée normalisée par le temps écoulé
        d_y = self.kd_y * (error_y - self.last_error_y) / dt_normalized
        up_down = int(p_y + d_y)
        
        # Si le drone est trop haut, ne pas monter
        try:
            current_height = self.tello.get_height()
            if current_height > self.max_height_cm and up_down > 0:
                up_down = 0
                print(f"Hauteur maximale atteinte: {current_height} cm")
        except Exception as e:
            print(f"Erreur lors de la récupération de l'altitude: {e}")
            pass


        # Contrôle pour le mouvement avant/arrière basé sur la taille du visage
        # Si le visage est trop petit, avancer. Si trop grand, reculer.
        # Coefficient augmenté pour des mouvements plus rapides
        forward_backward = int(-error_size * 0.4)  # Coefficient augmenté de 0.1 à 0.4 pour plus de réactivité
        
        # Rotation (yaw) - utiliser seulement si le mouvement latéral n'est pas suffisant
        # Réduire le yaw si on utilise le mouvement latéral
        yaw = int(left_right * 0.3) if abs(error_x) > self.dead_zone * 2 else 0
        
        # Réduction supplémentaire si l'erreur est petite (approche du centre)
        if abs(error_x) < self.dead_zone * 2:
            left_right = int(left_right * 0.6)
            yaw = int(yaw * 0.6)
        if abs(error_y) < self.dead_zone * 2:
            up_down = int(up_down * 0.6)
        # Réduction moins importante pour le mouvement avant/arrière pour garder la réactivité
        if abs(error_size) < self.face_size_tolerance * 2:
            forward_backward = int(forward_backward * 0.8)  # Réduction réduite de 0.6 à 0.8
        
        # Limitation des vitesses
        left_right = int(np.clip(left_right, -self.max_speed_horizontal, self.max_speed_horizontal))
        forward_backward = int(np.clip(forward_backward, -self.max_speed_forward, self.max_speed_forward))
        up_down = int(np.clip(up_down, -self.max_speed_vertical, self.max_speed_vertical))
        yaw = int(np.clip(yaw, -self.max_speed_yaw, self.max_speed_yaw))
        
        # Mise à jour des erreurs précédentes
        self.last_error_x = error_x
        self.last_error_y = error_y

        # Mise à jour du temps de contrôle
        self.last_control_time = current_time
        
        return (left_right, forward_backward, up_down, yaw)
    
    def draw_overlay(self, frame: np.ndarray, face_info: Optional[Tuple], 
                     velocity: Tuple[int, int, int, int]) -> np.ndarray:
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
        
        # Recalculer le centre de l'image pour cette frame (au cas où les dimensions changent)
        self.center_x = w // 2
        self.center_y = h // 2
        
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
        left_right, forward_backward, up_down, yaw = velocity
        try:
            current_height = self.tello.get_height()
            height_text = f"Hauteur: {current_height} cm"
            if current_height >= self.max_height_cm:
                height_text += " (MAX)"
        except Exception as e:
            height_text = "Hauteur: N/A"
            
        info_text = [
            height_text,
            f"FPS: {self.fps:.1f}",
            f"Gauche/Droite: {left_right} cm/s",
            f"Avant/Arriere: {forward_backward} cm/s",
            f"Monter/Descendre: {-up_down} cm/s",
            f"Rotation: {yaw} deg/s",
            height_text,
            f"Batterie: {self.tello.get_battery()}%"
        ]
        
        y_offset = 30
        for text in info_text:
            cv2.putText(frame, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 25
        
        return frame
    
    def _convert_frame_to_qimage(self, frame: np.ndarray):
        """
        Convertit une frame OpenCV (BGR) en QImage (RGB) pour PyQt6.
        Optimisé pour éviter les copies inutiles.
        
        Args:
            frame: Frame OpenCV en format BGR numpy array
            
        Returns:
            QImage en format RGB
        """
        try:
            from PyQt6.QtGui import QImage
            
            if frame is None or frame.size == 0:
                return None
            
            # Convertir BGR vers RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Obtenir les dimensions
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            
            # Créer QImage directement depuis les données numpy
            # Utiliser constData pour éviter les copies si possible
            qimage = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Copier les données pour éviter les problèmes de mémoire
            # (nécessaire car rgb_frame peut être libéré)
            return qimage.copy()
        except ImportError:
            # Si PyQt6 n'est pas disponible, retourner None
            return None
        except Exception as e:
            # Ne pas imprimer d'erreur à chaque frame pour éviter la saturation
            return None
    
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
        
        # OPTIMISATION : Compteur pour sauter des frames (traiter 1 frame sur N)
        frame_skip_counter = 0
        
        try:
            while True:
                # Récupération de la frame
                frame = self.get_frame()
                if frame is None:
                    continue
                
                # OPTIMISATION : Sauter certaines frames pour la détection
                # Cela améliore les performances en traitant moins de frames
                frame_skip_counter += 1
                should_detect = (frame_skip_counter % self.frame_skip_interval == 0)
                
                # Détection du visage (seulement toutes les N frames)
                if should_detect:
                    face_info = self.detect_face(frame)
                    # Sauvegarder la dernière détection pour les frames sautées
                    if face_info is not None:
                        self._last_face_info = face_info
                else:
                    # Réutiliser la dernière détection pour les frames sautées
                    face_info = self._last_face_info
                
                # Calcul des commandes de contrôle
                if face_info is not None:
                    x_center, y_center, width, height, _ = face_info
                    left_right, forward_backward, up_down, yaw = self.calculate_control((x_center, y_center, width, height))
                    self.no_detection_count = 0
                else:
                    # Aucun visage détecté - arrêter le mouvement
                    left_right, forward_backward, up_down, yaw = 0, 0, 0, 0
                    self.no_detection_count += 1
                    
                    # Si aucun visage détecté pendant trop longtemps, atterrir
                    #if self.no_detection_count > self.max_no_detection and is_flying:
                    #    print("Aucun visage detecte depuis trop longtemps. Atterrissage...")
                    #    self.tello.send_rc_control(0, 0, 0, 0)
                    #    time.sleep(1)
                    #    self.tello.land()
                    #    is_flying = False
                
                # Application des commandes si le drone vole
                if is_flying:
                    # Le Tello utilise send_rc_control avec:
                    # left_right_velocity: mouvement latéral (cm/s)
                    # forward_backward_velocity: mouvement avant/arrière (cm/s)
                    # up_down_velocity: mouvement vertical (cm/s), positif = monter
                    # yaw_velocity: rotation (deg/s), positif = tourner à droite
                    
                    # Si le drone est trop haut, ne pas monter
                    try:
                        current_height = self.tello.get_height()
                        if current_height > self.max_height_cm and up_down > 0:
                            up_down = 0
                    except Exception as e:
                        pass

                    # Pour centrer le visage:
                    # - Horizontal: mouvement latéral (gauche/droite) + rotation légère
                    # - Vertical: monter/descendre
                    # - Distance: avancer/reculer selon la taille du visage
                    self.rc_command_counter += 1
                    if self.rc_command_counter >= self.rc_command_interval:
                            self.tello.send_rc_control(
                                left_right_velocity=left_right,      # Mouvement latéral (gauche/droite)
                                forward_backward_velocity=forward_backward,  # Avancer/reculer
                                up_down_velocity=-up_down,          # Mouvement vertical (inversé: visage en haut = descendre)
                                yaw_velocity=yaw                     # Rotation légère pour ajustement fin
                            )
                            self.rc_command_counter = 0
                    #else:
                    #    self.tello.send_rc_control(0, 0, 0, 0)
                
                # Dessin de l'overlay
                frame = self.draw_overlay(frame, face_info, (left_right, forward_backward, up_down, yaw))
                
                # Affichage de la frame
                cv2.imshow("Tello Face Tracking", frame)
                
                # Gestion des touches clavier
                key = cv2.waitKey(1) & 0xFF
                if key == ord('a'):
                    print("Arret demande par l'utilisateur...")
                    break
                elif key == ord('t'):
                    if not is_flying:
                        print("Decollage...")
                        self.tello.takeoff()
                        is_flying = True
                        time.sleep(3)
                    else:
                        print("Atterrissage...")
                        self.tello.send_rc_control(0, 0, 0, 0)
                        time.sleep(1)
                        self.tello.land()
                        is_flying = False
                elif key == ord('z') and is_flying:
                    self.tello.send_rc_control(0, 20, 0, 0)  # Avancer
                elif key == ord('s') and is_flying:
                    self.tello.send_rc_control(0, -20, 0, 0)  # Reculer
                elif key == ord('q') and is_flying:
                    self.tello.send_rc_control(-20, 0, 0, 0)  # Gauche
                elif key == ord('d') and is_flying:
                    self.tello.send_rc_control(20, 0, 0, 0)  # Droite
                elif key == 82 and is_flying:
                    self.tello.send_rc_control(0, 0, 20, 0)  # Monter
                elif key == 84 and is_flying:
                    self.tello.send_rc_control(0, 0, -20, 0)  # Descendre
                elif key == 83 and is_flying:
                    self.tello.send_rc_control(0, 0, 0, 20)  # Tourner à droite
                elif key == 81 and is_flying:
                    self.tello.send_rc_control(0, 0, 0, -20)  # Tourner à gauche
                elif key == ord(' ') and is_flying:
                    self.tello.send_rc_control(0, 0, 0, 0)  # Stop
                
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
        Cette méthode est idempotente (peut être appelée plusieurs fois sans erreur).
        """
        # Éviter les appels multiples
        if hasattr(self, '_cleaning') and self._cleaning:
            return
        self._cleaning = True
        
        print("\nNettoyage des ressources...")
        
        # Atterrissage du drone si nécessaire
        try:
            if hasattr(self, 'tello') and self.tello is not None:
                try:
                    if self.tello.is_flying:
                        print("Atterrissage du drone...")
                        self.tello.send_rc_control(0, 0, 0, 0)
                        time.sleep(0.5)
                        self.tello.land()
                        time.sleep(0.5)
                except Exception as e:
                    print(f"Erreur lors de l'atterrissage (peut être ignorée): {e}")
        except Exception as e:
            print(f"Erreur lors de la vérification de l'état du drone: {e}")
        
        # Arrêt du flux vidéo et fermeture de la connexion
        try:
            # Arrêter le thread de lecture Windows si présent
            if hasattr(self, 'frame_read') and self.frame_read is not None:
                # Vérifier si c'est notre WindowsFrameRead avec thread
                if hasattr(self.frame_read, 'stop'):
                    try:
                        self.frame_read.stop()
                        print("Thread de lecture Windows arrêté.")
                    except Exception as e:
                        print(f"Erreur lors de l'arrêt du thread (peut être ignorée): {e}")
            
            # Fermer le VideoCapture Windows si présent
            if hasattr(self, '_windows_video_cap') and self._windows_video_cap is not None:
                try:
                    self._windows_video_cap.release()
                    print("Flux vidéo Windows fermé.")
                except Exception as e:
                    print(f"Erreur lors de la fermeture du flux vidéo Windows (peut être ignorée): {e}")
                finally:
                    self._windows_video_cap = None
            
            if hasattr(self, 'tello') and self.tello is not None:
                try:
                    self.tello.streamoff()
                except Exception as e:
                    print(f"Erreur lors de l'arrêt du flux (peut être ignorée): {e}")
                
                try:
                    self.tello.end()
                except Exception as e:
                    print(f"Erreur lors de la fermeture de la connexion (peut être ignorée): {e}")
                
                # Marquer comme nettoyé pour éviter les appels répétés
                self.tello = None
        except Exception as e:
            print(f"Erreur lors du nettoyage du drone: {e}")
        
        # Fermeture des fenêtres OpenCV (seulement en mode CLI)
        if not self.gui_mode:
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
        
        # Restauration de la connexion Wi-Fi précédente
        try:
            if hasattr(self, 'wifi_manager') and self.wifi_manager is not None:
                print("\nRestauration de la connexion Wi-Fi...")
                self.wifi_manager.cleanup()
                self.wifi_manager = None
        except Exception as e:
            print(f"Erreur lors de la restauration Wi-Fi: {e}")
        
        print("Nettoyage termine.")


def main():
    """
    Fonction principale.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Script de face tracking pour drone DJI Tello avec gestion Wi-Fi automatique"
    )
    parser.add_argument(
        '--model',
        type=str,
        default="yolov8n-face.pt",
        help="Chemin vers le modèle YOLO-face (.pt)"
    )
    parser.add_argument(
        '--conf',
        type=float,
        default=0.25,
        help="Seuil de confiance pour la détection (0.0-1.0)"
    )
    parser.add_argument(
        '--no-auto-wifi',
        action='store_true',
        help="Désactive la gestion automatique Wi-Fi"
    )
    parser.add_argument(
        '--tello-ssid',
        type=str,
        default=None,
        help="SSID du réseau Tello (si non spécifié, sera détecté automatiquement)"
    )
    parser.add_argument(
        '--gui',
        action='store_true',
        help="Lance l'interface graphique (PyQt6 requis)"
    )
    parser.add_argument(
        '--cli',
        action='store_true',
        help="Force le mode ligne de commande (désactive la GUI)"
    )
    
    args = parser.parse_args()
    
    # Détection du mode GUI
    use_gui = False
    if args.gui:
        use_gui = True
    elif not args.cli:
        # Par défaut, essayer d'utiliser la GUI si PyQt6 est disponible
        try:
            import PyQt6.QtWidgets
            use_gui = True
        except ImportError:
            use_gui = False
    
    if use_gui:
        # Lancer l'interface graphique
        try:
            from gui.tello_gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"Erreur: Impossible d'importer l'interface graphique: {e}")
            print("Assurez-vous que PyQt6 est installé: pip install PyQt6")
            sys.exit(1)
    else:
        # Mode ligne de commande
        tracker = FaceTracker(
            model_path=args.model,
            conf_threshold=args.conf,
            auto_wifi=not args.no_auto_wifi,
            tello_ssid=args.tello_ssid,
            gui_mode=False
        )
        tracker.run()


if __name__ == "__main__":
    main()

