# modules/formulario_manager.py
from database import get_db_conn # Conectar con la base de datos
from datetime import date, datetime # Fechas y horas
import json # JSON

class FormularioManager: # Gestiona formularios de inicio y fin
    def __init__(self):
        self.conn = get_db_conn()

    def _company_id(self, company_code): # ID de la empresa por código
        c = self.conn.cursor()
        c.execute("SELECT id FROM companies WHERE code = ?", (company_code,))
        r = c.fetchone()
        return r["id"] if r else None

    def _latest_route_for_driver_today(self, company_id, user_id): # Última ruta del conductor hoy
        today = date.today().isoformat()
        c = self.conn.cursor()
        c.execute("SELECT id FROM routes WHERE company_id = ? AND driver_user_id = ? AND date = ? ORDER BY id DESC LIMIT 1", (company_id, user_id, today))
        r = c.fetchone()
        return r["id"] if r else None

    def crear_form_inicio(self, company_code, user_id, hora_inicio, foto_path, firma): # Crear formulario de inicio
        """
        Guarda documento tipo 'inicio'. Vincula a la última ruta del conductor hoy si existe.
        """
        comp_id = self._company_id(company_code)
        if not comp_id:
            return False
        route_id = self._latest_route_for_driver_today(comp_id, user_id)
        c = self.conn.cursor()
        extra = {"hora": hora_inicio, "firma": firma}
        c.execute("INSERT INTO documents (route_id, user_id, type, filepath, timestamp, extra_json) VALUES (?, ?, ?, ?, ?, ?)",
                  (route_id, user_id, "inicio", foto_path or "", datetime.utcnow().isoformat(), json.dumps(extra, ensure_ascii=False)))
        self.conn.commit()
        return True

    def crear_form_fin(self, company_code, user_id, hora_fin, foto_final, lista_peajes, fotos_peajes, firma):
        #Guarda documento tipo 'final' y también guarda información de peajes en extra_json.
        #fotos_peajes puede ser una lista de paths (opcional).
        
        comp_id = self._company_id(company_code)
        if not comp_id: # Empresa no encontrada
            return False
        route_id = self._latest_route_for_driver_today(comp_id, user_id) # Ultima ruta del conductor hoy
        c = self.conn.cursor()
        extra = {"hora": hora_fin, "peajes": lista_peajes, "firma": firma, "peajes_files": fotos_peajes}
        c.execute("INSERT INTO documents (route_id, user_id, type, filepath, timestamp, extra_json) VALUES (?, ?, ?, ?, ?, ?)",
                  (route_id, user_id, "final", foto_final or "", datetime.utcnow().isoformat(), json.dumps(extra, ensure_ascii=False)))
        self.conn.commit()
        return True
