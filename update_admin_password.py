#!/usr/bin/env python3
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_admin_password():
    db = SessionLocal()
    try:
        # Nouveau mot de passe
        new_password = "adminpass123"
        hashed_password = pwd_context.hash(new_password)
        
        # Mettre à jour le mot de passe
        result = db.execute(text("""
            UPDATE users 
            SET hashed_password = :hashed_password, 
                email_confirmed = true, 
                is_active = true 
            WHERE username = 'admin'
        """), {
            'hashed_password': hashed_password
        })
        
        if result.rowcount > 0:
            db.commit()
            print(f"✅ Mot de passe admin mis à jour avec succès")
            print(f"   Username: admin")
            print(f"   Nouveau password: {new_password}")
        else:
            print("❌ Utilisateur admin non trouvé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_password()
