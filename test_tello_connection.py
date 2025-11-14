#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier la connexion au drone Tello
et la réception du flux vidéo.
"""

import sys

try:
    from djitellopy import Tello
except ImportError:
    print("Erreur: djitellopy n'est pas installe.")
    print("Installez-le avec: pip install djitellopy")
    sys.exit(1)

try:
    import cv2
except ImportError:
    print("Erreur: opencv-python n'est pas installe.")
    print("Installez-le avec: pip install opencv-python")
    sys.exit(1)


def test_connection():
    """
    Teste la connexion au Tello et affiche le flux vidéo.
    """
    print("Connexion au drone Tello...")
    tello = Tello()
    
    try:
        tello.connect()
        print("✓ Connexion reussie!")
        
        # Informations du drone
        battery = tello.get_battery()
        print(f"✓ Batterie: {battery}%")
        
        if battery < 20:
            print("⚠ ATTENTION: Batterie faible!")
        
        # Test du flux vidéo
        print("\nDemarrage du flux video...")
        print("Appuyez sur 'q' pour quitter")
        
        tello.streamon()
        frame_read = tello.get_frame_read()
        
        frame_count = 0
        
        while True:
            frame = frame_read.frame
            if frame is not None:
                frame_count += 1
                
                # Affichage d'informations sur la frame
                h, w = frame.shape[:2]
                cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Resolution: {w}x{h}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Batterie: {battery}%", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow("Test Tello", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("⚠ Aucune frame recue")
                break
        
        print("\nArret du flux video...")
        tello.streamoff()
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        print("\nVerifications:")
        print("1. Le drone est-il allume?")
        print("2. Etes-vous connecte au WiFi du Tello?")
        print("3. Le drone est-il a portee?")
    finally:
        try:
            tello.end()
        except:
            pass
        cv2.destroyAllWindows()
        print("Test termine.")


if __name__ == "__main__":
    test_connection()

