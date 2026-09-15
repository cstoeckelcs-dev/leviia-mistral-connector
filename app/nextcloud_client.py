import os
import requests
from dotenv import load_dotenv

load_dotenv()


class NextcloudClient:
    """Client for interacting with Leviia Drive (Nextcloud) API."""

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
        """List files in a Nextcloud folder."""
        url = f"{self.base_url}/ocs/v2.php/apps/files/api/v1/folders{path}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def download_file(self, file_path):
        """Download a file from Nextcloud."""
        url = f"{self.base_url}/ocs/v2.php/apps/files/api/v1/files{file_path}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.content, response.headers.get("Content-Type", "application/octet-stream")

    def get_file_metadata(self, file_path):
        """Get metadata for a specific file."""
        url = f"{self.base_url}/ocs/v2.php/apps/files/api/v1/files{file_path}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
