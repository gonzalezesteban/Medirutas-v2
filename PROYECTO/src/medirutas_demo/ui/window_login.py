import tkinter as tk
from tkinter import messagebox
from database import Database
from window_home_admin import HomeAdminWindow
from window_home_conductor import HomeConductorWindow
from window_register import RegisterWindow

class LoginWindow: # Ventana de inicio de sesión
    def __init__(self):
        self.db = Database()

        self.root = tk.Tk()
        self.root.title("Inicio de Sesión")
        self.root.geometry("400x350")

        tk.Label(self.root, text="Inicio de Sesión", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Código Empresa:").pack()
        self.entry_empresa = tk.Entry(self.root)
        self.entry_empresa.pack()

        tk.Label(self.root, text="Usuario:").pack()
        self.entry_usuario = tk.Entry(self.root)
        self.entry_usuario.pack()

        tk.Label(self.root, text="Contraseña:").pack()
        self.entry_contra = tk.Entry(self.root, show="*")
        self.entry_contra.pack()

        tk.Button(self.root, text="Ingresar", command=self.login).pack(pady=15)
        tk.Button(self.root, text="Registrar Empresa", command=self.open_register).pack()

        self.root.mainloop()

    def login(self): # Proceso inicio de sesión
        cod_empresa = self.entry_empresa.get()
        user = self.entry_usuario.get()
        pwd = self.entry_contra.get()

        valid, role = self.db.login_user(cod_empresa, user, pwd)

        if not valid:
            messagebox.showerror("Error", "Credenciales inválidas")
            return

        if role == "admin":
            self.root.destroy()
            HomeAdminWindow(cod_empresa)
        else:
            self.root.destroy()
            HomeConductorWindow(cod_empresa)

    def open_register(self):
        RegisterWindow()
