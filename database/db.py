import sqlite3
import os
from pathlib import Path
from config import Config

def is_postgresql():
    db_url = Config.DATABASE_URL
    return db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://"))

def get_db_connection():
    db_url = Config.DATABASE_URL
    
    if is_postgresql():
        try:
            import psycopg2
            import psycopg2.extras
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
            return conn
        except Exception as e:
            print(f"Warning: Failed to connect to PostgreSQL ({e}). Falling back to SQLite.")

    # SQLite Fallback
    db_path = Config.DATABASE_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def run_migrations(conn):
    """Auto-migrate schema columns for existing database files."""
    cursor = conn.cursor()

    # Check analyses.company_name
    try:
        cursor.execute("SELECT company_name FROM analyses LIMIT 1;")
    except Exception:
        try:
            cursor.execute("ALTER TABLE analyses ADD COLUMN company_name TEXT;")
            print("Migrated schema: Added company_name to analyses.")
        except Exception:
            pass

    # Check analyses.resume_version_id
    try:
        cursor.execute("SELECT resume_version_id FROM analyses LIMIT 1;")
    except Exception:
        try:
            cursor.execute("ALTER TABLE analyses ADD COLUMN resume_version_id INTEGER;")
            print("Migrated schema: Added resume_version_id to analyses.")
        except Exception:
            pass

    # Check profiles.phone
    try:
        cursor.execute("SELECT phone FROM profiles LIMIT 1;")
    except Exception:
        try:
            cursor.execute("ALTER TABLE profiles ADD COLUMN phone TEXT;")
            print("Migrated schema: Added phone to profiles.")
        except Exception:
            pass

    # Check profiles.target_role
    try:
        cursor.execute("SELECT target_role FROM profiles LIMIT 1;")
    except Exception:
        try:
            cursor.execute("ALTER TABLE profiles ADD COLUMN target_role TEXT DEFAULT 'Software Engineer';")
            print("Migrated schema: Added target_role to profiles.")
        except Exception:
            pass

    conn.commit()

def init_db():
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    conn = get_db_connection()
    if is_postgresql() and hasattr(conn, 'cursor'):
        pg_sql = schema_sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        pg_sql = pg_sql.replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        cursor = conn.cursor()
        cursor.execute(pg_sql)
        conn.commit()
        cursor.close()
    else:
        conn.executescript(schema_sql)
        conn.commit()
        run_migrations(conn)

    conn.close()
    print("Database schema initialized and migrated successfully.")

if __name__ == "__main__":
    init_db()
