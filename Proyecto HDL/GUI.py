from PIL import Image, ImageTk
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from bson import Binary
import ttkbootstrap as ttkbs
from ttkbootstrap.constants import *
import threading
import time
import re
import os
from typing import Optional


class FacturaGUI:
    # Se utiliza el tema "flatly" para lograr un look moderno y minimalista
    THEME = "flatly"
    FONT_PRIMARY = ("Segoe UI", 11)
    FONT_SECONDARY = ("Segoe UI", 10)
    ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}
    EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    
    def __init__(self, root, db_handler, email_sender):
        self.root = root
        self.db_handler = db_handler
        self.email_sender = email_sender
        self.current_file: Optional[str] = None
        
        self._configure_window()
        self._create_widgets()
        self._bind_events()
        
    def _configure_window(self):
        self.root.title("Facturas de Transporte")
        self.root.geometry("800x650")
        
        # VerifiNcar existencia de recursos
        self._verify_resources()        
        self.style = ttkbs.Style(theme=self.THEME)

        # Ajustamos estilos globales para Label, Frame y Button
        self.style.configure("TLabel", padding=5)
        self.style.configure("TFrame", padding=10)
        self.style.configure("TButton", padding=5)
        self.root.minsize(780, 600)

    def _verify_resources(self):
        resources = [
            os.path.join("C:\\Users\\Sergio Moscoso\\OneDrive\\Escritorio\\Proyecto\\image","DHL.PNG")
        ]
        
        for resource in resources:
            if not os.path.exists(resource):
                messagebox.showerror("Error crítico", f"Recurso faltante: {resource}")
                self.root.destroy()
                exit(1)

    def _create_widgets(self):
        # Encabezado principal (aquí se podría incluir un logotipo)
        header_frame = ttkbs.Frame(self.root)
        header_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Carga del logo DHL
        try:
            image_path = os.path.join(os.path.dirname(__file__), "C:\\Users\\Sergio Moscoso\\OneDrive\\Escritorio\\Proyecto\\image","DHL.PNG")
            self.dhl_logo = Image.open(image_path)
            self.dhl_logo = self.dhl_logo.resize((120, 40), Image.LANCZOS)  # Ajuste profesional del tamaño
            self.dhl_photo = ImageTk.PhotoImage(self.dhl_logo)
            
            logo_label = ttkbs.Label(
                header_frame, 
                image=self.dhl_photo,
                bootstyle=(LIGHT,),
                padding=(10, 5)
            )
            logo_label.image = self.dhl_photo  # Mantener referencia
            logo_label.pack(side=tk.LEFT, padx=(20, 10))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el logo: {str(e)}")
            self.dhl_photo = None

        # Título de la aplicación con mejor alineación
        header_label = ttkbs.Label(
            header_frame, 
            text="Facturas de Transporte", 
            font=("Segoe UI", 24, "bold"),
            bootstyle=(INFO, INVERSE),
            anchor=tk.CENTER
        )
        header_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 20))
        self.main_frame = ttkbs.Frame(self.root, padding=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_file_section()
        self._create_data_section()
        self._create_progress_bar()
        self._create_action_buttons()
        self._create_status_bar()
        
    def _create_file_section(self):
        file_frame = ttkbs.Labelframe(
            self.main_frame, 
            text="Gestión de Archivos",
            bootstyle=PRIMARY
        )
        file_frame.pack(fill=tk.X, pady=8)
        
        self.btn_browse = ttkbs.Button(
            file_frame, 
            text="📁 Examinar", 
            command=self._select_file,
            bootstyle=(OUTLINE, PRIMARY),
            width=15
        )
        self.btn_browse.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.lbl_file = ttkbs.Label(
            file_frame, 
            text="Seleccione un archivo",
            bootstyle=(INVERSE, PRIMARY),
            width=45,
            anchor=tk.W
        )
        self.lbl_file.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        
    def _create_data_section(self):
        data_frame = ttkbs.Labelframe(
            self.main_frame, 
            text="Información de Documento",
            bootstyle=PRIMARY
        )
        data_frame.pack(fill=tk.X, pady=10)
        
        # Email
        ttkbs.Label(data_frame, text="✉️ Correo electrónico:").grid(row=0, column=0, padx=8, pady=8, sticky=tk.W)
        self.entry_email = ttkbs.Entry(data_frame, width=40)
        self.entry_email.grid(row=0, column=1, padx=8, pady=8, sticky=tk.EW)
        
        # Estado
        ttkbs.Label(data_frame, text="📊 Estado:").grid(row=1, column=0, padx=8, pady=8, sticky=tk.W)
        self.cmb_status = ttkbs.Combobox(
            data_frame, 
            values=["Válida", "Inválida", "Pendiente"], 
            state=READONLY,
            width=15
        )
        self.cmb_status.current(2)
        self.cmb_status.grid(row=1, column=1, padx=8, pady=8, sticky=tk.W)
        
        # Observaciones
        ttkbs.Label(data_frame, text="📝 Observaciones:").grid(row=2, column=0, padx=8, pady=8, sticky=tk.W)
        self.entry_obs = ttkbs.Entry(data_frame, width=40, state=DISABLED)
        self.entry_obs.grid(row=2, column=1, padx=8, pady=8, sticky=tk.EW)
        
        data_frame.columnconfigure(1, weight=1)
        
    def _create_progress_bar(self):
        self.progress = ttkbs.Progressbar(
            self.main_frame, 
            orient=HORIZONTAL, 
            mode=DETERMINATE,
            bootstyle=(SUCCESS, STRIPED)
        )
        self.progress.pack(fill=tk.X, pady=15)
        
    def _create_action_buttons(self):
        btn_frame = ttkbs.Frame(self.main_frame)
        btn_frame.pack(pady=10)
        
        self.btn_view = ttkbs.Button(
            btn_frame,
            text="📂 Ver Documentos",
            command=self._show_files,
            bootstyle=(OUTLINE, INFO),
            width=15
        )
        self.btn_view.pack(side=tk.LEFT, padx=10)
        
        self.btn_save = ttkbs.Button(
            btn_frame,
            text="💾 Guardar",
            command=self._start_save_process,
            bootstyle=SUCCESS,
            width=15
        )
        self.btn_save.pack(side=tk.LEFT, padx=10)
        
    def _create_status_bar(self):
        self.status_bar = ttkbs.Label(
            self.root, 
            text="🟢 Sistema listo", 
            bootstyle=(INVERSE, DARK),
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def _bind_events(self):
        self.cmb_status.bind("<<ComboboxSelected>>", self._update_observations)
        
    def _update_status(self, message: str, alert: str = "info"):
        status_config = {
            "info": ("🚚", DARK),
            "success": ("✅", SUCCESS),
            "warning": ("⚠️", WARNING),
            "error": ("🔴", DANGER)
        }
        icon, style = status_config.get(alert, ("🟢", DARK))
        self.status_bar.config(text=f"{icon} {message}", bootstyle=(INVERSE, style))
        
    def _select_file(self):
        filetypes = (("Documentos", "*.pdf"), ("Imágenes", "*.png *.jpg *.jpeg"))
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            try:
                self._validate_file(filename)
                self.current_file = filename
                self.lbl_file.config(text=os.path.basename(filename))
                self._animate_progress(0, 100, 10, 0.1)
                self._update_status("Archivo listo para subir", "success")
            except Exception as e:
                self._update_status(str(e), "error")
                messagebox.showerror("Error", str(e))
    
    def _validate_file(self, file_path: str):
        if not os.path.isfile(file_path):
            raise ValueError("La ruta especificada no es un archivo válido")
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError("Tipo de archivo no permitido")
        
        if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10MB
            raise ValueError("El archivo excede el tamaño máximo permitido (10MB)")
    
    def _animate_progress(self, start: int, end: int, step: int, delay: float):
        self.progress["value"] = start
        for i in range(start, end + step, step):
            self.progress["value"] = min(i, 100)
            self.root.update()
            time.sleep(delay)
        self.progress["value"] = 0
    
    def _update_observations(self, event=None):
        if self.cmb_status.get() == "Inválida":
            self.entry_obs.config(state=NORMAL)
            self.entry_obs.focus()
        else:
            self.entry_obs.delete(0, tk.END)
            self.entry_obs.config(state=DISABLED)
    
    def _validate_inputs(self):
        if not self.current_file:
            raise ValueError("Debe seleccionar un archivo primero")
        
        email = self.entry_email.get()
        if not re.fullmatch(self.EMAIL_REGEX, email):
            raise ValueError("Formato de email inválido")
        
        if self.cmb_status.get() == "Inválida" and not self.entry_obs.get():
            raise ValueError("Debe ingresar observaciones para el Documento inválidas")
    
    def _start_save_process(self):
        try:
            self._validate_inputs()
            threading.Thread(target=self._save_document, daemon=True).start()
        except Exception as e:
            self._update_status(str(e), "error")
            messagebox.showerror("Error de validación", str(e))
    
    def _save_document(self):
        try:
            self._update_status("Iniciando proceso de guardado...", "info")
            self._animate_progress(0, 100, 20, 0.2)
            
            with open(self.current_file, 'rb') as f:
                file_data = f.read()
            
            estado = self.cmb_status.get()
            observaciones = "Ninguna" if estado == "Válida" else self.entry_obs.get()
            
            document = {
                "nombre_archivo": os.path.basename(self.current_file),
                "archivo": Binary(file_data),
                "email": self.entry_email.get(),
                "estado": estado,
                "observaciones": observaciones,
                "fecha_subida": datetime.now()
            }
            
            doc_id = self.db_handler.insert_document(document)
            self._send_email_notification()
            
            self.root.after(0, self._show_success, doc_id)
        except Exception as e:
            self.root.after(0, self._update_status, f"Error: {str(e)}", "error")
            self.root.after(0, messagebox.showerror, "Error crítico", str(e))
    
    def _send_email_notification(self):
        email = self.entry_email.get()
        estado = self.cmb_status.get()
        observaciones = self.entry_obs.get() if estado == "Inválida" else "Ninguna"
        file_name = os.path.basename(self.current_file)
        
        subject = f"Actualización de Estado de su Factura: {file_name}"
        body = f"""
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body {{
              margin: 0;
              padding: 0;
              background-color: #ffffff;
              font-family: 'Segoe UI', sans-serif;
            }}
            .container {{
              width: 600px;
              margin: 0 auto;
              border: 1px solid #eaeaea;
              border-radius: 8px;
              overflow: hidden;
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
            .header {{
              background-color: #007BFF;
              padding: 30px;
              text-align: center;
            }}
            .header h1 {{
              color: #ffffff;
              margin: 0;
              font-size: 26px;
            }}
            .content {{
              padding: 30px;
              color: #333333;
              font-size: 16px;
              line-height: 1.6;
            }}
            .content h2 {{
              font-size: 20px;
              margin-bottom: 20px;
            }}
            .card {{
              border: 1px solid #eaeaea;
              border-radius: 6px;
              padding: 20px;
              margin-bottom: 20px;
            }}
            .card table {{
              width: 100%;
            }}
            .card td {{
              padding: 5px 0;
            }}
            .card .label {{
              font-weight: bold;
              width: 35%;
            }}
            .footer {{
              background-color: #f8f9fa;
              padding: 20px;
              text-align: center;
              font-size: 14px;
              color: #777777;
            }}
            .footer a {{
              color: #007BFF;
              text-decoration: none;
            }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>Facturación de Transportes</h1>
            </div>
            <div class="content">
              <h2>Estimado/a Cliente,</h2>
              <p>Le informamos el estado actualizado de su factura <strong>{file_name}</strong>.</p>
              <div class="card">
                <table>
                  <tr>
                    <td class="label">Estado:</td>
                    <td>{estado}</td>
                  </tr>
                  <tr>
                    <td class="label">Observaciones:</td>
                    <td>{observaciones}</td>
                  </tr>
                  <tr>
                    <td class="label">Fecha de Registro:</td>
                    <td>{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</td>
                  </tr>
                </table>
              </div>
              <p>Adjuntamos el documento correspondiente para su referencia. Si tiene alguna duda o requiere asistencia, por favor contáctenos.</p>
              <p>Atentamente,<br><strong>Equipo de Facturación</strong></p>
            </div>
            <div class="footer">
              &copy; Facturación 2025. Todos los derechos reservados.<br>
              <a href="https://www.dhl.com/co-es/home.html">Visite nuestro sitio</a>
            </div>
          </div>
        </body>
        </html>
        """
    
        self.email_sender.send_email(
            to=email,
            subject=subject,
            body=body,
            file_path=self.current_file,
            is_html=True  # Asegúrate de que el método de envío soporte HTML
        )
        
    def _show_success(self, doc_id: str):
        messagebox.showinfo("Éxito", f"Documento guardado con ID: {doc_id}")
        self._reset_ui()
        self._update_status("Operación completada exitosamente", "success")
        
    def _reset_ui(self):
        self.lbl_file.config(text="Seleccione un archivo")
        self.entry_email.delete(0, tk.END)
        self.cmb_status.current(2)
        self.entry_obs.delete(0, tk.END)
        self.entry_obs.config(state=DISABLED)
        self.current_file = None
        
    def _show_files(self):
        try:
            # Crear ventana modal para mostrar los archivos
            window = ttkbs.Toplevel(self.root)
            window.title("Documentos Almacenados - DHL")
            window.geometry("1024x600")
            
            # Header con logo DHL
            header_frame = ttkbs.Frame(window)
            header_frame.pack(fill=tk.X, pady=(10, 5))
            
            # Logo DHL
            logo_label = ttkbs.Label(
                header_frame, 
                image=self.dhl_photo,
                bootstyle=(LIGHT,),
                padding=(10, 5)
            )
            logo_label.image = self.dhl_photo
            logo_label.pack(side=tk.LEFT, padx=(20, 10))
            
            # Título con estilo DHL
            title_label = ttkbs.Label(
                header_frame,
                text="Documentos Almacenados",
                font=("Segoe UI", 18, "bold"),
                bootstyle=(INVERSE, SECONDARY),
                anchor=tk.CENTER
            )
            title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))

            # Barra de búsqueda y refresco
            search_frame = ttkbs.Frame(window, padding=10)
            search_frame.pack(fill=tk.X)
            search_label = ttkbs.Label(search_frame, text="Buscar:", font=self.FONT_PRIMARY)
            search_label.pack(side=tk.LEFT, padx=(0, 5))
            search_var = tk.StringVar()
            search_entry = ttkbs.Entry(search_frame, textvariable=search_var, width=30)
            search_entry.pack(side=tk.LEFT, padx=(0, 10))

            refresh_btn = ttkbs.Button(
                search_frame,
                text="Refrescar",
                bootstyle=INFO,
                command=lambda: self._refresh_files(tree, search_var)
            )
            refresh_btn.pack(side=tk.LEFT)

            # Marco para el Treeview
            tree_frame = ttkbs.Frame(window, padding=10)
            tree_frame.pack(fill=tk.BOTH, expand=True)

            # Definir columnas del Treeview
            columns = ("nombre", "estado", "observaciones", "fecha", "accion")
            tree = ttkbs.Treeview(
                tree_frame,
                columns=columns,
                show="headings",
                bootstyle=INFO,
                selectmode="browse"
            )

            # Configurar encabezados y columnas con mejor espaciado
            tree.heading("nombre", text="Nombre del Archivo", anchor=tk.W)
            tree.heading("estado", text="Estado", anchor=tk.CENTER)
            tree.heading("observaciones", text="Observaciones", anchor=tk.W)
            tree.heading("fecha", text="Fecha de Subida", anchor=tk.CENTER)
            tree.heading("accion", text="Acciones", anchor=tk.CENTER)

            # Ajustes de ancho y stretching
            tree.column("nombre", width=320, anchor=tk.W, stretch=True)
            tree.column("estado", width=120, anchor=tk.CENTER, stretch=False)
            tree.column("observaciones", width=280, anchor=tk.W, stretch=True)
            tree.column("fecha", width=160, anchor=tk.CENTER, stretch=False)
            tree.column("accion", width=100, anchor=tk.CENTER, stretch=False)

            # Mejorar el estilo de las filas
            style = ttkbs.Style()
            style.configure("Treeview", rowheight=30, font=('Segoe UI', 10))
            style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))

            
            # Scrollbar vertical para la tabla
            scroll = ttkbs.Scrollbar(
                tree_frame,
                orient=tk.VERTICAL,
                command=tree.yview,
                bootstyle=ROUND
            )
            tree.configure(yscrollcommand=scroll.set)
            scroll.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Cargar documentos en el Treeview con filtro (si existe texto en búsqueda)
            self._populate_files(tree, search_var.get())

            # Evento de doble clic para descargar
            tree.bind("<Double-1>", lambda e: self._download_selected_file(tree))
            # Menú contextual para acciones rápidas (clic derecho)
            tree.bind("<Button-3>", lambda e: self._show_tree_context_menu(e, tree))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los archivos: {str(e)}")
    
    def _populate_files(self, tree, search_text=""):
        """Carga o recarga la información de los documentos en el Treeview,
        aplicando un filtro si se especifica un término de búsqueda."""
        # Configurar colores DHL
        style = ttkbs.Style()
        style.configure("Treeview",
            background=self.style.colors.light,
            fieldbackground=self.style.colors.light,
            foreground=self.style.colors.dark,
            rowheight=30
        )
        style.configure("Treeview.Heading",
            font=('Segoe UI', 10, 'bold'),
            background=self.style.colors.primary,
            foreground=self.style.colors.light
        )
        style.map("Treeview.Heading",
            background=[('active', self.style.colors.secondary)]
        )
        # Limpiar el Treeview
        for item in tree.get_children():
            tree.delete(item)
        docs = self.db_handler.get_all_documents()
        # Aplicar filtro en el nombre del archivo si se ingresó un término
        if search_text:
            docs = [doc for doc in docs if search_text.lower() in doc['nombre_archivo'].lower()]
        for doc in docs:
            tree.insert("", tk.END, values=(
                doc['nombre_archivo'],
                doc['estado'],
                doc.get('observaciones', 'N/A'),
                doc.get('fecha_local', 'N/A'),
                "⬇️ Descargar"
            ))
    
    def _refresh_files(self, tree, search_var):
        """Actualiza la lista de documentos utilizando el valor actual del campo de búsqueda."""
        self._populate_files(tree, search_var.get())
    
    def _show_tree_context_menu(self, event, tree):
        """Muestra un menú contextual para acciones rápidas sobre el Treeview."""
        menu = tk.Menu(tree, tearoff=0)
        menu.add_command(label="Descargar", command=lambda: self._download_selected_file(tree))
        menu.add_command(label="Refrescar", command=lambda: self._refresh_files(tree, tk.StringVar()))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _download_selected_file(self, tree):
        selected_item = tree.focus()
        if selected_item:
            item_data = tree.item(selected_item)
            doc_name = item_data['values'][0]
            docs = self.db_handler.get_all_documents()
            document = next((doc for doc in docs if doc['nombre_archivo'] == doc_name), None)
            if document:
                self._download_file(document)
    
    def _download_file(self, document):
        try:
            initial_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            file_path = filedialog.asksaveasfilename(
                initialdir=initial_dir,
                initialfile=document['nombre_archivo'],
                title="Guardar Archivo Como",
                defaultextension=os.path.splitext(document['nombre_archivo'])[1]
            )
            
            if file_path:
                with open(file_path, "wb") as f:
                    f.write(document['archivo'])
                self._update_status(f"Archivo guardado en: {file_path}", "success")
                messagebox.showinfo("Éxito", "Descarga completada exitosamente")
        except Exception as e:
            self._update_status(f"Error en descarga: {str(e)}", "error")
            messagebox.showerror("Error", f"No se pudo descargar el archivo: {str(e)}")
    
    def on_close(self):
        self.db_handler.disconnect()
        self.root.destroy()