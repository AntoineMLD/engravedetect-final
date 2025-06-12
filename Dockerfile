# Utiliser une image Python officielle comme image de base
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Installer le pilote ODBC pour SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get remove -y unixodbc unixodbc-dev \
    && apt-get purge -y unixodbc* \
    && ACCEPT_EULA=Y DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        unixodbc-dev \
        msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Variables d'environnement
ARG DATABASE_URL
ARG SECRET_KEY
ENV DATABASE_URL=$DATABASE_URL
ENV SECRET_KEY=$SECRET_KEY

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pyodbc==4.0.39

# Copier le reste du code de l'application
COPY src/ ./src/

# Exposer le port sur lequel l'application s'exécute
EXPOSE 8000

# Commande pour démarrer l'application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 