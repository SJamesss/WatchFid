import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import argparse

def scrape_brand_links(brand_name, max_links=None):
    base_url = "https://everywatch.com"
    all_watch_links = []
    page_number = 1
    
    while True:
        # Vérifier si on a atteint la limite
        if max_links and len(all_watch_links) >= max_links:
            print(f"Limite de {max_links} liens atteinte, arrêt du scraping.")
            break
            
        url = f"https://everywatch.com/{brand_name}/?pageNumber={page_number}"
        print(f"Récupération des liens de la page {page_number} pour la marque {brand_name}...")
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                watch_cards = soup.find_all('a', class_='ew-grid-item ew-grid-watch-card')
                
                if not watch_cards:
                    print("Plus de montres trouvées, arrêt du scraping.")
                    break
                
                for link in watch_cards:
                    # Vérifier la limite à chaque lien ajouté
                    if max_links and len(all_watch_links) >= max_links:
                        break
                        
                    if 'href' in link.attrs:
                        href = link['href']
                        full_link = base_url + href
                        all_watch_links.append(full_link)
                
                time.sleep(1)
            else:
                print(f"Erreur lors de l'accès à la page {page_number}: Code {response.status_code}")
                break
        except Exception as e:
            print(f"Erreur lors du traitement de la page {page_number}: {str(e)}")
            break
        
        page_number += 1
    
    print(f"Nombre total de liens récupérés pour {brand_name}: {len(all_watch_links)}")
    return all_watch_links

def save_links_to_excel(new_links, excel_file='breguet_watch_links.xlsx'):
    existing_links = set()
    if os.path.exists(excel_file):
        df_existing = pd.read_excel(excel_file)
        if 'URL' in df_existing.columns:
            existing_links = set(df_existing['URL'].tolist())
    
    # Filtrer les nouveaux liens
    filtered_links = [url for url in new_links if url not in existing_links]
    all_urls = list(existing_links) + filtered_links
    df = pd.DataFrame({'URL': all_urls})
    df = df.drop_duplicates(subset=['URL'])
    df.to_excel(excel_file, index=False)
    
    print(f"Nouveaux liens ajoutés: {len(filtered_links)}")
    print(f"Total de liens dans le fichier: {len(df)}")
    print(f"Les liens ont été enregistrés dans le fichier '{excel_file}'")


"""
if __name__ == '__main__':
    brand = input("Marque : ").strip().lower()
    
    # Demander le nombre maximum de liens à scraper
    max_links_input = input("Nombre maximum de liens à scraper (laissez vide pour tout scraper) : ").strip()
    
    max_links = None
    if max_links_input:
        try:
            max_links = int(max_links_input)
            print(f"Limitation à {max_links} liens maximum")
        except ValueError:
            print("Nombre invalide, scraping sans limite")
    else:
        print("Scraping sans limite")
    
    links = scrape_brand_links(brand, max_links)
    save_links_to_excel(links)
"""