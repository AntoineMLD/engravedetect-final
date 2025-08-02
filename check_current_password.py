#!/usr/bin/env python3
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_current_password():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT hashed_password FROM users WHERE username = 'admin'"))
        user = result.fetchone()
        
        if user:
            current_hash = user[0]
            print(f"Hash actuel: {current_hash}")
            
            # Tester différents mots de passe
            passwords_to_test = ["adminpass123", "admin123", "admin", "password"]
            
            for password in passwords_to_test:
                is_valid = pwd_context.verify(password, current_hash)
                print(f"'{password}' est valide: {is_valid}")
                
        else:
            print("Admin non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_current_password()
