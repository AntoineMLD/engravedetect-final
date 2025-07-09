FROM node:alpine

# Installer serve (un serveur web léger)
RUN npm install -g serve

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers de ton app
COPY index.html /app/
COPY style.css /app/
COPY app.js /app/
COPY api.js /app/
COPY favicon.ico /app/
COPY logo_engravedetect.png /app/

# Copier les IMAGES
COPY data/oversampled_gravures /app/data/oversampled_gravures

# Exposer le port 80
EXPOSE 80

# Lancer le serveur
CMD serve -p 80 -s .
