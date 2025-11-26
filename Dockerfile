# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires pour OpenCV et Qt
# libgl1-mesa-glx : pour OpenGL
# libglib2.0-0 : pour GLib
# libsm6, libxext6, libxrender-dev : pour le rendu X11
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .
COPY requirements_tello.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_tello.txt

# Copier le reste du code source
COPY . .

# Définir la variable d'environnement pour l'affichage (sera écrasée au runtime)
ENV DISPLAY=host.docker.internal:0.0

# Commande par défaut pour lancer l'application
CMD ["python", "tello_face_tracking.py"]
