FROM node:alpine

# Installer serve (un serveur web léger)
RUN npm install -g serve

# Créer le répertoire de travail
WORKDIR /app

# Créer le dossier pour les images
RUN mkdir -p /app/data/oversampled_gravures

# Copier les fichiers individuellement pour éviter les problèmes d'espaces
COPY index.html /app/
COPY style.css /app/
COPY app.js /app/
COPY api.js /app/
COPY favicon.ico /app/
COPY logo_engravedetect.png /app/

# Exposer le port 80
EXPOSE 80

# Lancer le serveur avec un lien symbolique pour les images (tolérant à l'existence du lien)
CMD serve -p 80 -s .
