import os
import requests
from dotenv import load_dotenv

load_dotenv()


class NextcloudClient:
    """Client pour interagir avec l'API Nextcloud de Leviia Drive."""

    def __init__(self):
        self.base_url = os.getenv("NEXTCLOUD_URL")
        self.username = os.getenv("NEXTCLOUD_USERNAME")
        self.token = os.getenv("NEXTCLOUD_TOKEN")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "OCS-APIRequest": "true"
        })

    def list_files(self, path="/"):
        """
        Liste les fichiers dans un dossier Nextcloud.
        
        Args:
            path (str): Chemin du dossier (ex: "/Documents").
            
        Returns:
            dict: Réponse JSON de l'API Nextcloud.
        """
        url = f"{self.base_url}/ocs/v2.php/apps/files/api/v1/folders{path}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def download_file(self, file_path):
        """
        Télécharge un fichier depuis Nextcloud.
        
        Args:
            file_path (str): Chemin du fichier (ex: "/Documents/fichier.pdf").
            
        Returns:
            tuple: (contenu du fichier, type de contenu).
        """
        url = f"{self.base_url}/ocs/v2.php/apps/files/api/v1/files{file_path}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.content, response.headers.get("Content-Type", "application/octet-stream")
