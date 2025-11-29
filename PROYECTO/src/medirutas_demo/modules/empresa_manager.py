#IGNORAR! -> AUN EN DESARROLLO / NO RELEVANTE POR EL MOMENTO -> Solo tenemos 1 empresa, esto es pa +1



from database import get_db # Conectar con base de datos

class EmpresaManager:
    def __init__(self):
        self.db = get_db()

    def crear_empresa(self, nombre):
        return self.db.execute(
            "INSERT INTO empresas (nombre) VALUES (?)", 
            (nombre,)
        )

    def listar_empresas(self):
        return self.db.query(
            "SELECT id, nombre FROM empresas"
        )

    def obtener_empresa(self, empresa_id):
        result = self.db.query(
            "SELECT id, nombre FROM empresas WHERE id = ?", 
            (empresa_id,)
        )
        return result[0] if result else None
