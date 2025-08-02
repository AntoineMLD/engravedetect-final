#!/usr/bin/env python3
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_admin():
    db = SessionLocal()
    try:
        # Vérifier si l'admin existe déjà
        from sqlalchemy import text
        result = db.execute(text("SELECT id FROM users WHERE username = 'admin'"))
        if result.fetchone():
            print("✅ L'utilisateur admin existe déjà")
            return
        
        # Créer l'admin
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        hashed_password = pwd_context.hash(admin_password)
        
        db.execute(text("""
            INSERT INTO users (username, email, hashed_password, email_confirmed, is_active)
            VALUES (:username, :email, :hashed_password, :email_confirmed, :is_active)
        """), {
            'username': 'admin',
            'email': admin_email,
            'hashed_password': hashed_password,
            'email_confirmed': True,
            'is_active': True
        })
        
        db.commit()
        print(f"✅ Utilisateur admin créé avec succès")
        print(f"   Email: {admin_email}")
        print(f"   Username: admin")
        print(f"   Password: {admin_password}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
