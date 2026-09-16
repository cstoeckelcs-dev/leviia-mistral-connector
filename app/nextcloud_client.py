import os
import logging
import xml.etree.ElementTree as ET
from urllib.parse import quote, unquote

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Espaces de noms WebDAV / Nextcloud utilisés dans les réponses PROPFIND.
NS = {
    "d": "DAV:",
    "oc": "http://owncloud.org/ns",
    "nc": "http://nextcloud.org/ns",
}

# Corps de la requête PROPFIND : propriétés demandées pour chaque entrée.
PROPFIND_BODY = """<?xml version="1.0" encoding="UTF-8"?>
<d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns">
  <d:prop>
    <d:displayname/>
    <d:resourcetype/>
    <d:getcontenttype/>
    <d:getcontentlength/>
    <d:getlastmodified/>
  </d:prop>
</d:propfind>
"""


class NextcloudClient:
    """Client pour interagir avec l'API WebDAV de Leviia Drive (Nextcloud)."""

    def __init__(self):
        self.base_url = (os.getenv("NEXTCLOUD_URL") or "").rstrip("/")
        self.username = os.getenv("NEXTCLOUD_USERNAME")
        self.token = os.getenv("NEXTCLOUD_TOKEN")
        self.session = requests.Session()
        self.session.auth = (self.username, self.token)
        # Endpoint WebDAV indiqué dans les paramètres de fichiers de Leviia Drive.
        self.webdav_prefix = f"/remote.php/dav/files/{self.username}"
        self.webdav_root = f"{self.base_url}{self.webdav_prefix}"

    def _webdav_url(self, path):
        """Construit l'URL WebDAV normalisée pour un chemin donné."""
        if not path:
            path = "/"
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.webdav_root}{quote(path)}"

    def _relative_path(self, href):
        """Convertit un href WebDAV en chemin relatif (ex: /Tickets/fichier.pdf)."""
        rel = unquote(href)
        idx = rel.find(self.webdav_prefix)
        if idx != -1:
            rel = rel[idx + len(self.webdav_prefix):]
        if not rel.startswith("/"):
            rel = "/" + rel
        return rel.rstrip("/") or "/"

    @staticmethod
    def _raise_with_body(response, url):
        """Journalise le corps de la réponse avant de lever une HTTPError."""
        if response.status_code >= 400:
            body = response.text
            logger.error("HTTP %s pour %s\nCorps de la réponse:\n%s", response.status_code, url, body)
        response.raise_for_status()

    def list_files(self, path="/"):
        """
        Liste les fichiers et dossiers dans un dossier Nextcloud via WebDAV (PROPFIND).

        Args:
            path (str): Chemin du dossier (ex: "/Tickets").

        Returns:
            list[dict]: Une entrée par élément trouvé, sous la forme :
                {"name", "path", "is_dir", "content_type", "size"}
        """
        url = self._webdav_url(path)
        # Conforme à la doc officielle Leviia : PROPFIND sans corps (data=None),
        # Depth: 1 pour ne lister que le niveau immédiat.
        headers = {"Depth": "1"}
        response = self.session.request("PROPFIND", url, headers=headers, data=None)
        self._raise_with_body(response, url)

        root = ET.fromstring(response.content)
        requested_path = self._relative_path(f"{self.webdav_prefix}{quote(path or '/')}")
        results = []

        for resp in root.findall("d:response", NS):
            href_el = resp.find("d:href", NS)
            if href_el is None or not href_el.text:
                continue
            rel_path = self._relative_path(href_el.text)

            # Sauter l'entrée correspondant au dossier interrogé lui-même.
            if rel_path.rstrip("/") == requested_path.rstrip("/"):
                continue

            prop = resp.find("d:propstat/d:prop", NS)
            is_dir = False
            content_type = None
            size = None
            if prop is not None:
                resourcetype = prop.find("d:resourcetype", NS)
                is_dir = resourcetype is not None and resourcetype.find("d:collection", NS) is not None
                ct_el = prop.find("d:getcontenttype", NS)
                if ct_el is not None and ct_el.text:
                    content_type = ct_el.text
                size_el = prop.find("d:getcontentlength", NS)
                if size_el is not None and size_el.text:
                    try:
                        size = int(size_el.text)
                    except ValueError:
                        size = None

            name = os.path.basename(rel_path.rstrip("/"))
            results.append({
                "name": name,
                "path": rel_path,
                "is_dir": is_dir,
                "content_type": content_type,
                "size": size,
            })

        return results

    def download_file(self, file_path):
        """
        Télécharge un fichier depuis Nextcloud via WebDAV (GET).

        Args:
            file_path (str): Chemin relatif du fichier (ex: "/Tickets/fichier.pdf").

        Returns:
            tuple: (contenu binaire du fichier, type de contenu).
        """
        url = self._webdav_url(file_path)
        response = self.session.get(url)
        self._raise_with_body(response, url)
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        return response.content, content_type
