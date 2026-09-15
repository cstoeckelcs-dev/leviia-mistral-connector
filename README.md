# Leviia Mistral Connector

Un prototype de connecteur entre **Mistral AI** et **Leviia Drive** (basé sur Nextcloud) pour indexer et rechercher dans les documents stockés sur Leviia.

---

## 📌 Fonctionnalités
- **Connexion à Leviia Drive** via l'API Nextcloud.
- **Indexation des fichiers** (PDF, DOCX, TXT, etc.) dans une base de données SQLite.
- **Recherche dans les documents** via une API REST (FastAPI).
- **Intégration avec Mistral AI** pour permettre des recherches via des workflows.

---

## 🛠 Prérequis
- Python 3.10+
- Un compte **Leviia Drive** avec un **token d'accès personnel** (voir [cette section](#-configuration)).
- Les dépendances Python listées dans `requirements.txt`.

---

## 🚀 Installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/cstoeckelcs-dev/leviia-mistral-connector.git
   cd leviia-mistral-connector
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer l'environnement** :
   - Copiez `.env.example` en `.env` :
     ```bash
     cp .env.example .env
     ```
   - Éditez `.env` avec vos informations (voir [Configuration](#-configuration)).

4. **Initialiser la base de données** :
   - La base de données SQLite (`data/documents.db`) sera créée automatiquement lors de la première exécution.

---

## 🔧 Configuration

### 1. Générer un token Nextcloud
1. Connectez-vous à votre instance **Leviia Drive** (Nextcloud).
2. Allez dans **Paramètres → Sécurité → Tokens d'accès personnel**. 
3. Créez un nouveau token avec les permissions suivantes :
   - `Lire les fichiers`
   - `Lister les fichiers`
4. Copiez le token généré et ajoutez-le dans `.env` :
   ```env
   NEXTCLOUD_TOKEN=votre_token_nextcloud
   ```

### 2. Configurer `.env`
Exemple de fichier `.env` :
```env
NEXTCLOUD_URL=https://votre-domaine.leviia.fr
NEXTCLOUD_USERNAME=votre_utilisateur
NEXTCLOUD_TOKEN=votre_token_nextcloud
INDEX_FOLDER=/Documents  # Dossier à indexer sur Leviia Drive
```

---

## 🏃‍♂️ Utilisation

### 1. Indexer les fichiers
Pour indexer les fichiers depuis Leviia Drive dans la base de données locale :
```bash
python -m app.indexer
```

### 2. Démarrer l'API FastAPI
Pour lancer l'API de recherche :
```bash
uvicorn app.main:app --reload
```
L'API sera accessible à l'adresse : `http://localhost:8000`.

---

## 🔍 Endpoints API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST`  | `/index`  | Indexe les fichiers depuis Leviia Drive. |
| `POST`  | `/search` | Recherche dans les fichiers indexés. |

### Exemple de requête pour `/search`
```bash
curl -X POST "http://localhost:8000/search" \
-H "Content-Type: application/json" \
-d '{"query": "votre_recherche"}'
```

---

## 🤖 Intégration avec Mistral AI

1. **Déployer l'API** :
   - Déployez l'API FastAPI sur un serveur accessible (ex: avec `uvicorn` + `nginx` ou un service comme Render/Heroku).
   - Notez l'URL de votre API (ex: `https://votre-serveur.com`).

2. **Créer un connecteur Mistral AI** :
   - Dans l'interface Mistral AI, allez dans **Connecteurs** et ajoutez un nouveau connecteur.
   - Configurez-le pour pointer vers votre API (ex: `https://votre-serveur.com/search`).
   - Ajoutez les identifiants nécessaires (token Nextcloud) dans la configuration du connecteur.

3. **Tester avec un workflow** :
   - Utilisez un workflow Mistral AI pour appeler votre connecteur et rechercher des documents.

---

## 📂 Structure du projet
```
leviia-mistral-connector/
│
├── app/
│   ├── __init__.py
│   ├── main.py               # API FastAPI
│   ├── nextcloud_client.py  # Client Nextcloud
│   ├── indexer.py            # Script d'indexation
│   └── models.py             # Modèles de données
│
├── data/
│   └── documents.db          # Base de données SQLite
│
├── requirements.txt          # Dépendances Python
├── .env.example              # Exemple de configuration
└── README.md                 # Documentation
```

---

## 🛠 Dépendances
- `fastapi` : Framework pour l'API REST.
- `uvicorn` : Serveur ASGI pour FastAPI.
- `requests` : Requêtes HTTP vers Nextcloud.
- `unstructured` : Extraction de texte depuis des fichiers (PDF, DOCX, etc.).
- `sqlalchemy` : ORM pour la base de données.
- `python-dotenv` : Gestion des variables d'environnement.

---

## 📜 Licence
Ce projet est sous licence **MIT**. Voir [LICENSE](LICENSE) pour plus de détails.
