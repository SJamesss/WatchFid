import requests
import pandas as pd
import time
import random
import re
from datetime import datetime
from fake_useragent import UserAgent
import os

# === CONFIGURATION ===
EXCEL_LINKS_FILE = 'EXCEL/breguet_watch_links.xlsx'  # Fichier généré par scraping_url.py
TEMP_OUTPUT_FILE = 'EXCEL/breguet_json_details_temp.xlsx'
OUTPUT_EXCEL_FILE = TEMP_OUTPUT_FILE  # Le fichier temp devient le fichier principal
BASE_URL = 'https://everywatch.com/breguet'
BATCH_SIZE = 25  # Nombre de montres par batch
BATCH_DELAY_RANGE = (2, 5)  # Délai (en secondes) entre chaque batch (réduit)

ua = UserAgent()

# === FONCTIONS UTILITAIRES ===
def get_build_id(url):
    """Récupère le buildId Next.js depuis la page (sans Selenium)"""
    try:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return None
            
        content = response.text
        
        # Essayer différents patterns
        patterns = [
            r'"buildId":"([^"]+)"',
            r'"buildId"\s*:\s*"([^"]+)"',
            r'/_next/static/([a-zA-Z0-9_-]{8,})/',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                build_id = match.group(1)
                if len(build_id) >= 8:
                    return build_id
                    
        return None
        
    except Exception:
        return None


    """Récupère le buildId Next.js depuis la page principale (Selenium headless)."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f'--user-agent={ua.chrome}')
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(random.uniform(2, 4))
        page_source = driver.page_source
        driver.quit()
        build_id_match = re.search(r'"buildId":"([^"]+)"', page_source)
        if build_id_match:
            return build_id_match.group(1)
    except Exception as e:
        print(f"Erreur get_build_id: {e}")
        try:
            driver.quit()
        except:
            pass
    return None

def convert_slug_to_json_url(slug, build_id):
    """Transforme un slug de montre en URL JSON API."""
    path_parts = slug.strip('/').split('/')
    if len(path_parts) >= 3:
        brand = path_parts[0]
        if path_parts[-1].startswith('watch-'):
            if len(path_parts) == 3:
                model_slug = path_parts[1]
                watch_id = path_parts[2]
                json_path = f"{brand}/{model_slug}/{watch_id}.json"
                params = f"brand={brand}&modelSlug={model_slug}&watchId={watch_id}"
            elif len(path_parts) == 2:
                watch_id = path_parts[1]
                json_path = f"{brand}/{watch_id}.json"
                params = f"brand={brand}&watchId={watch_id}"
            else:
                model_slug = path_parts[1]
                ref_slug = path_parts[2]
                watch_id = path_parts[3]
                json_path = f"{brand}/{model_slug}/{ref_slug}/{watch_id}.json"
                params = f"brand={brand}&modelSlug={model_slug}&refSlug={ref_slug}&watchId={watch_id}"
            return f"https://everywatch.com/_next/data/{build_id}/{json_path}?{params}"
    return None

def extract_slug_from_url(url):
    """Extrait le slug à partir d'une URL de montre classique."""
    # Ex: https://everywatch.com/breguet/classique/watch-123456
    match = re.search(r'everywatch.com/(.+)', url)
    if match:
        return match.group(1)
    return None

def get_random_headers(ref_url=BASE_URL):
    return {
        'accept': '*/*',
        'accept-language': random.choice([
            'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'en-US,en;q=0.9,fr;q=0.8',
            'de-DE,de;q=0.9,en;q=0.8'
        ]),
        'referer': ref_url,
        'user-agent': ua.random,
        'x-nextjs-data': '1'
    }

def scrape_json_detail(json_url, source_url):
    try:
        headers = get_random_headers()
        response = requests.get(json_url, headers=headers, timeout=30)
        if response.status_code != 200:
            return {'error': f'Status {response.status_code}', 'source_url': source_url}
        data = response.json()
        page_props = data.get('pageProps', {})
        watch_detail = page_props.get('watchDetail', {})
        related_watches = page_props.get('relatedWatches', {})
        similar_watches = page_props.get('similarWatches', {})
        # === IMAGES ===
        images = []
        primary_image = None
        for img in watch_detail.get('watchImages', []):
            image_data = {
                'url': img.get('url'),
                'original': img.get('original'),
                'previewEmail320': img.get('previewEmail320'),
                'preview320': img.get('preview320'),
                'preview480': img.get('preview480'),
                'preview768': img.get('preview768'),
                'preview960': img.get('preview960'),
                'preview1366': img.get('preview1366'),
                'isPrimary': img.get('isPrimary', False),
                'isDeleted': img.get('isDeleted', False)
            }
            images.append(image_data)
            if img.get('isPrimary', False):
                primary_image = image_data
        if not primary_image and watch_detail.get('primaryWatchImage'):
            primary_image = watch_detail['primaryWatchImage']
        # === RELATED WATCHES ===
        related_watches_list = []
        if isinstance(related_watches.get('data'), list):
            for watch in related_watches['data']:
                related_watch = {
                    'watchId': watch.get('watchId'),
                    'manufactureName': watch.get('manufactureName'),
                    'modelName': watch.get('modelName'),
                    'referenceNumber': watch.get('referenceNumber'),
                    'slug': watch.get('slug'),
                    'primaryImage': watch.get('primaryImage'),
                    'caseMaterialName': watch.get('caseMaterialName'),
                    'dialColorName': watch.get('dialColorName'),
                    'minEstUsd': watch.get('minEstUsd'),
                    'maxEstUsd': watch.get('maxEstUsd'),
                    'netPayableUsd': watch.get('netPayableUsd'),
                    'auctionLotType': watch.get('auctionLotType')
                }
                related_watches_list.append(related_watch)
        # === SIMILAR WATCHES ===
        similar_watches_list = []
        if isinstance(similar_watches.get('data'), list):
            for watch in similar_watches['data']:
                similar_watch = {
                    'watchId': watch.get('watchId'),
                    'manufactureName': watch.get('manufactureName'),
                    'modelName': watch.get('modelName'),
                    'referenceNumber': watch.get('referenceNumber'),
                    'slug': watch.get('slug'),
                    'primaryImage': watch.get('primaryImage'),
                    'sourceLink': watch.get('sourceLink'),
                    'organizationName': watch.get('organizationName'),
                    'sellerOrganizationName': watch.get('sellerOrganizationName'),
                    'minEstUsd': watch.get('minEstUsd'),
                    'daysOnMarket': watch.get('daysOnMarket'),
                    'countryName': watch.get('countryName')
                }
                similar_watches_list.append(similar_watch)
        # === FEATURES ===
        watch_features = watch_detail.get('watchFeatures', []) if isinstance(watch_detail.get('watchFeatures'), list) else []
        # === MSRP ===
        msrp_data = watch_detail.get('msrp', []) if isinstance(watch_detail.get('msrp'), list) else []
        # === CONSTRUCTION DU DICT FINAL ===
        watch_data = {
            'source_url': source_url,
            'scraped_at': datetime.now().isoformat(),
            'scraper_version': 'json_extractor_v2.0',
            'watchId': watch_detail.get('watchId'),
            'masterId': page_props.get('masterId'),
            'id': watch_detail.get('id'),
            'imageSimilarityScore': watch_detail.get('imageSimilarityScore'),
            'manufacturerId': watch_detail.get('manufacturerId'),
            'manufactureName': watch_detail.get('manufactureName'),
            'manufacturerSlug': watch_detail.get('manufacturerSlug'),
            'manufacturerURL': watch_detail.get('manufacturerURL'),
            'manufacturerPriority': watch_detail.get('manufacturerPriority'),
            'manufacturerParentId': watch_detail.get('manufacturerParentId'),
            'isActiveManufacturer': watch_detail.get('isActiveManufacturer'),
            'defaultManufacturerId': watch_detail.get('defaultManufacturerId'),
            'defaultManufacturerName': watch_detail.get('defaultManufacturerName'),
            'modelId': watch_detail.get('modelId'),
            'modelName': watch_detail.get('modelName'),
            'modelSlug': watch_detail.get('modelSlug'),
            'modelURL': watch_detail.get('modelURL'),
            'modelPriority': watch_detail.get('modelPriority'),
            'modelParentId': watch_detail.get('modelParentId'),
            'isActiveModel': watch_detail.get('isActiveModel'),
            'defaultModelId': watch_detail.get('defaultModelId'),
            'defaultModelName': watch_detail.get('defaultModelName'),
            'referenceNumberId': watch_detail.get('referenceNumberId'),
            'referenceNumber': watch_detail.get('referenceNumber'),
            'referenceNumberSlug': watch_detail.get('referenceNumberSlug'),
            'referenceNumberURL': watch_detail.get('referenceNumberURL'),
            'referenceNumberIsPending': watch_detail.get('referenceNumberIsPending'),
            'referenceParentId': watch_detail.get('referenceParentId'),
            'isActiveReferenceNumber': watch_detail.get('isActiveReferenceNumber'),
            'defaultReferenceNumberId': watch_detail.get('defaultReferenceNumberId'),
            'defaultReferenceNumberName': watch_detail.get('defaultReferenceNumberName'),
            'defaultReferenceNumberParentId': watch_detail.get('defaultReferenceNumberParentId'),
            'defaultReferenceNumberParentName': watch_detail.get('defaultReferenceNumberParentName'),
            'referenceParent': watch_detail.get('referenceParent'),
            'watchTitle': watch_detail.get('watchTitle'),
            'description': watch_detail.get('description'),
            'descriptionHtml': watch_detail.get('descriptionHtml'),
            'catelogNotes': watch_detail.get('catelogNotes'),
            'notes': watch_detail.get('notes'),
            'dimension': watch_detail.get('dimension'),
            'sourceLink': watch_detail.get('sourceLink'),
            'slug': watch_detail.get('slug'),
            'caseMaterialId': watch_detail.get('caseMaterialId'),
            'caseMaterialName': watch_detail.get('caseMaterialName'),
            'caseMaterialParentId': watch_detail.get('caseMaterialParentId'),
            'isActiveCaseMaterial': watch_detail.get('isActiveCaseMaterial'),
            'defaultCaseMaterialId': watch_detail.get('defaultCaseMaterialId'),
            'defaultCaseMaterialName': watch_detail.get('defaultCaseMaterialName'),
            'caseSizeId': watch_detail.get('caseSizeId'),
            'caseSizeName': watch_detail.get('caseSizeName'),
            'caseSizeParentId': watch_detail.get('caseSizeParentId'),
            'isActiveCaseSize': watch_detail.get('isActiveCaseSize'),
            'defaultCaseSizeId': watch_detail.get('defaultCaseSizeId'),
            'defaultCaseSizeName': watch_detail.get('defaultCaseSizeName'),
            'bezelMaterialId': watch_detail.get('bezelMaterialId'),
            'bezelMaterialName': watch_detail.get('bezelMaterialName'),
            'bezelMaterialParentId': watch_detail.get('bezelMaterialParentId'),
            'isActiveBezelMaterial': watch_detail.get('isActiveBezelMaterial'),
            'defaultBezelMaterialId': watch_detail.get('defaultBezelMaterialId'),
            'defaultBezelMaterialName': watch_detail.get('defaultBezelMaterialName'),
            'dialColorId': watch_detail.get('dialColorId'),
            'dialColorName': watch_detail.get('dialColorName'),
            'dialColorParentId': watch_detail.get('dialColorParentId'),
            'isActiveDialColor': watch_detail.get('isActiveDialColor'),
            'defaultColorId': watch_detail.get('defaultColorId'),
            'defaultColorName': watch_detail.get('defaultColorName'),
            'movementId': watch_detail.get('movementId'),
            'movementName': watch_detail.get('movementName'),
            'movementParentId': watch_detail.get('movementParentId'),
            'isActiveMovement': watch_detail.get('isActiveMovement'),
            'defaultMovementId': watch_detail.get('defaultMovementId'),
            'defaultMovementName': watch_detail.get('defaultMovementName'),
            'movementNo': watch_detail.get('movementNo'),
            'braceletMaterialId': watch_detail.get('braceletMaterialId'),
            'braceletMaterialName': watch_detail.get('braceletMaterialName'),
            'braceletMaterialParentId': watch_detail.get('braceletMaterialParentId'),
            'isActiveBraceletMaterial': watch_detail.get('isActiveBraceletMaterial'),
            'defaultBraceletMaterialId': watch_detail.get('defaultBraceletMaterialId'),
            'defaultBraceletMaterialName': watch_detail.get('defaultBraceletMaterialName'),
            'claspMaterialId': watch_detail.get('claspMaterialId'),
            'claspMaterialName': watch_detail.get('claspMaterialName'),
            'claspMaterialParentId': watch_detail.get('claspMaterialParentId'),
            'isActiveClaspMaterial': watch_detail.get('isActiveClaspMaterial'),
            'defaultClaspMaterialId': watch_detail.get('defaultClaspMaterialId'),
            'defaultClaspMaterialName': watch_detail.get('defaultClaspMaterialName'),
            'functionId': watch_detail.get('functionId'),
            'functionName': watch_detail.get('functionName'),
            'functionParentId': watch_detail.get('functionParentId'),
            'isActiveFunction': watch_detail.get('isActiveFunction'),
            'defaultFunctionId': watch_detail.get('defaultFunctionId'),
            'defaultFunctionName': watch_detail.get('defaultFunctionName'),
            'yearOfProductionId': watch_detail.get('yearOfProductionId'),
            'yearOfProduction': watch_detail.get('yearOfProduction'),
            'yearOfProductionParentId': watch_detail.get('yearOfProductionParentId'),
            'isActiveYearOfProduction': watch_detail.get('isActiveYearOfProduction'),
            'defaultYearOfProductionId': watch_detail.get('defaultYearOfProductionId'),
            'defaultYearOfProductionName': watch_detail.get('defaultYearOfProductionName'),
            'gender': watch_detail.get('gender'),
            'conditionId': watch_detail.get('conditionId'),
            'conditionName': watch_detail.get('conditionName'),
            'conditionParentId': watch_detail.get('conditionParentId'),
            'isActiveCondition': watch_detail.get('isActiveCondition'),
            'defaultConditionId': watch_detail.get('defaultConditionId'),
            'defaultConditionName': watch_detail.get('defaultConditionName'),
            'isBox': watch_detail.get('isBox'),
            'isPaper': watch_detail.get('isPaper'),
            'box': watch_detail.get('box'),
            'paper': watch_detail.get('paper'),
            'certificationId': watch_detail.get('certificationId'),
            'certificationName': watch_detail.get('certificationName'),
            'nickNameId': watch_detail.get('nickNameId'),
            'nickName': watch_detail.get('nickName'),
            'nickNameParentId': watch_detail.get('nickNameParentId'),
            'isActiveNickName': watch_detail.get('isActiveNickName'),
            'defaultNickNameId': watch_detail.get('defaultNickNameId'),
            'defaultNickName': watch_detail.get('defaultNickName'),
            'auctionLotType': watch_detail.get('auctionLotType'),
            'auctionLotPublishId': watch_detail.get('auctionLotPublishId'),
            'lotId': watch_detail.get('lotId'),
            'lotNumber': watch_detail.get('lotNumber'),
            'lotNumberint': watch_detail.get('lotNumberint'),
            'lotSlug': watch_detail.get('lotSlug'),
            'lotQuantity': watch_detail.get('lotQuantity'),
            'isResultPending': watch_detail.get('isResultPending'),
            'lotStatusId': watch_detail.get('lotStatusId'),
            'lotStatusName': watch_detail.get('lotStatusName'),
            'lotPerformance': watch_detail.get('lotPerformance'),
            'eventPublishId': watch_detail.get('eventPublishId'),
            'eventPublishTitle': watch_detail.get('eventPublishTitle'),
            'eventPublishLotQuantity': watch_detail.get('eventPublishLotQuantity'),
            'eventPublishEndDate': watch_detail.get('eventPublishEndDate'),
            'eventPublistStartDate': watch_detail.get('eventPublistStartDate'),
            'eventSlug': watch_detail.get('eventSlug'),
            'eventIsDeleted': watch_detail.get('eventIsDeleted'),
            'eventTypeId': watch_detail.get('eventTypeId'),
            'eventTypeName': watch_detail.get('eventTypeName'),
            'locationId': watch_detail.get('locationId'),
            'countryId': watch_detail.get('countryId'),
            'countryName': watch_detail.get('countryName'),
            'countryCode': watch_detail.get('countryCode'),
            'countryCode2': watch_detail.get('countryCode2'),
            'flagURL': watch_detail.get('flagURL'),
            'eventCountryId': watch_detail.get('eventCountryId'),
            'eventCountryName': watch_detail.get('eventCountryName'),
            'eventCityId': watch_detail.get('eventCityId'),
            'eventCityName': watch_detail.get('eventCityName'),
            'organizationId': watch_detail.get('organizationId'),
            'organizationName': watch_detail.get('organizationName'),
            'organizationSlug': watch_detail.get('organizationSlug'),
            'sellerOrganizationName': watch_detail.get('sellerOrganizationName'),
            'infoSourceId': watch_detail.get('infoSourceId'),
            'infoSourceName': watch_detail.get('infoSourceName'),
            'infoSourceSlug': watch_detail.get('infoSourceSlug'),
            'currencyId': watch_detail.get('currencyId'),
            'currencyName': watch_detail.get('currencyName'),
            'price': watch_detail.get('price'),
            'curruncyForSorting': watch_detail.get('curruncyForSorting'),
            'soldPrice': watch_detail.get('soldPrice'),
            'maximumEstimatedPrice': watch_detail.get('maximumEstimatedPrice'),
            'minimumEstimatedPrice': watch_detail.get('minimumEstimatedPrice'),
            'minEstUsd': watch_detail.get('minEstUsd'),
            'maxEstUsd': watch_detail.get('maxEstUsd'),
            'hammerUsd': watch_detail.get('hammerUsd'),
            'netPayableUsd': watch_detail.get('netPayableUsd'),
            'retailCurrencyId': watch_detail.get('retailCurrencyId'),
            'retailPrice': watch_detail.get('retailPrice'),
            'retailPriceUsd': watch_detail.get('retailPriceUsd'),
            'minEstEur': watch_detail.get('minEstEur'),
            'maxEstEur': watch_detail.get('maxEstEur'),
            'hammerEur': watch_detail.get('hammerEur'),
            'netPayableEur': watch_detail.get('netPayableEur'),
            'retailPriceEur': watch_detail.get('retailPriceEur'),
            'minEstGbp': watch_detail.get('minEstGbp'),
            'maxEstGbp': watch_detail.get('maxEstGbp'),
            'hammerGbp': watch_detail.get('hammerGbp'),
            'netPayableGbp': watch_detail.get('netPayableGbp'),
            'retailPriceGbp': watch_detail.get('retailPriceGbp'),
            'minEstChf': watch_detail.get('minEstChf'),
            'maxEstChf': watch_detail.get('maxEstChf'),
            'hammerChf': watch_detail.get('hammerChf'),
            'netPayableChf': watch_detail.get('netPayableChf'),
            'retailPriceChf': watch_detail.get('retailPriceChf'),
            'minEstHkd': watch_detail.get('minEstHkd'),
            'maxEstHkd': watch_detail.get('maxEstHkd'),
            'hammerHkd': watch_detail.get('hammerHkd'),
            'netPayableHkd': watch_detail.get('netPayableHkd'),
            'retailPriceHkd': watch_detail.get('retailPriceHkd'),
            'minEstSgd': watch_detail.get('minEstSgd'),
            'maxEstSgd': watch_detail.get('maxEstSgd'),
            'hammerSgd': watch_detail.get('hammerSgd'),
            'netPayableSgd': watch_detail.get('netPayableSgd'),
            'retailPriceSgd': watch_detail.get('retailPriceSgd'),
            'minEstAed': watch_detail.get('minEstAed'),
            'maxEstAed': watch_detail.get('maxEstAed'),
            'hammerAed': watch_detail.get('hammerAed'),
            'netPayableAed': watch_detail.get('netPayableAed'),
            'retailPriceAed': watch_detail.get('retailPriceAed'),
            'minEstJpy': watch_detail.get('minEstJpy'),
            'maxEstJpy': watch_detail.get('maxEstJpy'),
            'hammerJpy': watch_detail.get('hammerJpy'),
            'netPayableJpy': watch_detail.get('netPayableJpy'),
            'retailPriceJpy': watch_detail.get('retailPriceJpy'),
            'buyersPremiumRate': watch_detail.get('buyersPremiumRate'),
            'isBuyersPremiumIncluded': watch_detail.get('isBuyersPremiumIncluded'),
            'auctionIsDeleted': watch_detail.get('auctionIsDeleted'),
            'images': images,
            'primaryImage': primary_image,
            'relatedWatches': related_watches_list,
            'similarWatches': similar_watches_list,
            'features': watch_features,
            'msrp': msrp_data
        }
        return watch_data
    except Exception as e:
        return {'error': str(e), 'source_url': source_url}

def main():
    print('Chargement des liens depuis', EXCEL_LINKS_FILE)
    df_links = pd.read_excel(EXCEL_LINKS_FILE)
    all_links = set(df_links['URL'].dropna().unique())
    print(f'Nombre total de liens dans {EXCEL_LINKS_FILE}: {len(all_links)}')

    # Charger les liens déjà scrapés (si le fichier existe)
    already_scraped = set()
    if os.path.exists(OUTPUT_EXCEL_FILE):
        print(f'Chargement des liens déjà scrapés depuis {OUTPUT_EXCEL_FILE}')
        df_existing = pd.read_excel(OUTPUT_EXCEL_FILE)
        already_scraped = set(df_existing['source_url'].dropna().unique())
        print(f'Nombre de montres déjà scrapées: {len(already_scraped)}')

    # Filtrer pour ne garder que les nouveaux liens à scraper
    links_to_scrape = list(all_links - already_scraped)
    print(f'Nombre de nouvelles montres à scraper: {len(links_to_scrape)}')

    if not links_to_scrape:
        print('Aucune nouvelle montre à scraper. Terminé !')
        return

    print('Obtention du buildId...')
    build_id = get_build_id(BASE_URL)
    if not build_id:
        print('Impossible de récupérer le buildId, arrêt.')
        return
    print('buildId =', build_id)

    total = len(links_to_scrape)
    num_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_idx in range(num_batches):
        start = batch_idx * BATCH_SIZE
        end = min((batch_idx + 1) * BATCH_SIZE, total)
        batch_urls = links_to_scrape[start:end]
        print(f'\n=== Batch {batch_idx+1}/{num_batches} ({start+1}-{end}) ===')
        
        # Liste pour stocker les résultats du batch actuel
        batch_results = []
        
        for i, url in enumerate(batch_urls, start=start+1):
            slug = extract_slug_from_url(url)
            if not slug:
                print(f'[{i}/{total}] Slug non trouvé pour {url}, skip.')
                continue
            json_url = convert_slug_to_json_url(slug, build_id)
            if not json_url:
                print(f'[{i}/{total}] JSON URL non générée pour {url}, skip.')
                continue
            print(f'[{i}/{total}] Scraping {json_url}')
            data = scrape_json_detail(json_url, url)
            batch_results.append(data)
            time.sleep(random.uniform(1, 3))  # Délai réduit entre chaque requête : max 3 secondes

        # Sauvegarder uniquement les nouvelles montres de ce batch
        if batch_results:
            print(f'Sauvegarde de {len(batch_results)} nouvelles montres...')
            # Charger les résultats existants
            if os.path.exists(OUTPUT_EXCEL_FILE):
                df_existing = pd.read_excel(OUTPUT_EXCEL_FILE)
                existing_results = df_existing.to_dict('records')
                # Ajouter les nouvelles montres à la fin
                all_results = existing_results + batch_results
            else:
                all_results = batch_results
            
            # Sauvegarder le fichier mis à jour
            df_all = pd.json_normalize(all_results)
            df_all.to_excel(OUTPUT_EXCEL_FILE, index=False)
            print(f'Total des montres dans le fichier: {len(all_results)}')

        # Délai court entre les batchs (sauf le dernier)
        if batch_idx < num_batches - 1:
            batch_delay = random.uniform(*BATCH_DELAY_RANGE)
            print(f'Attente de {batch_delay:.1f} secondes avant le prochain batch...')
            time.sleep(batch_delay)

    print(f'\nTerminé ! Les résultats sont dans {OUTPUT_EXCEL_FILE}')


"""
if __name__ == '__main__':
    main()
"""