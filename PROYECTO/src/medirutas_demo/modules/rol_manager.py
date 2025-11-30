# modules/rol_manager.py
from database import get_db_conn
import sqlite3

class RolManager: # Gestión de roles
    def __init__(self):
        self.conn = get_db_conn()

    def _company_id(self, company_code): # Id de la empresa
        c = self.conn.cursor()
        c.execute("SELECT id FROM companies WHERE code = ?", (company_code,))
        r = c.fetchone()
        return r["id"] if r else None

    def crear_rol(self, company_code, nombre, codigo, is_admin=False): # Crear rol
        
        #Crea un rol para la empresa. Retorna True si se creó, False si ya existe.
        
        comp_id = self._company_id(company_code)
        if not comp_id: # Empresa no existe
            return False
        c = self.conn.cursor()
        # Verificar si el código ya existe
        c.execute("SELECT id FROM roles WHERE company_id = ? AND code = ?", (comp_id, codigo))
        if c.fetchone():
            return False
        try:
            c.execute("INSERT INTO roles (company_id, name, code, is_admin) VALUES (?, ?, ?, ?)",
                     (comp_id, nombre, codigo, 1 if is_admin else 0))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_roles(self, company_code):
        #Retornar lista de tuplas (id, name, code, is_admin) para la empresa.
        
        comp_id = self._company_id(company_code)
        if not comp_id:
            return []
        c = self.conn.cursor()
        c.execute("SELECT id, name, code, is_admin FROM roles WHERE company_id = ?", (comp_id,))
        return [(r["id"], r["name"], r["code"], bool(r["is_admin"])) for r in c.fetchall()]

    def get_role_by_code(self, company_code, role_code):
        #Retorna el rol con el código dado, o None si no existe.
        
        comp_id = self._company_id(company_code)
        if not comp_id:
            return None
        c = self.conn.cursor()
        c.execute("SELECT id, name, code, is_admin FROM roles WHERE company_id = ? AND code = ?", 
                 (comp_id, role_code))
        r = c.fetchone()
        if r:
            return {"id": r["id"], "name": r["name"], "code": r["code"], "is_admin": bool(r["is_admin"])}
        return None
