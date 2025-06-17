# Utiliser Python 3.11 comme image de base
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires (version minimale)
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers du projet
COPY . .

# Créer les répertoires nécessaires et donner les permissions
RUN mkdir -p EXCEL PROMPT \
    && chmod -R 777 /app

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Exécuter en tant que root pour avoir toutes les permissions
# Note: Ceci est moins sécurisé, mais permet une modification complète des fichiers

# Exposer le port si nécessaire (optionnel)
# EXPOSE 8000

# Commande par défaut
CMD ["python", "main.py"]