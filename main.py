import scraping_url
import scraping_json_detail  
import match_columns
import description_analysis
import os
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Configuration
    brand = input("Marque: ").strip().lower() or "breguet"
    
    # Limite de liens
    max_links_input = input("Nombre maximum de liens à scraper (laissez vide pour tout): ").strip()
    max_links = None
    if max_links_input:
        try:
            max_links = int(max_links_input)
        except ValueError:
            max_links = None
    
    # Récupérer la clé API depuis l'environnement ou demander à l'utilisateur
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = input("Clé API OpenAI: ").strip()
    
    # max_items = max_links
    max_items = max_links or 300
    
    # Exécution séquentielle
    links = scraping_url.scrape_brand_links(brand, max_links)
    scraping_url.save_links_to_excel(links)
    scraping_json_detail.main() 
    match_columns.align_breguet_daytona_data()
    description_analysis.process_watches(api_key, max_items=max_items)
    
    print("Terminé!")

if __name__ == "__main__":
    main()