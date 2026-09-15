import os
import logging
from unstructured.partition.auto import partition
from .nextcloud_client import NextcloudClient
from .models import Document, SessionLocal
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


def index_files(folder_path="/"):
    """
    Indexe les fichiers d'un dossier Nextcloud dans la base de données SQLite.
    
    Args:
        folder_path (str): Chemin du dossier à indexer (ex: "/Documents").
    """
    client = NextcloudClient()
    db = None
    
    try:
        # Lister les fichiers dans le dossier
        files_response = client.list_files(folder_path)
        files = files_response.get("ocs", {}).get("data", [])
        
        db = SessionLocal()
        
        for file in files:
            if file.get("type") == "file":
                file_path = file.get("path")
                file_name = file.get("name")
                
                logger.info(f"Traitement du fichier : {file_name}")
                
                try:
                    # Télécharger le fichier
                    content, content_type = client.download_file(file_path)
                    
                    # Extraire le texte avec unstructured
                    elements = partition(content=content, content_type=content_type)
                    text = "\n".join([str(el) for el in elements])
                    
                    # Sauvegarder dans la base de données
                    doc = Document(
                        name=file_name,
                        path=file_path,
                        content=text,
                        content_type=content_type
                    )
                    db.add(doc)
                    logger.info(f"Fichier indexé : {file_name}")
                    
                except Exception as e:
                    logger.error(f"Erreur lors du traitement de {file_name}: {e}")
        
        db.commit()
        logger.info("Indexation terminée avec succès.")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'indexation : {e}")
        raise
    
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    folder = os.getenv("INDEX_FOLDER", "/")
    index_files(folder)
