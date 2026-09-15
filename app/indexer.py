import os
from unstructured.partition.auto import partition
from .nextcloud_client import NextcloudClient
from .models import Document, SessionLocal
from dotenv import load_dotenv

load_dotenv()


def index_files(folder_path="/"):
    """Index files from a Nextcloud folder into the database."""
    client = NextcloudClient()
    
    # List files in the specified folder
    response = client.list_files(folder_path)
    files = response.get("ocs", {}).get("data", [])

    db = SessionLocal()
    
    for file in files:
        if file.get("type") == "file":
            file_path = file.get("path")
            file_name = file.get("name")
            
            # Download the file
            content, content_type = client.download_file(file_path)
            
            # Extract text using unstructured
            try:
                elements = partition(content=content, content_type=content_type)
                text = "\n".join([str(el) for el in elements])
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")
                text = ""

            # Save to database
            doc = Document(
                name=file_name,
                path=file_path,
                content=text,
                content_type=content_type
            )
            db.add(doc)
    
    db.commit()
    db.close()
    print("Indexing completed successfully!")
