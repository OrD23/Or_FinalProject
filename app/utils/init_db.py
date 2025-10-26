# app/utils/init_db.py

from app.database import engine, Base
import app.models  # ensure all models are imported and registered


def init_db(drop_first: bool = False):
    """
    Initialize the database schema.

    If drop_first is True, first dispose of all existing connections
    (so SQLite won’t deadlock), then drop every table before recreating them.
    """
    if drop_first:
        print("🔄 Disposing engine connections…")
        engine.dispose()
        
        print("🗑‍ Dropping existing tables…")
        Base.metadata.drop_all(bind=engine)
    
    print("📦 Creating database tables…")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Done.")


if __name__ == "__main__":
    # Usage: python app/utils/init_db.py
    # pass True to drop existing tables first
    init_db(drop_first=True)
