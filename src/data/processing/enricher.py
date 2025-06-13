import logging
import json
import re
from typing import List, Dict, Any
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...api.models.verres import Verre
from ...api.models.references import Fournisseur
from ...api.core.config import settings


class DataEnricher:
    """
    Classe pour enrichir les données de la table enhanced vers la table verres.
    Ajoute des informations extraites et traitées à partir des données brutes.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Mots-clés pour la détection des caractéristiques
        self.PROTECTION_KEYWORDS = [
            "protect",
            "uv",
            "blue",
            "bleu",
            "anti",
            "shield",
            "safe",
            "eye protect",
        ]

        self.PHOTOCHROMIC_KEYWORDS = [
            "transition",
            "photochrom",
            "xtractive",
            "sensitiv",
            "variable",
            "adapt",
        ]

    def extract_variante(self, nom_complet: str, nom_base: str) -> str:
        """Extrait la variante en comparant le nom complet et le nom de base."""
        if not nom_base or not nom_complet:
            return ""
        variante = nom_complet.replace(nom_base, "").strip()
        return variante if variante else ""

    def detect_protection(self, nom: str) -> bool:
        """Détecte si le verre a des propriétés de protection."""
        nom_lower = nom.lower()
        return any(keyword in nom_lower for keyword in self.PROTECTION_KEYWORDS)

    def detect_photochromic(self, nom: str) -> bool:
        """Détecte si le verre est photochromique."""
        nom_lower = nom.lower()
        return any(keyword in nom_lower for keyword in self.PHOTOCHROMIC_KEYWORDS)

    def extract_tags(self, nom: str) -> List[str]:
        """Extrait les tags pertinents du nom du verre."""
        tags = []
        nom_lower = nom.lower()

        # Détection du type de verre
        if any(x in nom_lower for x in ["progress", "varilux"]):
            tags.append("progressif")
        elif "unifocal" in nom_lower:
            tags.append("unifocal")

        # Détection des traitements
        if self.detect_protection(nom):
            tags.append("protection")
        if self.detect_photochromic(nom):
            tags.append("photochromique")

        # Détection des matériaux spéciaux
        if "transition" in nom_lower:
            tags.append("transitions")
        if "polarisant" in nom_lower or "polar" in nom_lower:
            tags.append("polarisant")

        return list(set(tags))  # Enlever les doublons

    def extract_hauteurs(self, nom: str) -> tuple:
        """Extrait les hauteurs min et max si spécifiées dans le nom."""
        hauteur_pattern = r"(\d+)(?:\s*[-/]\s*(\d+))?\s*mm"
        match = re.search(hauteur_pattern, nom)

        if match:
            min_h = int(match.group(1))
            max_h = int(match.group(2)) if match.group(2) else min_h
            return min_h, max_h
        return None, None

    def clean_nom(self, nom: str) -> str:
        """Nettoie le nom en enlevant les informations de hauteur et autres détails."""
        # Enlever les hauteurs
        nom = re.sub(r"\d+\s*[-/]\s*\d+\s*mm", "", nom)
        nom = re.sub(r"\d+\s*mm", "", nom)

        # Enlever les espaces multiples
        nom = " ".join(nom.split())
        return nom.strip()

    def enrich_data(self, enhanced_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Enrichit les données de enhanced pour la table verres.

        Args:
            enhanced_data: DataFrame contenant les données de la table enhanced

        Returns:
            List[Dict]: Liste des données enrichies pour insertion dans verres
        """
        enriched_records = []

        # Charger les fournisseurs existants
        session = self.SessionLocal()
        try:
            fournisseurs = {f.nom: f.id for f in session.query(Fournisseur).all()}

            for _, row in enhanced_data.iterrows():
                nom_complet = row["nom_verre"]
                nom_nettoye = self.clean_nom(nom_complet)
                hauteur_min, hauteur_max = self.extract_hauteurs(nom_complet)

                # Gérer le fournisseur
                fournisseur_nom = row["fournisseur"]
                fournisseur_id = None
                if fournisseur_nom in fournisseurs:
                    fournisseur_id = fournisseurs[fournisseur_nom]
                else:
                    # Créer le fournisseur s'il n'existe pas
                    nouveau_fournisseur = Fournisseur(nom=fournisseur_nom)
                    session.add(nouveau_fournisseur)
                    session.flush()  # Pour obtenir l'ID
                    fournisseur_id = nouveau_fournisseur.id
                    fournisseurs[fournisseur_nom] = fournisseur_id

                # Traitement de l'indice
                if pd.notna(row["indice"]):  # Utiliser la colonne originale
                    try:
                        indice = float(row["indice"])
                        if 1.0 <= indice <= 2.0:
                            return indice
                    except (ValueError, TypeError):
                        pass

                record = {
                    "nom": nom_nettoye,
                    "materiaux": row["materiaux"],
                    "indice": indice,
                    "fournisseur_id": fournisseur_id,
                    "gravure": row["gravure_nasale"],
                    "url_source": row["source_url"],
                    "variante": self.extract_variante(nom_complet, nom_nettoye),
                    "hauteur_min": hauteur_min,
                    "hauteur_max": hauteur_max,
                    "protection": self.detect_protection(nom_complet),
                    "photochromic": self.detect_photochromic(nom_complet),
                    "tags": json.dumps(self.extract_tags(nom_complet)),
                    "image_gravure": None,  # À remplir plus tard avec le chemin de l'image
                }

                enriched_records.append(record)

            session.commit()
            return enriched_records

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def process_enhanced_to_verres(self):
        """
        Traite les données de la table enhanced et les insère dans la table verres
        avec les enrichissements.
        """
        try:
            # 1. Charger les données de enhanced
            with self.engine.connect() as conn:
                enhanced_data = pd.read_sql("SELECT * FROM enhanced ORDER BY id", conn)

            if enhanced_data.empty:
                self.logger.warning("⚠️ Aucune donnée trouvée dans la table enhanced")
                return

            self.logger.info(f"📊 {len(enhanced_data)} lignes chargées depuis enhanced")

            # 2. Enrichir les données
            enriched_records = self.enrich_data(enhanced_data)
            self.logger.info(f"✨ Données enrichies générées : {len(enriched_records)} enregistrements")

            # 3. Vider la table verres
            session = self.SessionLocal()
            try:
                session.query(Verre).delete()
                session.commit()
                self.logger.info("🗑️ Table verres vidée")

                # 4. Insérer les nouvelles données
                for record in enriched_records:
                    verre = Verre(**record)
                    session.add(verre)

                session.commit()
                self.logger.info(f"✅ {len(enriched_records)} verres insérés avec succès")

            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()

        except Exception as e:
            self.logger.error(f"❌ Erreur lors du traitement enhanced -> verres : {str(e)}")
            raise


def main():
    """Point d'entrée du script."""
    enricher = DataEnricher()
    enricher.process_enhanced_to_verres()


if __name__ == "__main__":
    main()
