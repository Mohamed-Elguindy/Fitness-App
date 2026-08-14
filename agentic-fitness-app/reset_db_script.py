import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text
from app.models.domain import Base

def reset_db():
    print("Dropping tables with CASCADE...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS generated_diets CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS generated_programs CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS user_profiles CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.commit()
    
    print("Recreating tables...")
    Base.metadata.create_all(bind=engine)
    print("DONE!")

if __name__ == "__main__":
    reset_db()
