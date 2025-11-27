# 🚁 Tello Face Tracking - Guide Windows

Guide d'installation et d'utilisation pour Windows destiné aux utilisateurs débutants.

---

## 📋 Table des matières

- [Qu'est-ce que c'est ?](#quest-ce-que-cest-)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration WiFi](#configuration-wifi)
- [Utilisation](#utilisation)
- [Dépannage](#dépannage)
- [Conseils de sécurité](#conseils-de-sécurité)

---

## Qu'est-ce que c'est ?

**Tello Face Tracking** est une application qui permet à votre drone DJI Tello de **suivre automatiquement un visage**. Le drone détecte votre visage grâce à sa caméra et ajuste sa position pour vous garder au centre de l'image.

### Fonctionnalités

- ✅ Détection automatique de visage avec intelligence artificielle (YOLO)
- ✅ Suivi en temps réel avec contrôle automatique du drone
- ✅ Interface graphique intuitive
- ✅ Contrôles manuels disponibles
- ✅ Affichage du flux vidéo en direct
- ✅ Surveillance de la batterie

---

## Prérequis

### Matériel requis

1. **Un drone DJI Tello** (Tello, Tello EDU, ou Tello Talent)
2. **Un ordinateur Windows** (Windows 7 ou supérieur)
3. **Une batterie chargée** pour le drone (recommandé : >50%)

### Logiciels requis

- **Windows 7, 8, 10 ou 11**
- **Connexion WiFi** (pour se connecter au drone)
- Aucun logiciel supplémentaire nécessaire ! L'application est autonome.

---

## Installation

### Étape 1 : Télécharger l'application

1. Téléchargez le fichier **TelloFaceTracking.zip** depuis la page de téléchargement
2. Téléchargez également le fichier **yolov8n-face.pt** (modèle de détection, ~6 MB)

### Étape 2 : Extraire les fichiers

1. Faites un **clic droit** sur **TelloFaceTracking.zip**
2. Sélectionnez **"Extraire tout..."**
3. Choisissez un emplacement (par exemple : `C:\Users\VotreNom\TelloFaceTracking\`)
4. Cliquez sur **"Extraire"**

### Étape 3 : Placer le modèle de détection

**⚠️ IMPORTANT** : Cette étape est **obligatoire** !

1. Copiez le fichier **yolov8n-face.pt** que vous avez téléchargé
2. Collez-le dans le **même dossier** que **TelloFaceTracking.exe**

Votre dossier doit ressembler à ceci :

```
📁 TelloFaceTracking/
  ├── 📄 TelloFaceTracking.exe    ← L'application
  ├── 📄 yolov8n-face.pt          ← Le modèle (REQUIS !)
  ├── 📄 LISEZMOI.txt
  └── 📄 BUILD_INFO.txt
```

### Étape 4 : Autorisation du pare-feu

Au premier lancement, Windows peut afficher une alerte de sécurité :

1. **Cochez** "Réseaux privés" et "Réseaux publics"
2. Cliquez sur **"Autoriser l'accès"**

> **Pourquoi ?** L'application a besoin d'accéder au réseau pour communiquer avec le drone via WiFi.

---

## Configuration WiFi

### Se connecter au drone Tello

**Avant de lancer l'application**, vous devez vous connecter manuellement au WiFi du drone.

#### Étape 1 : Allumer le drone

1. Allumez votre drone Tello
2. Attendez que la **LED clignote** (jaune/orange)
3. Cela signifie que le drone émet son réseau WiFi

#### Étape 2 : Se connecter au WiFi du drone

1. Ouvrez les **paramètres WiFi** de Windows :
   - Cliquez sur l'icône WiFi dans la barre des tâches
   - Ou : Paramètres → Réseau et Internet → WiFi

2. Recherchez un réseau nommé **"TELLO-XXXXXX"**
   - Les X représentent des chiffres/lettres uniques à votre drone

3. Cliquez sur le réseau Tello et sélectionnez **"Se connecter"**
   - **Pas de mot de passe nécessaire** : connexion directe
   - Si demandé, choisissez **"Non"** pour "Autoriser d'autres appareils à découvrir ce PC"

4. Attendez que Windows indique **"Connecté"**

> **📌 Note** : Une fois connecté au Tello, vous n'aurez **plus accès à Internet**. C'est normal ! Le drone crée son propre réseau local.

#### Vérifier la connexion

Votre icône WiFi Windows doit afficher :
- ✅ **"Connecté, aucun Internet"** ou **"TELLO-XXXXXX"**

C'est normal ! Le drone n'a pas d'accès Internet.

---

## Utilisation

### Lancement de l'application

1. **Double-cliquez** sur **TelloFaceTracking.exe**
2. L'interface graphique s'ouvre

### Interface utilisateur

L'interface est divisée en 3 parties :

```
┌─────────────┬────────────────────┬──────────────┐
│ Configuration│   Flux vidéo       │ Statistiques │
│   et         │                    │   et logs    │
│  contrôles   │                    │              │
└─────────────┴────────────────────┴──────────────┘
```

#### Panneau gauche : Configuration et contrôle

- **Onglet Configuration** :
  - Sélection du modèle YOLO
  - Réglage du seuil de confiance
  - Information WiFi

- **Onglet Contrôle** :
  - État du drone (au sol / en vol)
  - Bouton "Décoller" / "Atterrir"
  - Bouton "ARRÊT D'URGENCE" (en rouge)

- **Onglet Avancé** :
  - Paramètres PID (pour utilisateurs avancés)
  - Vitesses maximales
  - Zone morte et taille cible

#### Panneau central : Flux vidéo

- Affichage en temps réel de la caméra du drone
- Cadre vert : centre de l'image (cible)
- Cadre rouge : visage détecté
- Ligne bleue : vecteur de correction

#### Panneau droit : Statistiques et logs

- **Onglet Statistiques** :
  - Niveau de batterie (%)
  - FPS (images par seconde)
  - État de la détection
  - Vitesses de contrôle actuelles

- **Onglet Logs** :
  - Messages d'information en temps réel
  - Historique des actions

### Utilisation étape par étape

#### 1. Démarrer le tracking

1. Vérifiez que vous êtes **connecté au WiFi du Tello**
2. Cliquez sur le bouton vert **"Démarrer le tracking"**
3. Attendez quelques secondes
4. Le **flux vidéo** apparaît au centre
5. Le bouton devient rouge **"Arrêter le tracking"**

Si tout va bien, vous verrez :
- ✅ Flux vidéo en direct
- ✅ Batterie affichée (%)
- ✅ "Connecté" dans les logs

#### 2. Faire décoller le drone

⚠️ **IMPORTANT** : Avant de faire décoller le drone :
- Placez le drone sur une **surface plane et dégagée**
- Assurez-vous d'avoir au moins **2-3 mètres d'espace libre** autour
- Éloignez-vous d'au moins **1 mètre** du drone

1. Allez dans l'onglet **"Contrôle"** (panneau gauche)
2. Cliquez sur **"Décoller"**
3. Le drone décolle automatiquement à ~1 mètre de hauteur
4. Le bouton devient **"Atterrir"**
5. Le statut passe de "Au sol" à **"En vol"** (LED verte)

#### 3. Tracking automatique

Une fois en vol :
- Placez-vous **face à la caméra du drone**
- À **2-4 mètres de distance**
- Le drone détecte automatiquement votre visage
- Il ajuste sa position pour vous **centrer dans l'image**

**Le drone peut :**
- Se déplacer **gauche/droite** pour vous centrer horizontalement
- **Monter/descendre** pour vous centrer verticalement
- **Avancer/reculer** pour maintenir une distance constante
- **Tourner légèrement** pour les ajustements fins

**Vous verrez :**
- Un **cadre rouge** autour de votre visage
- Une **ligne bleue** entre le centre et votre visage
- Les **vitesses de contrôle** dans le panneau droit

#### 4. Faire atterrir le drone

Pour arrêter le tracking et faire atterrir le drone :

1. Cliquez sur **"Atterrir"**
2. Le drone atterrit automatiquement
3. Attendez que le drone soit **complètement au sol**
4. Le statut repasse à **"Au sol"** (LED rouge)

#### 5. Arrêter l'application

1. Cliquez sur **"Arrêter le tracking"**
2. La connexion au drone est fermée
3. Vous pouvez fermer l'application

> **💡 Astuce** : Vous pouvez maintenant vous **reconnecter à votre WiFi habituel** !

### Arrêt d'urgence

Si quelque chose ne va pas :

1. Cliquez sur le bouton rouge **"ARRÊT D'URGENCE"**
2. Le drone s'arrête immédiatement et atterrit
3. Utilisez ce bouton en cas de danger ou de comportement anormal

---

## Dépannage

### Problèmes courants

#### ❌ "Le modèle n'est pas trouvé"

**Cause** : Le fichier `yolov8n-face.pt` n'est pas au bon endroit.

**Solution** :
1. Vérifiez que `yolov8n-face.pt` est dans le **même dossier** que `TelloFaceTracking.exe`
2. Vérifiez l'orthographe exacte du fichier
3. Redémarrez l'application

#### ❌ "Impossible de se connecter au drone"

**Cause 1** : Vous n'êtes pas connecté au WiFi du Tello

**Solution** :
1. Ouvrez les paramètres WiFi de Windows
2. Connectez-vous au réseau **TELLO-XXXXXX**
3. Attendez que la connexion soit établie
4. Redémarrez l'application

**Cause 2** : Le drone n'est pas allumé ou la batterie est faible

**Solution** :
1. Vérifiez que le drone est allumé (LED clignotante)
2. Rechargez la batterie si nécessaire (>20%)
3. Redémarrez le drone

**Cause 3** : Le pare-feu Windows bloque la connexion

**Solution** :
1. Allez dans : Panneau de configuration → Système et sécurité → Pare-feu Windows Defender
2. Cliquez sur "Autoriser une application via le Pare-feu Windows"
3. Cherchez "TelloFaceTracking" et **cochez les cases**
4. Si absent, cliquez sur "Modifier les paramètres" puis "Autoriser une autre application"
5. Ajoutez `TelloFaceTracking.exe`

#### ❌ "Pas de flux vidéo" (écran noir)

**Solution** :
1. Attendez **5-10 secondes** après avoir cliqué sur "Démarrer le tracking"
2. Vérifiez que le drone est bien allumé
3. Arrêtez et redémarrez le tracking
4. En dernier recours : redémarrez le drone et l'application

#### ❌ "Le drone ne réagit pas" ou "Détection instable"

**Cause** : Mauvaises conditions d'éclairage ou environnement

**Solution** :
1. **Éclairage** : Utilisez le drone dans un environnement bien éclairé
2. **Fond** : Évitez les fonds trop chargés ou complexes
3. **Distance** : Placez-vous à 2-4 mètres du drone
4. **Ajustez le seuil** : Dans Configuration, augmentez légèrement le seuil de confiance

#### ❌ Le drone oscille ou bouge de manière saccadée

**Solution** : Ajustez les paramètres avancés (onglet "Avancé")
1. **Réduisez** les gains PID (kp_x, kp_y) pour des mouvements plus doux
2. **Augmentez** la zone morte (dead_zone) pour éviter les micro-corrections
3. Cliquez sur "Réinitialiser aux valeurs par défaut" en cas de doute

#### ❌ L'application se ferme immédiatement

**Solution** :
1. Vérifiez que `yolov8n-face.pt` est présent
2. Vérifiez que vous êtes connecté au WiFi du Tello
3. Essayez de lancer l'application en tant qu'**administrateur** :
   - Clic droit sur `TelloFaceTracking.exe`
   - Sélectionnez "Exécuter en tant qu'administrateur"

### Problèmes de performance

#### Le drone répond lentement

**Causes possibles** :
- Ordinateur trop lent (CPU insuffisant)
- Trop d'applications ouvertes en arrière-plan
- Interférences WiFi

**Solutions** :
1. Fermez les **applications inutiles**
2. Rapprochez-vous du drone (< 5 mètres)
3. Évitez les zones avec beaucoup d'appareils WiFi

#### FPS faible (< 10 FPS)

**Solutions** :
1. Fermez les applications gourmandes (navigateur, jeux, etc.)
2. Dans l'onglet Configuration, augmentez légèrement le seuil de confiance (0.3-0.35)
3. Redémarrez l'ordinateur

---

## Conseils de sécurité

### ⚠️ Avant chaque vol

- [ ] Batterie du drone chargée (>20%, idéalement >50%)
- [ ] Espace dégagé de **3-5 mètres minimum** autour du drone
- [ ] Surface plane pour le décollage/atterrissage
- [ ] Pas de personnes ou d'animaux à proximité
- [ ] Fenêtres fermées (éviter que le drone sorte)

### ⚠️ Pendant le vol

- [ ] **Surveillez constamment le drone**
- [ ] Gardez la main près du bouton "ARRÊT D'URGENCE"
- [ ] Surveillez le niveau de batterie (ne pas descendre sous 20%)
- [ ] Ne volez pas au-dessus de personnes ou d'objets fragiles
- [ ] Gardez le drone à vue

### ⚠️ Limitations importantes

- **Portée WiFi** : Maximum 10 mètres (peut varier)
- **Durée de vol** : ~10-13 minutes par batterie
- **Conditions météo** : Intérieur uniquement ou extérieur par temps calme
- **Altitude** : Le Tello vole jusqu'à ~10 mètres maximum

### 🚨 En cas de problème

1. **Bouton "ARRÊT D'URGENCE"** dans l'application
2. **Attraper le drone** (attention aux hélices !)
3. **Éteindre le drone** (bouton power)

---

## Questions fréquentes (FAQ)

### Puis-je utiliser l'application sans Internet ?

**Oui !** L'application fonctionne entièrement en local. Vous avez juste besoin de vous connecter au WiFi du drone.

### Le modèle yolov8n-face.pt est-il gratuit ?

**Oui !** C'est un modèle open-source que vous pouvez télécharger et utiliser gratuitement.

### Puis-je suivre plusieurs visages en même temps ?

**Non**, actuellement l'application suit le **visage le plus grand** (le plus proche du drone).

### Le drone enregistre-t-il des vidéos ?

**Non**, l'application affiche le flux en direct mais ne l'enregistre pas. Si vous souhaitez enregistrer, vous devrez ajouter cette fonctionnalité vous-même.

### Puis-je utiliser un autre drone ?

**Non**, cette application est conçue spécifiquement pour le **DJI Tello**. D'autres drones ne sont pas compatibles.

### L'application fonctionne-t-elle sur Mac ou Linux ?

Cette version est pour **Windows uniquement**. Pour Linux, utilisez le code source Python directement (voir README.md principal).

### Comment désinstaller l'application ?

Supprimez simplement le dossier `TelloFaceTracking`. Aucune installation système n'est nécessaire.

---

## Support et ressources

### Documentation technique

Pour les utilisateurs avancés ou développeurs :
- **README.md** : Documentation technique complète
- **BUILD_INSTRUCTIONS.md** : Guide pour recompiler l'application

### Signaler un problème

Si vous rencontrez un problème non résolu :
1. Vérifiez d'abord cette documentation
2. Consultez la section [Dépannage](#dépannage)
3. Ouvrez un ticket sur GitHub (si applicable)

---

## Crédits

- **YOLO (Ultralytics)** : Modèle de détection d'objets
- **djitellopy** : Bibliothèque de contrôle du Tello
- **PyQt6** : Framework d'interface graphique
- **OpenCV** : Traitement d'image

---

## Licence

Ce projet utilise la licence **GPL-3.0**.

---

**Bon vol avec votre Tello ! 🚁✨**

Si ce guide vous a été utile, n'hésitez pas à le partager !

---

*Dernière mise à jour : Novembre 2025*

