# main.py
#!/usr/bin/env python3
"""
Entry point para la demo Medirutas (Tkinter).
Este main importa la inicialización de la base (database.py).
"""

import os #manejo de rutas y directorios
import json #manejo de permisos en JSON
from datetime import datetime, date #fechas y horas
import tkinter as tk #interfaz gráfica
from tkinter import ttk, filedialog, messagebox #adiciones de diseño
from PIL import Image, ImageTk, ImageOps #manejar imágenes

# importa funciones de database.py
from database import get_db_conn, init_db, BASE_DIR

# directorios assets/uploads
ASSETS_DIR = os.path.join(BASE_DIR, "assets") #para logos, iconos
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads") #para archivos subidos
os.makedirs(ASSETS_DIR, exist_ok=True) #asegurarse que existen
os.makedirs(UPLOAD_DIR, exist_ok=True) #asegurarse que existen

# Inicializar (crear tablas y admin por defecto)
init_db()

# ---------- Resto del código de la UI ----------

import sqlite3 #base de datos

def get_conn(): #conectar la base de datos
    return get_db_conn()

class App: 
    def __init__(self, root): #inicializar la app
        self.root = root
        root.title("Medirutas - Demo") #de aqui para abajo es el diseño
        root.geometry("1100x700")
        # Left panel (fixed lateral panel that acts as sliding panel)
        self.left_panel = tk.Frame(root, width=260, bg="#f0f0f0")
        self.left_panel.pack(side="left", fill="y")
        # Main area
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(side="right", expand=True, fill="both")
        # Header in left panel
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.resize((220, 80))
            self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(self.left_panel, image=self.logo_img, bg="#f0f0f0").pack(pady=10)
        else:
            tk.Label(self.left_panel, text="Medirutas", bg="#f0f0f0", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self.left_panel, text="Slogan de la app", bg="#f0f0f0").pack(pady=(0,10))

        # initialize session
        self.conn = get_conn()
        self.current_user = None
        self.build_auth_ui()

    # Authentication UI (login/register)
    def build_auth_ui(self):
        for w in self.main_frame.winfo_children():
            w.destroy()
        frm = tk.Frame(self.main_frame, padx=20, pady=20)
        frm.pack(expand=True)
        tk.Label(frm, text="Autenticación", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=(0,10))
        self.auth_mode = tk.StringVar(value="login")
        tk.Radiobutton(frm, text="Iniciar sesión", variable=self.auth_mode, value="login", command=self._render_auth_form).grid(row=1, column=0, sticky="w")
        tk.Radiobutton(frm, text="Crear cuenta", variable=self.auth_mode, value="register", command=self._render_auth_form).grid(row=1, column=1, sticky="w")
        self.form_area = tk.Frame(frm)
        self.form_area.grid(row=2, column=0, columnspan=2, pady=10)
        self._render_auth_form()

    def _render_auth_form(self): #formulario login/registro
        for w in self.form_area.winfo_children():
            w.destroy()
        mode = self.auth_mode.get()
        if mode == "login":
            tk.Label(self.form_area, text="Código de empresa").grid(row=0, column=0, sticky="e") #diseño del formulario de login
            self.login_company = tk.Entry(self.form_area); self.login_company.grid(row=0, column=1)
            tk.Label(self.form_area, text="Nombre usuario").grid(row=1, column=0, sticky="e")
            self.login_name = tk.Entry(self.form_area); self.login_name.grid(row=1, column=1)
            tk.Label(self.form_area, text="Contraseña").grid(row=2, column=0, sticky="e")
            self.login_pass = tk.Entry(self.form_area, show="*"); self.login_pass.grid(row=2, column=1)
            tk.Button(self.form_area, text="Iniciar sesión", command=self._do_login, width=20).grid(row=3, column=0, columnspan=2, pady=8)
            tk.Label(self.form_area, text="(Para demo: empresa 0000, usuario admin_lider, pass 0000)").grid(row=4, column=0, columnspan=2, pady=(6,0))
        else:
            tk.Label(self.form_area, text="Código de empresa").grid(row=0, column=0, sticky="e") #diseño del formulario de registro
            self.reg_company = tk.Entry(self.form_area); self.reg_company.grid(row=0, column=1)
            tk.Label(self.form_area, text="Código de rol").grid(row=1, column=0, sticky="e")
            self.reg_role = tk.Entry(self.form_area); self.reg_role.grid(row=1, column=1)
            tk.Label(self.form_area, text="Nombre usuario").grid(row=2, column=0, sticky="e")
            self.reg_name = tk.Entry(self.form_area); self.reg_name.grid(row=2, column=1)
            tk.Label(self.form_area, text="Contraseña").grid(row=3, column=0, sticky="e")
            self.reg_pass = tk.Entry(self.form_area, show="*"); self.reg_pass.grid(row=3, column=1)
            tk.Label(self.form_area, text="Confirmar contraseña").grid(row=4, column=0, sticky="e")
            self.reg_pass2 = tk.Entry(self.form_area, show="*"); self.reg_pass2.grid(row=4, column=1)
            tk.Button(self.form_area, text="Crear cuenta", command=self._do_register, width=20).grid(row=5, column=0, columnspan=2, pady=8)
            tk.Label(self.form_area, text="(La primera cuenta creada con company code 0000 y role code 0000 es Admin Líder)").grid(row=6, column=0, columnspan=2, pady=(6,0))

    def _do_login(self): #parte lógica del login
        company_code = self.login_company.get().strip(); name = self.login_name.get().strip(); password = self.login_pass.get()
        if not (company_code and name and password): #si esta incompleto
            messagebox.showerror("Error", "Complete todos los campos"); return
        c = self.conn.cursor()
        c.execute("SELECT id FROM companies WHERE code = ?", (company_code,))
        comp = c.fetchone()
        if not comp: #Codigo de la empresa incorrecto
            messagebox.showerror("Error", "Código de empresa inválido"); return
        comp_id = comp["id"]
        c.execute("SELECT * FROM users WHERE company_id = ? AND name = ? AND password = ?", (comp_id, name, password))
        user = c.fetchone()
        if not user: #cuando las credenciales (usuario/contraseña) son inválidas
            messagebox.showerror("Error", "Credenciales inválidas"); return
        c.execute("SELECT is_admin FROM roles WHERE id = ?", (user["role_id"],))
        role = c.fetchone()
        is_admin = bool(role["is_admin"]) if role else False
        self.current_user = {"id": user["id"], "name": user["name"], "company_id": user["company_id"], "company_code": company_code, "role_id": user["role_id"], "is_admin": is_admin}
        self.build_main_ui()

    def _do_register(self): #parte lógica del registro
        company_code = self.reg_company.get().strip(); role_code = self.reg_role.get().strip()
        name = self.reg_name.get().strip(); p1 = self.reg_pass.get(); p2 = self.reg_pass2.get()
        if not (company_code and role_code and name and p1 and p2): #si esta incompleto
            messagebox.showerror("Error", "Complete todos los campos"); return
        if p1 != p2: #si las contraseñas no coinciden
            messagebox.showerror("Error", "Contraseñas no coinciden"); return
        c = self.conn.cursor()
        c.execute("SELECT id FROM companies WHERE code = ?", (company_code,))
        comp = c.fetchone()
        if not comp: #si el codigo de la empresa es incorrecto
            messagebox.showerror("Error", "Código de empresa inválido"); return
        comp_id = comp["id"]
        
        # Verificar si es la primera cuenta (company_code 0000 y role_code 0000)
        # Si es así, crear el rol si no existe
        if company_code == "0000" and role_code == "0000": #Admin líder
            c.execute("SELECT id FROM roles WHERE company_id = ? AND code = ?", (comp_id, role_code))
            role = c.fetchone()
            if not role:
                # Crear el rol de admin líder
                c.execute("INSERT INTO roles (company_id, name, code, is_admin) VALUES (?, ?, ?, ?)",
                         (comp_id, "Admin Líder", "0000", 1))
                self.conn.commit()
                role_id = c.lastrowid
            else: #ya existe el rol
                role_id = role["id"]
        else: #Para otros roles
            c.execute("SELECT id FROM roles WHERE company_id = ? AND code = ?", (comp_id, role_code))
            role = c.fetchone()
            if not role: #si el codigo de rol es incorrecto
                messagebox.showerror("Error", "Código de rol inválido"); return
            role_id = role["id"]
        
        # Verificar si el usuario ya existe
        c.execute("SELECT id FROM users WHERE company_id = ? AND name = ?", (comp_id, name))
        if c.fetchone():
            messagebox.showerror("Error", "El nombre de usuario ya existe"); return
        
        now = datetime.utcnow().isoformat()
        try: #crear el usuario
            c.execute("INSERT INTO users (company_id, role_id, name, password, created_at) VALUES (?,?,?,?,?)", (comp_id, role_id, name, p1, now))
            self.conn.commit()
            messagebox.showinfo("Listo", "Cuenta creada correctamente. Inicie sesión.")
            self.auth_mode.set("login"); self._render_auth_form()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"No se pudo crear usuario: {e}")

    # Construir la UI despues del login
    def build_main_ui(self):
        # agregar botones al panel lateral según el rol
        for w in self.left_panel.winfo_children(): #limpiar/cambiar el panel
            w.destroy()
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path): #agregar logo
            img = Image.open(logo_path); img = img.resize((220,80)); self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(self.left_panel, image=self.logo_img, bg="#f0f0f0").pack(pady=10)
        else: #por si no carga el logo
            tk.Label(self.left_panel, text="Medirutas", bg="#f0f0f0", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self.left_panel, text=f"Usuario: {self.current_user['name']}", bg="#f0f0f0").pack(pady=(0,10))

        menu_items = [("Inicio", self.win_inicio)] #botones
        if self.current_user["is_admin"]: #si es admin
            # Verificar si es admin líder (tiene todos los permisos)
            c = self.conn.cursor()
            c.execute("SELECT code FROM roles WHERE id = ?", (self.current_user["role_id"],))
            role = c.fetchone()
            is_lider = role and role["code"] == "0000"
            
            if is_lider:
                # Admin líder tiene todos los permisos
                menu_items += [
                    ("Crear rutas", self.win_crear_rutas),
                    ("Cuentas de cobro", self.win_cuentas_cobro),
                    ("Documentos", self.win_documentos),
                    ("Lista de usuarios", self.win_lista_usuarios),
                    ("Reportar problema", self.win_reportar),
                    ("Crear servicios", self.win_crear_servicios),
                    ("Crear códigos", self.win_crear_codigos),
                    ("Permisos", self.win_permisos)
                ]
            else:
                # Admin normal: verificar permisos otorgados
                c.execute("SELECT permissions_json FROM users WHERE id = ?", (self.current_user["id"],))
                user = c.fetchone()
                permissions = []
                if user and user["permissions_json"]:
                    try:
                        permissions = json.loads(user["permissions_json"])
                    except:
                        pass
                
                # De permisos a funciones
                perm_map = {
                    "Crear rutas": self.win_crear_rutas,
                    "Cuentas de cobro": self.win_cuentas_cobro,
                    "Documentos": self.win_documentos,
                    "Lista de usuarios": self.win_lista_usuarios,
                    "Reportar problema": self.win_reportar,
                    "Crear servicios": self.win_crear_servicios,
                    "Crear códigos": self.win_crear_codigos,
                    "Permisos": self.win_permisos
                }
                
                for perm in permissions:
                    if perm in perm_map:
                        menu_items.append((perm, perm_map[perm]))
        else: #si es conductor
            menu_items += [
                ("Horario", self.win_horario),
                ("Cuentas de cobro", self.win_cuentas_cobro)
            ]
        for (label, cmd) in menu_items: #crear botones
            btn = tk.Button(self.left_panel, text=label, width=24, command=cmd); btn.pack(pady=4)
        tk.Button(self.left_panel, text="Cerrar sesión", width=24, fg="red", command=self._logout).pack(side="bottom", pady=10)
        self.win_inicio()

    def _logout(self): #cerrar sesión
        self.current_user = None
        for w in self.left_panel.winfo_children(): w.destroy()
        tk.Label(self.left_panel, text="Medirutas", bg="#f0f0f0", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self.left_panel, text="Slogan de la app", bg="#f0f0f0").pack(pady=(0,10))
        for w in self.main_frame.winfo_children(): w.destroy()
        self.build_auth_ui()

    def win_inicio(self): #diseño del inicio
        for w in self.main_frame.winfo_children(): w.destroy()
        frm = tk.Frame(self.main_frame, padx=10, pady=10); frm.pack(fill="both", expand=True)
        tk.Label(frm, text="Inicio", font=("Arial",16)).pack(anchor="nw")
        tk.Label(frm, text=f"Bienvenido {self.current_user['name']}").pack(anchor="nw", pady=(6,10))
        
        if self.current_user["is_admin"]:
            # Vista para administradores
            search_frame = tk.Frame(frm); search_frame.pack(anchor="ne", fill="x")
            tk.Label(search_frame, text="Buscar conductor:").pack(side="left")
            self.search_var = tk.StringVar(); tk.Entry(search_frame, textvariable=self.search_var).pack(side="left")
            tk.Button(search_frame, text="Buscar", command=self._search_conductor).pack(side="left", padx=6)
            content = tk.Frame(frm); content.pack(fill="both", expand=True, pady=10)
            left = tk.Frame(content); left.pack(side="left", fill="both", expand=True)
            right = tk.Frame(content, width=420); right.pack(side="right", fill="y")
            logo_path = os.path.join(ASSETS_DIR, "logo.png")
            if os.path.exists(logo_path): #agregar logo
                img = Image.open(logo_path).resize((300,120)); imgtk = ImageTk.PhotoImage(img); tk.Label(left, image=imgtk).pack(); self._logo_imgtk = imgtk
            tk.Label(left, text="Slogan de la App", font=("Arial",12)).pack()
            map_path = os.path.join(ASSETS_DIR, "map_placeholder.png")
            if os.path.exists(map_path): #poner el mapa (en este momento puse una imagen)
                mimg = Image.open(map_path).resize((400,300)); self._map_imgtk = ImageTk.PhotoImage(mimg); tk.Label(right, image=self._map_imgtk).pack()
            else: #por si no nos carga el mapa
                tk.Label(right, text="[mapa estático aquí]", width=50, height=15, bg="#ddd").pack()
            bottom = tk.Frame(frm); bottom.pack(fill="both", expand=True)
            leftb = tk.Frame(bottom); leftb.pack(side="left", fill="both", expand=True)
            tk.Label(leftb, text="Direcciones de hoy", font=("Arial",12,"bold")).pack(anchor="w")
            tree = ttk.Treeview(leftb, columns=("route","address"), show="headings"); tree.heading("route", text="Ruta ID"); tree.heading("address", text="Dirección"); tree.pack(fill="both", expand=True)
            c = self.conn.cursor(); today = date.today().isoformat()
            c.execute("SELECT id FROM routes WHERE company_id = ? AND date = ?", (self.current_user["company_id"], today))
            for r in c.fetchall(): #una tabla con las rutas de hoy
                rid = r["id"]
                c2 = self.conn.cursor(); c2.execute("SELECT address FROM stops WHERE route_id = ? ORDER BY order_index", (rid,))
                for s in c2.fetchall(): #agregar las paradas
                    tree.insert("", "end", values=(rid, s["address"]))
            tk.Label(leftb, text="(Use el panel lateral para navegar)").pack(anchor="e", pady=4)
        else:
            # Vista para conductores
            top_frame = tk.Frame(frm); top_frame.pack(fill="x", pady=10)
            info_frame = tk.Frame(top_frame); info_frame.pack(side="left", fill="both", expand=True)
            
            # Obtener ruta de hoy
            c = self.conn.cursor(); today = date.today().isoformat()
            c.execute("SELECT id, start_time, start_location FROM routes WHERE company_id = ? AND driver_user_id = ? AND date = ? ORDER BY id DESC LIMIT 1", 
                      (self.current_user["company_id"], self.current_user["id"], today))
            route = c.fetchone()
            
            if route: #si hay ruta asignada
                tk.Label(info_frame, text=f"Ubicación de inicio: {route['start_location']}", font=("Arial", 12)).pack(anchor="w")
                tk.Label(info_frame, text=f"Hora de inicio: {route['start_time']}", font=("Arial", 12)).pack(anchor="w")
                
                # Verificar si ya hay formulario de inicio
                c.execute("SELECT id FROM documents WHERE route_id = ? AND user_id = ? AND type = 'inicio'", (route["id"], self.current_user["id"]))
                has_inicio = c.fetchone() is not None
                c.execute("SELECT id FROM documents WHERE route_id = ? AND user_id = ? AND type = 'final'", (route["id"], self.current_user["id"]))
                has_final = c.fetchone() is not None
                
                btn_frame = tk.Frame(top_frame); btn_frame.pack(side="right", padx=10)
                if not has_inicio: #botones para formularios
                    tk.Button(btn_frame, text="Realizar Formulario de Inicio", command=self._form_inicio, width=25, height=2).pack(pady=5)
                elif not has_final:
                    tk.Button(btn_frame, text="Realizar Formulario Final", command=self._form_fin, width=25, height=2, bg="#4CAF50", fg="white").pack(pady=5)
                else: #si ya completó ambos formularios
                    tk.Label(btn_frame, text="Ruta completada", font=("Arial", 12), fg="green").pack(pady=5)
            else: #si no hay ruta asignada
                tk.Label(info_frame, text="No hay rutas asignadas para hoy", font=("Arial", 12)).pack(anchor="w")
            
            # Direcciones y mapa
            content = tk.Frame(frm); content.pack(fill="both", expand=True, pady=10)
            left = tk.Frame(content); left.pack(side="left", fill="both", expand=True)
            right = tk.Frame(content, width=420); right.pack(side="right", fill="y")
            
            tk.Label(left, text="Direcciones de las paradas de hoy", font=("Arial",12,"bold")).pack(anchor="w")
            dir_list = tk.Listbox(left, height=10); dir_list.pack(fill="both", expand=True)
            
            if route: #llenar las direcciones
                c.execute("SELECT address FROM stops WHERE route_id = ? ORDER BY order_index", (route["id"],))
                for s in c.fetchall(): #agregar las paradas
                    dir_list.insert(tk.END, s["address"])
            
            map_path = os.path.join(ASSETS_DIR, "map_placeholder.png")
            if os.path.exists(map_path): #mapa
                mimg = Image.open(map_path).resize((400,300)); self._map_imgtk = ImageTk.PhotoImage(mimg); tk.Label(right, image=self._map_imgtk).pack()
            else:
                tk.Label(right, text="[mapa estático aquí]", width=50, height=15, bg="#ddd").pack()
    
    def _form_inicio(self):# abrir formulario de inicio
        from ui.conductor.window_form_inicio import FormInicioWindow
        FormInicioWindow(self.current_user["company_code"], self.current_user["id"], self.conn, self.win_inicio)
    
    def _form_fin(self): # abror formulario final
        from ui.conductor.window_form_fin import FormFinWindow
        FormFinWindow(self.current_user["company_code"], self.current_user["id"], self.conn, self.win_inicio)

    def _search_conductor(self): #buscar conductores
        q = self.search_var.get().strip()
        if not q: 
            messagebox.showinfo("Buscar", "Ingrese texto para buscar"); return
        c = self.conn.cursor()
        c.execute("SELECT id, name FROM users WHERE company_id = ? AND name LIKE ?", (self.current_user["company_id"], f"%{q}%"))
        rows = c.fetchall()
        if not rows:
            messagebox.showinfo("Resultado", "No se encontraron conductores"); return
        txt = "\n".join([f"{r['id']}: {r['name']}" for r in rows])
        messagebox.showinfo("Conductores encontrados", txt)

    # Importar módulos y ventanas
    def win_crear_rutas(self): #ventana "crear rutas"
        from ui.admin.window_crear_ruta import CrearRutaWindow
        CrearRutaWindow(self.current_user["company_code"], self.current_user["id"], self.conn)
    
    def win_crear_servicios(self):# ventana "crear servicios"
        from ui.admin.window_crear_servicios import CrearServiciosWindow
        CrearServiciosWindow(self.current_user["company_code"], self.conn)
    
    def win_crear_codigos(self):# ventana "crear códigos"
        from ui.admin.window_crear_codigos import CrearCodigosWindow
        CrearCodigosWindow(self.current_user["company_code"], self.current_user["id"], self.conn)
    
    def win_lista_usuarios(self):# ventana "lista de usuarios"
        from ui.admin.window_lista_usuarios import ListaUsuariosWindow
        ListaUsuariosWindow(self.current_user["company_code"], self.conn)
    
    def win_permisos(self): # ventana "permisos"
        from ui.admin.window_permisos import PermisosWindow
        PermisosWindow(self.current_user["company_code"], self.current_user["id"], self.conn)
    
    def win_reportar(self): # ventana "reportar problema"
        from ui.admin.window_reportar_problema import ReportarProblemaWindow
        ReportarProblemaWindow(self.current_user["company_code"], self.current_user["id"], self.conn)
    
    def win_documentos(self): # ventana "documentos"
        from ui.admin.window_documentos import DocumentosWindow
        DocumentosWindow(self.current_user["company_code"], self.conn)
    
    def win_cuentas_cobro(self): # ventana "cuentas de cobro"
        if self.current_user["is_admin"]:
            from ui.admin.window_cuentas_cobro import CuentasCobroWindow
            CuentasCobroWindow(self.current_user["company_code"], self.conn)
        else: # conductor
            from ui.conductor.window_cuentas_cobro_conductor import CuentasCobroConductorWindow
            CuentasCobroConductorWindow(self.current_user["company_code"], self.current_user["id"], self.conn)
    
    def win_horario(self): # ventana "horario" (para conductores)
        from ui.conductor.window_horario import HorarioConductorWindow
        HorarioConductorWindow(self.current_user["company_code"], self.current_user["id"], self.conn)

# para ejecutar la app
def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
