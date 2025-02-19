import ssl
from pymongo import MongoClient
from bson.binary import Binary
import logging
from datetime import datetime
from typing import Optional, Dict, Any

class MongoDBHandler:
    """Manejador de operaciones con MongoDB"""
    
    def __init__(self, uri: str, db_name: str, collection_name: str):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client: Optional[MongoClient] = None
        self.collection = None

    def connect(self) -> None:
        """Establece conexión con MongoDB"""
        try:
            self.client = MongoClient(self.uri, tls=True, tlsAllowInvalidCertificates=True)
            db = self.client[self.db_name]
            self.collection = db[self.collection_name]
            self.collection.find_one()  # Test de conexión
            logging.info("Conexión a MongoDB establecida")
        except Exception as e:
            self.collection = None
            logging.error(f"Error de conexión: {str(e)}")
            raise

    def disconnect(self) -> None:
        """Cierra la conexión con MongoDB"""
        if self.client:
            self.client.close()
            logging.info("Conexión a MongoDB cerrada")

    def insert_document(self, document: Dict[str, Any]) -> str:
        """Inserta un documento en la colección"""
        if self.collection is None:
            raise ConnectionError("No hay conexión a la base de datos")
        document_con_fechas = {**document, "fecha": datetime.utcnow()}
        
        result = self.collection.insert_one(document_con_fechas)
        logging.info(f"Documento insertado ID: {result.inserted_id}")
        return str(result.inserted_id)

    def get_all_documents(self) -> list:
        """Obtiene todos los documentos de la colección"""
        if self.collection is None:
            raise ConnectionError("No hay conexión a la base de datos")
        
        """Obtiene documentos con fecha convertida a zona horaria local"""
        
        pipeline = [
            {
                "$addFields": {
                    "fecha_local": {
                        "$dateToString": {
                            "format": "%Y-%m-%d %H:%M:%S",
                            "date": "$fecha",
                            "timezone": "America/Bogota"  # Cambiar por tu zona
                        }
                    }
                }
            }
        ]
        
        return list(self.collection.aggregate(pipeline))