from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .models import Document, SessionLocal
from .indexer import index_files
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Leviia Mistral Connector API",
    description="API pour rechercher dans les documents indexés depuis Leviia Drive.",
    version="0.1.0"
)


class SearchRequest(BaseModel):
    query: str


@app.post("/index", tags=["Indexation"])
def index():
    """
    Indexe les fichiers depuis Leviia Drive dans la base de données.
    
    Returns:
        dict: Message de confirmation.
    """
    try:
        folder = os.getenv("INDEX_FOLDER", "/")
        index_files(folder)
        return {"message": "Indexation terminée avec succès."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'indexation : {e}")


@app.post("/search", tags=["Recherche"])
def search(request: SearchRequest):
    """
    Recherche dans les fichiers indexés.
    
    Args:
        request (SearchRequest): Requête de recherche avec le champ `query`.
        
    Returns:
        dict: Liste des documents correspondant à la recherche.
    """
    db = SessionLocal()
    try:
        results = db.query(Document).filter(Document.content.contains(request.query)).all()
        return {
            "results": [
                {"name": doc.name, "path": doc.path, "content_type": doc.content_type}
                for doc in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche : {e}")
    finally:
        db.close()


@app.get("/", tags=["Health"])
def read_root():
    """Endpoint de santé pour vérifier que l'API est en cours d'exécution."""
    return {"message": "Leviia Mistral Connector API est en ligne !"}
