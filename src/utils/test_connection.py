import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scrapy_project.france_optique.pipelines import AzureSQLPipeline

def test_connection():
    try:
        pipeline = AzureSQLPipeline()
        if pipeline.test_connection():
            print("✅ Connexion à la base de données réussie!")
        else:
            print("❌ Échec de la connexion à la base de données")
    except Exception as e:
        print(f"❌ Erreur lors du test de connexion : {str(e)}")

if __name__ == "__main__":
    test_connection()