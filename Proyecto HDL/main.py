from dotenv import load_dotenv
import os
import logging
from database import MongoDBHandler
from email_sender import EmailSender
from GUI import FacturaGUI
import tkinter as tk

# Configuración inicial
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)

def main():
    # Configurar servicios
    db_handler = MongoDBHandler(
        uri=os.getenv("MONGO_URI"),
        db_name=os.getenv("DB_NAME", "facturas_db"),
        collection_name=os.getenv("COLLECTION_NAME", "facturas")
    )
    db_handler.connect()
    
    email_sender = EmailSender(
        smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        port=int(os.getenv("SMTP_PORT", "587")),
        email=os.getenv("EMAIL_USER"),
        password=os.getenv("EMAIL_PASSWORD")
    )

    # Iniciar aplicación
    root = tk.Tk()
    app = FacturaGUI(root, db_handler, email_sender)
    root.mainloop()

if __name__ == "__main__":
    main()