# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires pour OpenCV et Qt
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source
COPY . .

# Définir la variable d'environnement pour l'affichage (sera écrasée au runtime)
ENV DISPLAY=host.docker.internal:0.0
ENV QT_QPA_PLATFORM=xcb

# Commande par défaut pour lancer l'application
CMD ["python", "-u", "tello_face_tracking.py"]
