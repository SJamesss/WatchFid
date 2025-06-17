#!/bin/bash

# Script de lancement simplifié pour WatchFid

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Vérifier si l'image Docker existe, sinon la construire
if ! docker image inspect watchfid &> /dev/null; then
    echo "Construction de l'image Docker..."
    docker build -t watchfid .
fi

# Paramètres par défaut
BRAND="breguet"
MAX_LINKS=""
API_KEY=""

# Afficher l'aide
show_help() {
    echo "Usage: ./run.sh -b <marque> -l <max_liens> -k <api_key> [-s <étape>]"
    echo ""
    echo "Options:"
    echo "  -b, --brand <marque>    Spécifie la marque à scraper (défaut: breguet)"
    echo "  -l, --links <nombre>    Limite le nombre de liens à scraper"
    echo "  -k, --key <clé>         Clé API OpenAI (obligatoire pour analyze et all)"
    echo "  -s, --step <étape>      Étape à exécuter: urls, details, match, analyze, all (défaut: all)"
    echo "  -h, --help              Affiche cette aide"
    echo ""
    echo "Exemples:"
    echo "  ./run.sh -b breguet -l 100 -k sk-xxxx            # Scrape 100 montres Breguet et fait l'analyse"
    echo "  ./run.sh -b rolex -l 50 -s urls                  # Récupère 50 URLs Rolex uniquement"
    echo "  ./run.sh -k sk-xxxx -s analyze                   # Analyse les descriptions uniquement"
    exit 0
}

# Charger les variables d'environnement si .env existe
if [ -f .env ]; then
    source .env
    # Si API_KEY est vide, utiliser celle du fichier .env
    if [ -z "$API_KEY" ]; then
        API_KEY="$OPENAI_API_KEY"
    fi
fi

# Traiter les arguments
STEP="all"
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--brand)
            BRAND="$2"
            shift 2
            ;;
        -l|--links)
            MAX_LINKS="$2"
            shift 2
            ;;
        -k|--key)
            API_KEY="$2"
            shift 2
            ;;
        -s|--step)
            STEP="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Option non reconnue: $1"
            show_help
            ;;
    esac
done

# Vérifier si la clé API est nécessaire et présente
if [ "$STEP" = "analyze" ] || [ "$STEP" = "all" ]; then
    if [ -z "$API_KEY" ]; then
        # Vérifier si la clé est dans .env
        if [ -f .env ] && grep -q "OPENAI_API_KEY=" .env && [ -n "$OPENAI_API_KEY" ]; then
            echo "Utilisation de la clé API OpenAI depuis le fichier .env"
            API_KEY="$OPENAI_API_KEY"
        else
            echo "ERREUR: Clé API OpenAI requise pour les étapes 'analyze' et 'all'"
            echo "Utilisez l'option -k ou --key pour spécifier votre clé API"
            echo "Ou ajoutez OPENAI_API_KEY=votre_clé dans un fichier .env"
            exit 1
        fi
    fi
fi

# Construire les arguments pour le script Python
ARGS="--brand $BRAND --step $STEP"

# Ajouter max_links si spécifié
if [ -n "$MAX_LINKS" ]; then
    ARGS="$ARGS --max_links $MAX_LINKS"
fi

# Ajouter api_key si spécifié
if [ -n "$API_KEY" ]; then
    ARGS="$ARGS --api_key $API_KEY"
fi

# Exécuter le container Docker
echo "Lancement du pipeline pour:"
echo "- Marque: $BRAND"
echo "- Étape: $STEP"
if [ -n "$MAX_LINKS" ]; then echo "- Max liens: $MAX_LINKS"; fi
if [ -n "$API_KEY" ]; then echo "- API Key: [Configurée]"; fi

if [ "$(uname)" = "Darwin" ] || [ "$(expr substr $(uname -s) 1 5)" = "Linux" ]; then
    # Mac ou Linux
    docker run -it --rm -v "$(pwd)":/app watchfid $ARGS
else
    # Windows
    docker run -it --rm -v "%cd%":/app watchfid $ARGS
fi