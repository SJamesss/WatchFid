# WatchFid - Scraping et Analyse de Montres

## 📦 Code source

Le code source complet est disponible sur GitHub :  
[lien_vers_le_repo_GitHub](https://github.com/SJamesss/WatchFid)  
*(Remplace ce lien par l'URL réelle de ton dépôt)*

---

## 🚀 Fonctionnalités

- Scraping des URLs de montres par marque (Breguet, Rolex, etc.)
- Scraping des détails techniques pour chaque montre
- Matching/alignement des colonnes pour obtenir un fichier Excel final (`watches_details.xlsx`)
- Analyse automatique des descriptions via l'API OpenAI (GPT-4) sur le fichier aligné

---

## 🛠️ Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé sur votre machine (Windows, Mac, Linux)
- Une clé API OpenAI valide (pour l'analyse des descriptions)

---

## ⚡ Installation & Exécution

### 1. **Cloner le dépôt**

```bash
git clone https://github.com/SJamesss/WatchFid
cd WatchFid
```

### 2. **Configurer la clé API OpenAI (optionnel)**

Créez un fichier `.env` à partir du fichier `.env.example` à la racine du projet avec votre clé API :

```
OPENAI_API_KEY=votre_clé_api_openai
```

### 3. **Construire l'image Docker**

```bash
docker build -t watchfid .
```

### 4. **Lancer le pipeline complet**

```bash
# Windows
docker run -it -v .:/app watchfid

# Mac/Linux
docker run -it -v $(pwd):/app watchfid
```

Le programme vous demandera interactivement :
- La marque à scraper (ex: breguet)
- Le nombre maximum de liens à scraper
- Votre clé API OpenAI (si non configurée dans .env)

### 5. **Fichiers générés**

- `breguet_watch_links.xlsx` : liens des montres trouvées
- `breguet_json_details_temp.xlsx` : détails techniques bruts
- `watches_details.xlsx` : fichier final aligné (après matching et analyse)

---

## 🔑 **Clé API OpenAI**

- Obtenez une clé sur [platform.openai.com](https://platform.openai.com/api-keys)
- Elle est obligatoire pour l'étape d'analyse des descriptions.
- Vous pouvez soit :
  - La fournir directement quand le programme vous la demande
  - La configurer dans un fichier `.env` à la racine du projet

---

## 📂 **Organisation du projet**

- `main.py` : orchestrateur du pipeline
- `scraping_url.py` : scraping des URLs
- `scraping_json_detail.py` : scraping des détails
- `match_columns.py` : alignement des colonnes pour l'export Excel (génère `watches_details.xlsx`)
- `description_analysis.py` : analyse des descriptions (OpenAI) sur le fichier aligné
- Fichiers `.xlsx` : données d'entrée/sortie

---

## 💡 **Support & Conseils**

- **Données de sortie** : tous les fichiers Excel générés sont accessibles dans le dossier du projet (grâce au montage `-v %cd%:/app`).
- **Problème de clé API** : vérifiez que votre clé est bien active et dispose de crédits.
- **Besoin d'aide** : ouvrez une issue sur le dépôt GitHub.

---

## 📞 **Contact**

Pour toute question ou assistance technique :
- Email: contact@votreorganisation.com

---

*Projet réalisé par Sackdiphat Sounthala, Pierre Malychev, Gabriel Pelenga, Ulrielle Ngos*
