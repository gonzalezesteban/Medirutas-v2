# database.py
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # esto es para saber el directorio en el que esta (src/medirutas_demo)
DB_PATH = os.path.join(BASE_DIR, "medirutas.db") # llamar la base de datos

def get_db_conn(): # conectar la base de datos
    """
    Devuelve una conexión sqlite3 con row_factory configurada.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(): # inicializar la base de datos
    """
    Crea las tablas necesarias y garantiza la existencia de la
    company/role/admin líder por defecto (códigos 0000).
    """
    conn = get_db_conn()
    c = conn.cursor()
    c.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        code TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        name TEXT,
        code TEXT,
        is_admin INTEGER DEFAULT 0,
        FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        role_id INTEGER,
        name TEXT,
        password TEXT,
        created_at TEXT,
        FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
        FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        name TEXT,
        cost_per_hour REAL DEFAULT 0,
        FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS routes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        service_id INTEGER,
        date TEXT,
        start_time TEXT,
        start_location TEXT,
        driver_user_id INTEGER,
        created_by INTEGER,
        FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
        FOREIGN KEY(service_id) REFERENCES services(id) ON DELETE SET NULL,
        FOREIGN KEY(driver_user_id) REFERENCES users(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS stops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id INTEGER,
        address TEXT,
        lat TEXT,
        lng TEXT,
        order_index INTEGER,
        FOREIGN KEY(route_id) REFERENCES routes(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id INTEGER,
        user_id INTEGER,
        type TEXT,
        filepath TEXT,
        timestamp TEXT,
        extra_json TEXT,
        FOREIGN KEY(route_id) REFERENCES routes(id) ON DELETE CASCADE,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS billing_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        driver_user_id INTEGER,
        month_year TEXT,
        details_json TEXT,
        total_amount REAL,
        FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
        FOREIGN KEY(driver_user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)
    conn.commit()

    # Agregar columna permissions_json si no existe
    try:
        c.execute("ALTER TABLE users ADD COLUMN permissions_json TEXT")
        conn.commit()
    except:
        pass  # La columna ya existe

    # por defecto: (company code 0000, role code 0000, user admin_lider/password 0000)
    c.execute("SELECT id FROM companies WHERE code = ?", ("0000",))
    comp = c.fetchone()
    if not comp: # si no existe la compañia
        c.execute("INSERT INTO companies (name, code) VALUES (?, ?)", ("Empresa Inicial", "0000"))
        conn.commit()
        comp_id = c.lastrowid
    else: # si si existe
        comp_id = comp["id"]

    c.execute("SELECT id FROM roles WHERE company_id = ? AND code = ?", (comp_id, "0000"))
    role = c.fetchone()
    if not role: # si no existe el rol
        c.execute("INSERT INTO roles (company_id, name, code, is_admin) VALUES (?, ?, ?, ?)",
                  (comp_id, "Admin Líder", "0000", 1))
        conn.commit()
        role_id = c.lastrowid
    else: # si si existe
        role_id = role["id"]

    c.execute("SELECT id FROM users WHERE company_id = ? AND role_id = ?", (comp_id, role_id))
    user = c.fetchone()
    if not user: # si no existe el usuario
        now = datetime.utcnow().isoformat()
        c.execute("INSERT INTO users (company_id, role_id, name, password, created_at) VALUES (?, ?, ?, ?, ?)",
                  (comp_id, role_id, "admin_lider", "0000", now))
        conn.commit()

    conn.close()

# Ejecutar init_db
if __name__ == "__main__":
    init_db()
    print(f"Base de datos inicializada en: {DB_PATH}")
