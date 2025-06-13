from database import Database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_enhanced_table():
    db = Database()
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Vérifier les valeurs par défaut actuelles
            logger.info("Vérification des valeurs par défaut...")
            cursor.execute(
                """
                SELECT hauteur_max, hauteur_min, fournisseur_id, materiau_id
                FROM enhanced
                WHERE hauteur_max = 35 OR hauteur_min = 14
                OR fournisseur_id IS NULL OR materiau_id IS NULL
            """
            )
            problematic_rows = cursor.fetchall()
            logger.info(f"Trouvé {len(problematic_rows)} lignes problématiques")

            # 2. Mettre à jour les hauteurs par défaut
            logger.info("Mise à jour des hauteurs par défaut...")
            cursor.execute(
                """
                UPDATE enhanced
                SET hauteur_max = NULL
                WHERE hauteur_max = 35
            """
            )
            cursor.execute(
                """
                UPDATE enhanced
                SET hauteur_min = NULL
                WHERE hauteur_min = 14
            """
            )

            # 3. Essayer de lier les IDs manquants
            logger.info("Tentative de liaison des IDs manquants...")

            # Lier les fournisseurs
            cursor.execute(
                """
                UPDATE e
                SET e.fournisseur_id = f.id
                FROM enhanced e
                INNER JOIN fournisseurs f ON e.fournisseur = f.nom
                WHERE e.fournisseur_id IS NULL
            """
            )

            # Lier les matériaux
            cursor.execute(
                """
                UPDATE e
                SET e.materiau_id = m.id
                FROM enhanced e
                INNER JOIN materiaux m ON e.materiaux = m.nom
                WHERE e.materiau_id IS NULL
            """
            )

            # 4. Vérifier les résultats
            cursor.execute(
                """
                SELECT COUNT(*) as count,
                    SUM(CASE WHEN hauteur_max = 35 THEN 1 ELSE 0 END) as default_hauteur_max,
                    SUM(CASE WHEN hauteur_min = 14 THEN 1 ELSE 0 END) as default_hauteur_min,
                    SUM(CASE WHEN fournisseur_id IS NULL THEN 1 ELSE 0 END) as null_fournisseur,
                    SUM(CASE WHEN materiau_id IS NULL THEN 1 ELSE 0 END) as null_materiau
                FROM enhanced
            """
            )
            stats = cursor.fetchone()

            logger.info("Statistiques après correction :")
            logger.info(f"Total des lignes : {stats[0]}")
            logger.info(f"Hauteur max = 35 : {stats[1]}")
            logger.info(f"Hauteur min = 14 : {stats[2]}")
            logger.info(f"Fournisseur ID NULL : {stats[3]}")
            logger.info(f"Materiau ID NULL : {stats[4]}")

            conn.commit()
            logger.info("✅ Corrections terminées")

    except Exception as e:
        logger.error(f"❌ Erreur lors de la correction : {e}")
        raise


if __name__ == "__main__":
    fix_enhanced_table()
