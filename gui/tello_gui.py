#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface graphique PyQt6 pour le tracking de visage avec le drone Tello.
"""

import sys
import os
import platform
from typing import Optional, Dict, Any
from pathlib import Path

# Configuration de la plateforme Qt avant d'importer PyQt6
# Éviter les conflits avec OpenCV qui peut avoir ses propres plugins Qt

# Trouver le chemin des plugins PyQt6
try:
    import PyQt6
    pyqt6_path = os.path.dirname(PyQt6.__file__)
    plugins_path = os.path.join(pyqt6_path, 'Qt6', 'plugins')
    
    # Si le répertoire des plugins PyQt6 existe, l'utiliser
    if os.path.exists(plugins_path):
        # Ajouter le chemin des plugins PyQt6 en priorité
        if 'QT_PLUGIN_PATH' in os.environ:
            os.environ['QT_PLUGIN_PATH'] = plugins_path + os.pathsep + os.environ['QT_PLUGIN_PATH']
        else:
            os.environ['QT_PLUGIN_PATH'] = plugins_path
except Exception:
    pass

# Ne pas forcer xcb si ce n'est pas nécessaire
# PyQt6 détectera automatiquement la meilleure plateforme

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QFileDialog, QCheckBox, QLineEdit, QSpinBox, QDoubleSpinBox,
    QTabWidget, QProgressBar, QTextEdit, QGroupBox, QMessageBox, QSplitter,
    QStatusBar, QMenuBar, QToolBar, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap, QFont, QIcon, QAction

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tello_face_tracking import FaceTracker
from gui.components.tracking_thread import TrackingThread
from gui.components.init_thread import InitializationThread


class TelloFaceTrackingGUI(QMainWindow):
    """
    Interface graphique principale pour le tracking de visage avec le drone Tello.
    """
    
    def __init__(self, parent=None):
        """
        Initialise l'interface graphique.
        """
        super().__init__(parent)
        self.tracker: Optional[FaceTracker] = None
        self.tracking_thread: Optional[TrackingThread] = None
        self.init_thread: Optional[InitializationThread] = None
        
        # Configuration par défaut
        # Détection automatique de Windows : désactiver auto_wifi
        is_windows = platform.system() == "Windows"
        self.config = {
            'model_path': 'yolov8n-face.pt',
            'conf_threshold': 0.25,
            'auto_wifi': not is_windows,  # Désactivé sous Windows (pas de nmcli)
            'tello_ssid': None,
            'kp_x': 0.15,
            'kp_y': 0.12,
            'kd_x': 0.25,
            'kd_y': 0.2,
            'max_speed_yaw': 30,
            'max_speed_vertical': 30,
            'max_speed_horizontal': 40,
            'max_speed_forward': 50,
            'dead_zone': 40,
            'target_face_size': 150
        }
        
        # État de l'application
        self.is_tracking = False
        self.is_flying = False
        
        # Initialisation de l'interface
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        
        # Timer pour la mise à jour périodique (moins fréquent pour éviter la saturation)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(200)  # Mise à jour toutes les 200ms (5 Hz)
        
    def setup_ui(self):
        """
        Configure l'interface utilisateur principale.
        """
        self.setWindowTitle("Tello Face Tracking - Interface Graphique")
        self.setMinimumSize(1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (horizontal splitter)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panneau gauche : Configuration et contrôle
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Zone centrale : Affichage vidéo
        video_widget = self.create_video_widget()
        splitter.addWidget(video_widget)
        
        # Panneau droit : Statistiques et logs
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Proportions des panneaux (20% gauche, 60% centre, 20% droit)
        splitter.setSizes([240, 720, 240])
        
        # Barre de statut
        self.statusBar().showMessage("Prêt - Configurez les paramètres et démarrez le tracking")
        
    def create_left_panel(self) -> QWidget:
        """
        Crée le panneau gauche avec configuration et contrôle.
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Configuration
        config_tab = self.create_config_tab()
        tabs.addTab(config_tab, "Configuration")
        
        # Onglet Contrôle
        control_tab = self.create_control_tab()
        tabs.addTab(control_tab, "Contrôle")
        
        # Onglet Paramètres avancés
        advanced_tab = self.create_advanced_tab()
        tabs.addTab(advanced_tab, "Avancé")
        
        layout.addWidget(tabs)
        
        # Bouton de démarrage/arrêt
        self.start_button = QPushButton("Démarrer le tracking")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.start_button.clicked.connect(self.toggle_tracking)
        layout.addWidget(self.start_button)
        
        return panel
    
    def create_config_tab(self) -> QWidget:
        """
        Crée l'onglet de configuration.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # Groupe Modèle YOLO
        model_group = QGroupBox("Modèle YOLO")
        model_layout = QVBoxLayout()
        
        model_hbox = QHBoxLayout()
        self.model_path_label = QLabel(self.config['model_path'])
        self.model_path_label.setWordWrap(True)
        model_browse_btn = QPushButton("Parcourir...")
        model_browse_btn.clicked.connect(self.browse_model_file)
        model_hbox.addWidget(self.model_path_label)
        model_hbox.addWidget(model_browse_btn)
        model_layout.addLayout(model_hbox)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Groupe Seuil de confiance
        conf_group = QGroupBox("Seuil de confiance")
        conf_layout = QVBoxLayout()
        
        self.conf_slider = QSlider(Qt.Orientation.Horizontal)
        self.conf_slider.setMinimum(0)
        self.conf_slider.setMaximum(100)
        self.conf_slider.setValue(int(self.config['conf_threshold'] * 100))
        self.conf_slider.valueChanged.connect(self.on_conf_changed)
        
        self.conf_label = QLabel(f"{self.config['conf_threshold']:.2f}")
        self.conf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        conf_layout.addWidget(self.conf_slider)
        conf_layout.addWidget(self.conf_label)
        conf_group.setLayout(conf_layout)
        layout.addWidget(conf_group)
        
        # Groupe Wi-Fi
        wifi_group = QGroupBox("Configuration Wi-Fi")
        wifi_layout = QVBoxLayout()
        
        # Message d'information sous Windows
        if platform.system() == "Windows":
            windows_wifi_info = QLabel("⚠ Windows détecté : Connectez-vous manuellement au WiFi du Tello avant de démarrer.")
            windows_wifi_info.setWordWrap(True)
            windows_wifi_info.setStyleSheet("color: #FF6B35; font-weight: bold; padding: 5px;")
            wifi_layout.addWidget(windows_wifi_info)
        
        self.auto_wifi_checkbox = QCheckBox("Connexion Wi-Fi automatique (Linux uniquement)")
        self.auto_wifi_checkbox.setChecked(self.config['auto_wifi'])
        self.auto_wifi_checkbox.toggled.connect(self.on_auto_wifi_toggled)
        # Désactiver sous Windows
        if platform.system() == "Windows":
            self.auto_wifi_checkbox.setEnabled(False)
            self.auto_wifi_checkbox.setToolTip("La gestion WiFi automatique n'est disponible que sous Linux")
        wifi_layout.addWidget(self.auto_wifi_checkbox)
        
        ssid_hbox = QHBoxLayout()
        ssid_hbox.addWidget(QLabel("SSID Tello:"))
        self.ssid_input = QLineEdit()
        self.ssid_input.setPlaceholderText("Auto-détection si vide")
        self.ssid_input.setEnabled(not self.config['auto_wifi'])
        ssid_hbox.addWidget(self.ssid_input)
        wifi_layout.addLayout(ssid_hbox)
        
        wifi_group.setLayout(wifi_layout)
        layout.addWidget(wifi_group)
        
        layout.addStretch()
        
        return tab
    
    def create_control_tab(self) -> QWidget:
        """
        Crée l'onglet de contrôle.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # Indicateur d'état
        status_group = QGroupBox("État du drone")
        status_layout = QVBoxLayout()
        
        status_hbox = QHBoxLayout()
        self.status_led = QLabel("●")
        self.status_led.setStyleSheet("color: red; font-size: 24px;")
        self.status_label = QLabel("Au sol")
        status_hbox.addWidget(self.status_led)
        status_hbox.addWidget(self.status_label)
        status_hbox.addStretch()
        status_layout.addLayout(status_hbox)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Boutons de contrôle
        control_group = QGroupBox("Contrôle du drone")
        control_layout = QVBoxLayout()
        
        self.takeoff_button = QPushButton("Décoller")
        self.takeoff_button.setEnabled(False)
        self.takeoff_button.clicked.connect(self.on_takeoff_clicked)
        control_layout.addWidget(self.takeoff_button)
        
        self.emergency_button = QPushButton("ARRÊT D'URGENCE")
        self.emergency_button.setEnabled(False)
        self.emergency_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.emergency_button.clicked.connect(self.on_emergency_stop)
        control_layout.addWidget(self.emergency_button)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        layout.addStretch()
        
        return tab
    
    def create_advanced_tab(self) -> QWidget:
        """
        Crée l'onglet des paramètres avancés.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # Paramètres PID
        pid_group = QGroupBox("Paramètres PID")
        pid_layout = QVBoxLayout()
        
        # kp_x
        kp_x_hbox = QHBoxLayout()
        kp_x_hbox.addWidget(QLabel("kp_x:"))
        self.kp_x_spin = QDoubleSpinBox()
        self.kp_x_spin.setDecimals(3)
        self.kp_x_spin.setSingleStep(0.01)
        self.kp_x_spin.setRange(0.0, 1.0)
        self.kp_x_spin.setValue(self.config['kp_x'])
        kp_x_hbox.addWidget(self.kp_x_spin)
        pid_layout.addLayout(kp_x_hbox)
        
        # kp_y
        kp_y_hbox = QHBoxLayout()
        kp_y_hbox.addWidget(QLabel("kp_y:"))
        self.kp_y_spin = QDoubleSpinBox()
        self.kp_y_spin.setDecimals(3)
        self.kp_y_spin.setSingleStep(0.01)
        self.kp_y_spin.setRange(0.0, 1.0)
        self.kp_y_spin.setValue(self.config['kp_y'])
        kp_y_hbox.addWidget(self.kp_y_spin)
        pid_layout.addLayout(kp_y_hbox)
        
        # kd_x
        kd_x_hbox = QHBoxLayout()
        kd_x_hbox.addWidget(QLabel("kd_x:"))
        self.kd_x_spin = QDoubleSpinBox()
        self.kd_x_spin.setDecimals(3)
        self.kd_x_spin.setSingleStep(0.01)
        self.kd_x_spin.setRange(0.0, 1.0)
        self.kd_x_spin.setValue(self.config['kd_x'])
        kd_x_hbox.addWidget(self.kd_x_spin)
        pid_layout.addLayout(kd_x_hbox)
        
        # kd_y
        kd_y_hbox = QHBoxLayout()
        kd_y_hbox.addWidget(QLabel("kd_y:"))
        self.kd_y_spin = QDoubleSpinBox()
        self.kd_y_spin.setDecimals(3)
        self.kd_y_spin.setSingleStep(0.01)
        self.kd_y_spin.setRange(0.0, 1.0)
        self.kd_y_spin.setValue(self.config['kd_y'])
        kd_y_hbox.addWidget(self.kd_y_spin)
        pid_layout.addLayout(kd_y_hbox)
        
        pid_group.setLayout(pid_layout)
        layout.addWidget(pid_group)
        
        # Vitesses maximales
        speed_group = QGroupBox("Vitesses maximales")
        speed_layout = QVBoxLayout()
        
        # max_speed_yaw
        yaw_hbox = QHBoxLayout()
        yaw_hbox.addWidget(QLabel("Rotation (deg/s):"))
        self.max_speed_yaw_spin = QSpinBox()
        self.max_speed_yaw_spin.setRange(0, 100)
        self.max_speed_yaw_spin.setValue(self.config['max_speed_yaw'])
        yaw_hbox.addWidget(self.max_speed_yaw_spin)
        speed_layout.addLayout(yaw_hbox)
        
        # max_speed_vertical
        vert_hbox = QHBoxLayout()
        vert_hbox.addWidget(QLabel("Vertical (cm/s):"))
        self.max_speed_vertical_spin = QSpinBox()
        self.max_speed_vertical_spin.setRange(0, 100)
        self.max_speed_vertical_spin.setValue(self.config['max_speed_vertical'])
        vert_hbox.addWidget(self.max_speed_vertical_spin)
        speed_layout.addLayout(vert_hbox)
        
        # max_speed_horizontal
        hor_hbox = QHBoxLayout()
        hor_hbox.addWidget(QLabel("Latéral (cm/s):"))
        self.max_speed_horizontal_spin = QSpinBox()
        self.max_speed_horizontal_spin.setRange(0, 100)
        self.max_speed_horizontal_spin.setValue(self.config['max_speed_horizontal'])
        hor_hbox.addWidget(self.max_speed_horizontal_spin)
        speed_layout.addLayout(hor_hbox)
        
        # max_speed_forward
        fwd_hbox = QHBoxLayout()
        fwd_hbox.addWidget(QLabel("Avant/Arrière (cm/s):"))
        self.max_speed_forward_spin = QSpinBox()
        self.max_speed_forward_spin.setRange(0, 100)
        self.max_speed_forward_spin.setValue(self.config['max_speed_forward'])
        fwd_hbox.addWidget(self.max_speed_forward_spin)
        speed_layout.addLayout(fwd_hbox)
        
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        # Autres paramètres
        other_group = QGroupBox("Autres paramètres")
        other_layout = QVBoxLayout()
        
        # dead_zone
        dz_hbox = QHBoxLayout()
        dz_hbox.addWidget(QLabel("Zone morte (px):"))
        self.dead_zone_spin = QSpinBox()
        self.dead_zone_spin.setRange(0, 200)
        self.dead_zone_spin.setValue(self.config['dead_zone'])
        dz_hbox.addWidget(self.dead_zone_spin)
        other_layout.addLayout(dz_hbox)
        
        # target_face_size
        tfs_hbox = QHBoxLayout()
        tfs_hbox.addWidget(QLabel("Taille cible visage (px):"))
        self.target_face_size_spin = QSpinBox()
        self.target_face_size_spin.setRange(50, 500)
        self.target_face_size_spin.setValue(self.config['target_face_size'])
        tfs_hbox.addWidget(self.target_face_size_spin)
        other_layout.addLayout(tfs_hbox)
        
        other_group.setLayout(other_layout)
        layout.addWidget(other_group)
        
        # Bouton réinitialiser
        reset_btn = QPushButton("Réinitialiser aux valeurs par défaut")
        reset_btn.clicked.connect(self.reset_advanced_params)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        
        return tab
    
    def create_video_widget(self) -> QWidget:
        """
        Crée le widget d'affichage vidéo.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: 2px solid #333333;
            }
        """)
        self.video_label.setText("Aucune vidéo\nDémarrez le tracking pour voir le flux")
        self.video_label.setMinimumSize(640, 480)
        
        layout.addWidget(self.video_label)
        
        return widget
    
    def create_right_panel(self) -> QWidget:
        """
        Crée le panneau droit avec statistiques et logs.
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        tabs = QTabWidget()
        
        # Onglet Statistiques
        stats_tab = self.create_stats_tab()
        tabs.addTab(stats_tab, "Statistiques")
        
        # Onglet Logs
        logs_tab = self.create_logs_tab()
        tabs.addTab(logs_tab, "Logs")
        
        layout.addWidget(tabs)
        
        return panel
    
    def create_stats_tab(self) -> QWidget:
        """
        Crée l'onglet de statistiques.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # Batterie
        battery_group = QGroupBox("Batterie")
        battery_layout = QVBoxLayout()
        
        self.battery_progress = QProgressBar()
        self.battery_progress.setRange(0, 100)
        self.battery_progress.setValue(0)
        battery_layout.addWidget(self.battery_progress)
        
        self.battery_label = QLabel("0%")
        self.battery_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        battery_layout.addWidget(self.battery_label)
        
        battery_group.setLayout(battery_layout)
        layout.addWidget(battery_group)
        
        # FPS
        fps_group = QGroupBox("Performance")
        fps_layout = QVBoxLayout()
        
        self.fps_label = QLabel("FPS: 0.0")
        self.fps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fps_layout.addWidget(self.fps_label)
        
        fps_group.setLayout(fps_layout)
        layout.addWidget(fps_group)
        
        # Détection
        detection_group = QGroupBox("Détection")
        detection_layout = QVBoxLayout()
        
        self.detection_status_label = QLabel("Aucun visage détecté")
        self.detection_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detection_layout.addWidget(self.detection_status_label)
        
        self.face_size_label = QLabel("Taille: 0 px")
        self.face_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detection_layout.addWidget(self.face_size_label)
        
        self.confidence_label = QLabel("Confiance: 0.00")
        self.confidence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detection_layout.addWidget(self.confidence_label)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        # Vitesses
        velocity_group = QGroupBox("Vitesses de contrôle")
        velocity_layout = QVBoxLayout()
        
        self.left_right_label = QLabel("Gauche/Droite: 0 cm/s")
        velocity_layout.addWidget(self.left_right_label)
        
        self.forward_backward_label = QLabel("Avant/Arrière: 0 cm/s")
        velocity_layout.addWidget(self.forward_backward_label)
        
        self.up_down_label = QLabel("Monter/Descendre: 0 cm/s")
        velocity_layout.addWidget(self.up_down_label)
        
        self.yaw_label = QLabel("Rotation: 0 deg/s")
        velocity_layout.addWidget(self.yaw_label)
        
        velocity_group.setLayout(velocity_layout)
        layout.addWidget(velocity_group)
        
        layout.addStretch()
        
        return tab
    
    def create_logs_tab(self) -> QWidget:
        """
        Crée l'onglet de logs.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.log_text)
        
        # Boutons de contrôle des logs
        log_controls = QHBoxLayout()
        
        clear_btn = QPushButton("Effacer")
        clear_btn.clicked.connect(self.log_text.clear)
        log_controls.addWidget(clear_btn)
        
        log_controls.addStretch()
        layout.addLayout(log_controls)
        
        return tab
    
    def setup_menu(self):
        """
        Configure la barre de menu.
        """
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")
        
        exit_action = QAction("Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Aide
        help_menu = menubar.addMenu("Aide")
        
        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """
        Configure la barre d'outils.
        """
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Action pour démarrer/arrêter
        self.toolbar_start_action = QAction("▶ Démarrer", self)
        self.toolbar_start_action.triggered.connect(self.toggle_tracking)
        toolbar.addAction(self.toolbar_start_action)
        
        toolbar.addSeparator()
        
        # Action pour décoller
        self.toolbar_takeoff_action = QAction("🚁 Décoller", self)
        self.toolbar_takeoff_action.setEnabled(False)
        self.toolbar_takeoff_action.triggered.connect(self.on_takeoff_clicked)
        toolbar.addAction(self.toolbar_takeoff_action)
    
    # Slots et méthodes de gestion
    
    def browse_model_file(self):
        """
        Ouvre un dialogue pour sélectionner le fichier modèle.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le modèle YOLO",
            "",
            "Fichiers PyTorch (*.pt);;Tous les fichiers (*)"
        )
        if file_path:
            self.config['model_path'] = file_path
            self.model_path_label.setText(file_path)
            self.add_log(f"Modèle sélectionné: {file_path}", "info")
    
    def on_conf_changed(self, value: int):
        """
        Gère le changement du seuil de confiance.
        """
        self.config['conf_threshold'] = value / 100.0
        self.conf_label.setText(f"{self.config['conf_threshold']:.2f}")
        if self.tracker:
            self.tracker.conf_threshold = self.config['conf_threshold']
    
    def on_auto_wifi_toggled(self, checked: bool):
        """
        Gère le changement de l'option Wi-Fi automatique.
        """
        self.config['auto_wifi'] = checked
        self.ssid_input.setEnabled(not checked)
    
    def reset_advanced_params(self):
        """
        Réinitialise les paramètres avancés aux valeurs par défaut.
        """
        self.kp_x_spin.setValue(0.15)
        self.kp_y_spin.setValue(0.12)
        self.kd_x_spin.setValue(0.25)
        self.kd_y_spin.setValue(0.2)
        self.max_speed_yaw_spin.setValue(30)
        self.max_speed_vertical_spin.setValue(30)
        self.max_speed_horizontal_spin.setValue(40)
        self.max_speed_forward_spin.setValue(50)
        self.dead_zone_spin.setValue(40)
        self.target_face_size_spin.setValue(150)
        self.add_log("Paramètres avancés réinitialisés", "info")
    
    def toggle_tracking(self):
        """
        Démarre ou arrête le tracking.
        """
        if not self.is_tracking:
            self.start_tracking()
        else:
            self.stop_tracking()
    
    def start_tracking(self):
        """
        Démarre le tracking.
        """
        if self.is_tracking:
            # Si déjà en cours, arrêter d'abord
            self.stop_tracking()
            return
        
        try:
            # Récupération de la configuration
            self.config['tello_ssid'] = self.ssid_input.text() if self.ssid_input.text() else None
            
            # Mettre à jour la configuration avec les valeurs des spinboxes
            self.config['kp_x'] = self.kp_x_spin.value()
            self.config['kp_y'] = self.kp_y_spin.value()
            self.config['kd_x'] = self.kd_x_spin.value()
            self.config['kd_y'] = self.kd_y_spin.value()
            self.config['max_speed_yaw'] = self.max_speed_yaw_spin.value()
            self.config['max_speed_vertical'] = self.max_speed_vertical_spin.value()
            self.config['max_speed_horizontal'] = self.max_speed_horizontal_spin.value()
            self.config['max_speed_forward'] = self.max_speed_forward_spin.value()
            self.config['dead_zone'] = self.dead_zone_spin.value()
            self.config['target_face_size'] = self.target_face_size_spin.value()
            
            # Désactiver le bouton pendant l'initialisation
            self.start_button.setEnabled(False)
            self.start_button.setText("Initialisation en cours...")
            self.toolbar_start_action.setEnabled(False)
            
            # Afficher un message dans la barre de statut
            self.statusBar().showMessage("Connexion au drone en cours...")
            self.add_log("Démarrage de l'initialisation...", "info")
            
            # Créer et démarrer le thread d'initialisation
            self.init_thread = InitializationThread(self.config)
            self.init_thread.progress_update.connect(self.add_log)
            self.init_thread.initialization_complete.connect(self.on_tracker_initialized)
            self.init_thread.initialization_failed.connect(self.on_tracker_init_failed)
            self.init_thread.finished.connect(self.on_init_thread_finished)
            self.init_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de démarrer l'initialisation:\n{str(e)}")
            self.add_log(f"Erreur: {str(e)}", "error")
            self.start_button.setEnabled(True)
            self.start_button.setText("Démarrer le tracking")
            self.toolbar_start_action.setEnabled(True)
            self.statusBar().showMessage("Prêt")
    
    def on_tracker_initialized(self, tracker):
        """
        Callback appelé quand le tracker est initialisé avec succès.
        """
        try:
            self.tracker = tracker
            self.add_log("Tracker initialisé, démarrage du tracking...", "info")
            
            # Création et connexion du thread de tracking
            self.tracking_thread = TrackingThread(self.tracker)
            self.tracking_thread.frame_ready.connect(self.on_frame_received)
            self.tracking_thread.stats_updated.connect(self.on_stats_updated)
            self.tracking_thread.status_changed.connect(self.on_status_changed)
            self.tracking_thread.error_occurred.connect(self.on_error)
            self.tracking_thread.log_message.connect(self.add_log)
            self.tracking_thread.tracking_finished.connect(self.on_tracking_finished)
            
            # Démarrage du thread de tracking
            self.tracking_thread.start()
            self.is_tracking = True
            
            # Mise à jour de l'interface
            self.start_button.setEnabled(True)
            self.start_button.setText("Arrêter le tracking")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            self.toolbar_start_action.setEnabled(True)
            self.toolbar_start_action.setText("⏹ Arrêter")
            self.takeoff_button.setEnabled(True)
            self.toolbar_takeoff_action.setEnabled(True)
            
            self.statusBar().showMessage("Tracking en cours...")
            self.add_log("Tracking démarré", "info")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de démarrer le tracking:\n{str(e)}")
            self.add_log(f"Erreur: {str(e)}", "error")
            self.is_tracking = False
            self.start_button.setEnabled(True)
            self.start_button.setText("Démarrer le tracking")
            self.toolbar_start_action.setEnabled(True)
            self.statusBar().showMessage("Prêt")
            if self.tracker:
                try:
                    self.tracker.cleanup()
                except Exception:
                    pass
                self.tracker = None
    
    def on_tracker_init_failed(self, error_msg: str):
        """
        Callback appelé quand l'initialisation échoue.
        """
        QMessageBox.critical(self, "Erreur d'initialisation", 
                        f"Impossible d'initialiser le tracker:\n{error_msg}")
        self.add_log(f"Erreur d'initialisation: {error_msg}", "error")
        self.start_button.setEnabled(True)
        self.start_button.setText("Démarrer le tracking")
        self.toolbar_start_action.setEnabled(True)
        self.statusBar().showMessage("Prêt")
    
    def on_init_thread_finished(self):
        """
        Callback appelé quand le thread d'initialisation se termine.
        """
        if self.init_thread:
            self.init_thread.deleteLater()
            self.init_thread = None
    
    def stop_tracking(self):
        """
        Arrête le tracking.
        """
        # Annuler l'initialisation si elle est en cours
        if self.init_thread and self.init_thread.isRunning():
            self.add_log("Annulation de l'initialisation...", "info")
            self.init_thread.cancel()
            self.init_thread.wait(3000)  # Attendre jusqu'à 3 secondes
            if self.init_thread.isRunning():
                self.init_thread.terminate()
                self.init_thread.wait(1000)
            self.init_thread = None
            self.start_button.setEnabled(True)
            self.start_button.setText("Démarrer le tracking")
            self.toolbar_start_action.setEnabled(True)
            self.statusBar().showMessage("Prêt")
            return
        
        if self.tracking_thread:
            # Demander l'arrêt du thread
            self.tracking_thread.stop()
            
            # Attendre que le thread se termine (avec timeout)
            if not self.tracking_thread.wait(5000):  # Attendre jusqu'à 5 secondes
                self.add_log("Le thread ne s'est pas terminé dans les temps, forçage de l'arrêt...", "warning")
                self.tracking_thread.terminate()  # Forcer l'arrêt si nécessaire
                self.tracking_thread.wait(1000)  # Attendre encore un peu
            
            self.tracking_thread = None
        
        # Le cleanup du tracker est déjà fait dans le thread
        # Mais on peut le faire ici aussi pour être sûr (cleanup est idempotent)
        if self.tracker:
            try:
                self.tracker.cleanup()
            except Exception as e:
                self.add_log(f"Erreur lors du nettoyage: {e}", "warning")
            self.tracker = None
        
        self.is_tracking = False
        self.is_flying = False
        
        # Mise à jour de l'interface
        self.start_button.setText("Démarrer le tracking")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.toolbar_start_action.setText("▶ Démarrer")
        self.takeoff_button.setEnabled(False)
        self.toolbar_takeoff_action.setEnabled(False)
        self.emergency_button.setEnabled(False)
        
        self.status_led.setStyleSheet("color: red; font-size: 24px;")
        self.status_label.setText("Au sol")
        
        self.video_label.setText("Aucune vidéo\nDémarrez le tracking pour voir le flux")
        
        self.statusBar().showMessage("Tracking arrêté")
        self.add_log("Tracking arrêté", "info")
    
    @pyqtSlot(object)
    def on_frame_received(self, qimage: QImage):
        """
        Reçoit et affiche une nouvelle frame.
        Cette méthode doit être rapide pour ne pas bloquer l'interface.
        """
        if qimage and not qimage.isNull():
            try:
                pixmap = QPixmap.fromImage(qimage)
                if not pixmap.isNull():
                    # Redimensionner pour s'adapter au widget tout en gardant les proportions
                    # Utiliser FastTransformation pour être plus rapide
                    scaled_pixmap = pixmap.scaled(
                        self.video_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.FastTransformation  # Plus rapide que SmoothTransformation
                    )
                    self.video_label.setPixmap(scaled_pixmap)
            except Exception as e:
                # Ignorer les erreurs d'affichage pour ne pas bloquer l'interface
                pass
    
    @pyqtSlot(dict)
    def on_stats_updated(self, stats: Dict[str, Any]):
        """
        Met à jour les statistiques affichées.
        """
        # Batterie
        battery = stats.get('battery', 0)
        self.battery_progress.setValue(battery)
        self.battery_label.setText(f"{battery}%")
        
        # FPS
        fps = stats.get('fps', 0.0)
        self.fps_label.setText(f"FPS: {fps:.1f}")
        
        # Détection
        face_detected = stats.get('face_detected', False)
        if face_detected:
            self.detection_status_label.setText("✓ Visage détecté")
            self.detection_status_label.setStyleSheet("color: green;")
        else:
            self.detection_status_label.setText("✗ Aucun visage")
            self.detection_status_label.setStyleSheet("color: red;")
        
        face_size = stats.get('face_size', 0)
        self.face_size_label.setText(f"Taille: {face_size:.0f} px")
        
        confidence = stats.get('confidence', 0.0)
        self.confidence_label.setText(f"Confiance: {confidence:.2f}")
        
        # Vitesses
        self.left_right_label.setText(f"Gauche/Droite: {stats.get('left_right', 0)} cm/s")
        self.forward_backward_label.setText(f"Avant/Arrière: {stats.get('forward_backward', 0)} cm/s")
        self.up_down_label.setText(f"Monter/Descendre: {stats.get('up_down', 0)} cm/s")
        self.yaw_label.setText(f"Rotation: {stats.get('yaw', 0)} deg/s")
        
        # État de vol
        self.is_flying = stats.get('is_flying', False)
        if self.is_flying:
            self.emergency_button.setEnabled(True)
    
    @pyqtSlot(str)
    def on_status_changed(self, status: str):
        """
        Gère le changement de statut du drone.
        """
        if status == "flying":
            self.status_led.setStyleSheet("color: green; font-size: 24px;")
            self.status_label.setText("En vol")
            self.takeoff_button.setText("Atterrir")
            self.toolbar_takeoff_action.setText("🛬 Atterrir")
        else:
            self.status_led.setStyleSheet("color: red; font-size: 24px;")
            self.status_label.setText("Au sol")
            self.takeoff_button.setText("Décoller")
            self.toolbar_takeoff_action.setText("🚁 Décoller")
            self.emergency_button.setEnabled(False)
    
    @pyqtSlot(str)
    def on_error(self, error_msg: str):
        """
        Gère les erreurs.
        """
        QMessageBox.warning(self, "Erreur", error_msg)
        self.add_log(f"ERREUR: {error_msg}", "error")
    
    def on_takeoff_clicked(self):
        """
        Gère le clic sur le bouton décollage/atterrissage.
        """
        if self.tracking_thread:
            if self.is_flying:
                self.tracking_thread.request_land()
            else:
                self.tracking_thread.request_takeoff()
    
    def on_emergency_stop(self):
        """
        Gère l'arrêt d'urgence.
        """
        reply = QMessageBox.question(
            self,
            "Arrêt d'urgence",
            "Êtes-vous sûr de vouloir effectuer un arrêt d'urgence?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.tracking_thread:
                self.tracking_thread.emergency_stop()
    
    def on_tracking_finished(self):
        """
        Appelé quand le tracking est terminé.
        """
        self.stop_tracking()
    
    def add_log(self, message: str, level: str = "info"):
        """
        Ajoute un message au log.
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "error":
            prefix = "[ERREUR]"
            color = "red"
        elif level == "warning":
            prefix = "[ATTENTION]"
            color = "orange"
        else:
            prefix = "[INFO]"
            color = "black"
        
        log_entry = f'<span style="color: {color};">[{timestamp}] {prefix} {message}</span>'
        self.log_text.append(log_entry)
        
        # Scroll automatique vers le bas
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_ui(self):
        """
        Met à jour l'interface utilisateur périodiquement.
        """
        # Cette méthode peut être utilisée pour des mises à jour périodiques
        pass
    
    def show_about(self):
        """
        Affiche la boîte de dialogue À propos.
        """
        QMessageBox.about(
            self,
            "À propos",
            "Tello Face Tracking - Interface Graphique\n\n"
            "Application de tracking de visage pour drone DJI Tello\n"
            "utilisant YOLO-face pour la détection.\n\n"
            "Version: 1.0"
        )
    
    def closeEvent(self, event):
        """
        Gère la fermeture de la fenêtre.
        """
        if self.is_tracking:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Le tracking est en cours. Voulez-vous vraiment quitter?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            # Arrêter le tracking proprement
            self.add_log("Fermeture de l'application...", "info")
            self.stop_tracking()
            
            # Attendre un peu pour que tout se termine proprement
            import time
            time.sleep(1)
        
        # Arrêter le timer de mise à jour
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        
        event.accept()


def main():
    """
    Point d'entrée principal pour l'interface graphique.
    """
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Tello Face Tracking")
        
        window = TelloFaceTrackingGUI()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"Erreur lors du lancement de l'interface graphique: {e}")
        print("\nSolutions possibles:")
        print("1. Installer les dépendances système:")
        print("   sudo apt-get install libxcb-cursor0 libxcb-xinerama0 libxcb-xkb1")
        print("2. Ou installer via:")
        print("   sudo apt-get install libxcb-cursor-dev")
        print("3. Vérifier que PyQt6 est correctement installé:")
        print("   pip install --upgrade PyQt6")
        sys.exit(1)


if __name__ == "__main__":
    main()

