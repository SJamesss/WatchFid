import pandas as pd
import numpy as np
import os

def align_breguet_daytona_data():
    """
    Aligne les données Breguet selon le schéma Daytona en préservant les données existantes
    """
    
    # Fichiers fixes
    breguet_file = "EXCEL/breguet_json_details_temp.xlsx"
    daytona_file = "EXCEL/Daytona-db-sample.xlsx"
    output_file = "EXCEL/watches_details.xlsx"
    
    # Lecture des fichiers
    breguet_df = pd.read_excel(breguet_file)
    daytona_df = pd.read_excel(daytona_file)
    
    # Vérifier si le fichier de sortie existe déjà
    if os.path.exists(output_file):
        print(f"Le fichier {output_file} existe déjà. Chargement des données existantes...")
        existing_df = pd.read_excel(output_file)
        
        # Identifier les URLs déjà présentes dans le fichier existant
        existing_urls = set()
        if 'source_url' in existing_df.columns:
            existing_urls = set(existing_df['source_url'].dropna())
        elif 'source' in existing_df.columns:
            existing_urls = set(existing_df['source'].dropna())
        
        print(f"Nombre de montres déjà présentes: {len(existing_urls)}")
        
        # Filtrer les nouvelles données Breguet (qui ne sont pas déjà dans le fichier)
        if 'source_url' in breguet_df.columns:
            breguet_urls = set(breguet_df['source_url'].dropna())
            new_breguet_mask = ~breguet_df['source_url'].isin(existing_urls)
            new_breguet_df = breguet_df[new_breguet_mask].copy()
        else:
            print("Attention: colonne 'source_url' non trouvée dans breguet_df")
            new_breguet_df = breguet_df.copy()
        
        print(f"Nouvelles montres Breguet à ajouter: {len(new_breguet_df)}")
        
        # Si aucune nouvelle donnée Breguet, retourner le fichier existant
        if len(new_breguet_df) == 0:
            print("Aucune nouvelle donnée à ajouter. Le fichier existant est conservé.")
            return existing_df
        
        # Utiliser le schéma du fichier existant comme base
        base_df = existing_df.copy()
        
    else:
        print(f"Le fichier {output_file} n'existe pas. Création d'un nouveau fichier...")
        # Commencer avec le DataFrame Daytona complet
        base_df = daytona_df.copy()
        existing_urls = set()
        new_breguet_df = breguet_df.copy()
    
    # Mapping vers colonnes existantes
    existing_column_mapping = {
        'source_url': 'source',
        'scraped_at': 'Date',
        'modelName': 'Model',
        'referenceNumber': 'Reference',
        'caseMaterialName': 'Case material',
        'dialColorName': 'Dial color',
        'braceletMaterialName': 'Bracelet',
        'yearOfProduction': 'Model year',
        'conditionName': 'Condition',
        'countryName': 'Delivery country',
        'organizationName': 'last known location',
        'soldPrice': 'Sold',
    }
    
    # Nouvelles colonnes à ajouter (selon votre schéma)
    new_columns_mapping = {
        'manufactureName': 'Manufacture Name',
        'watchTitle': 'Watch Title', 
        'description': 'Description',
        'caseSizeName': 'Case Size',
        'movementName': 'Movement Type',
        'sellerOrganizationName': 'Seller Organization Name',
        'isBox': 'isBox',
        'isPaper': 'isPaper', 
        'box': 'box',
        'paper': 'paper',
        'primaryImage.original': 'primaryImage.original',
        'primaryImage.previewEmail320': 'primaryImage.previewEmail320',
        'primaryImage.preview320': 'primaryImage.preview320',
        'primaryImage.preview480': 'primaryImage.preview480',
        'primaryImage.preview768': 'primaryImage.preview768',
        'primaryImage.preview960': 'primaryImage.preview960',
        'primaryImage.preview1366': 'primaryImage.preview1366'
    }
    
    # Préparer les nouvelles lignes Breguet
    if len(new_breguet_df) > 0:
        breguet_aligned = pd.DataFrame()
        
        # Créer les colonnes selon le schéma existant avec NaN
        for col in base_df.columns:
            breguet_aligned[col] = np.nan
        
        # Remplir avec les données Breguet là où on a un mapping
        for breguet_col, target_col in existing_column_mapping.items():
            if breguet_col in new_breguet_df.columns and target_col in breguet_aligned.columns:
                breguet_aligned[target_col] = new_breguet_df[breguet_col].values
        
        # Traitement spécial pour FS Price et FS Currency
        if 'minEstUsd' in new_breguet_df.columns and 'maxEstUsd' in new_breguet_df.columns:
            fs_price = []
            for idx, row in new_breguet_df.iterrows():
                min_est = row.get('minEstUsd', 0)
                max_est = row.get('maxEstUsd', 0)
                
                if pd.notna(max_est) and max_est != 0:
                    fs_price.append(f"{min_est}-{max_est}")
                else:
                    fs_price.append(str(min_est) if pd.notna(min_est) else "")
            
            breguet_aligned['FS price'] = fs_price
            breguet_aligned['FS CURRENCY'] = 'USD'
            breguet_aligned['Sold currency'] = 'USD'
        
        # Ajouter les nouvelles colonnes pour les nouvelles données Breguet
        for breguet_col, new_col in new_columns_mapping.items():
            if breguet_col in new_breguet_df.columns:
                # Ajouter la colonne si elle n'existe pas déjà dans base_df
                if new_col not in base_df.columns:
                    base_df[new_col] = np.nan
                    breguet_aligned[new_col] = new_breguet_df[breguet_col].values
                else:
                    breguet_aligned[new_col] = new_breguet_df[breguet_col].values
            else:
                if new_col not in base_df.columns:
                    base_df[new_col] = np.nan
                breguet_aligned[new_col] = np.nan
        
        # Concaténer les données existantes + nouvelles données Breguet
        aligned_df = pd.concat([base_df, breguet_aligned], ignore_index=True)
    else:
        # Aucune nouvelle donnée, garder seulement les données existantes
        aligned_df = base_df.copy()
        
        # Ajouter les nouvelles colonnes vides si elles n'existent pas
        for new_col in new_columns_mapping.values():
            if new_col not in aligned_df.columns:
                aligned_df[new_col] = np.nan
    
    # Supprimer les doublons basés sur source_url ou source
    source_col = 'source_url' if 'source_url' in aligned_df.columns else 'source'
    if source_col in aligned_df.columns:
        aligned_df = aligned_df.drop_duplicates(subset=[source_col], keep='first')
    
    # Sauvegarde
    aligned_df.to_excel(output_file, index=False)
    
    print(f"Fichier {output_file} mis à jour avec succès!")
    print(f"Total de montres dans le fichier: {len(aligned_df)}")
    
    return aligned_df


def check_file_status(output_file="watches_details.xlsx"):
    """
    Vérifie le statut du fichier watches_details.xlsx pour le traitement par description_analysis.py
    """
    if not os.path.exists(output_file):
        print(f"Le fichier {output_file} n'existe pas encore.")
        return
    
    df = pd.read_excel(output_file)
    
    # Vérifier les colonnes de traitement
    if 'processing_status' in df.columns:
        status_counts = df['processing_status'].value_counts()
        print(f"\nStatut de traitement dans {output_file}:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Compter les lignes non traitées
        unprocessed = df[df['processing_status'] != 'success']
        print(f"\nLignes à traiter par description_analysis.py: {len(unprocessed)}")
    else:
        print(f"\nAucune colonne 'processing_status' trouvée.")
        print(f"Toutes les {len(df)} lignes seront traitées par description_analysis.py")
    
    # Vérifier la présence de descriptions
    if 'Description' in df.columns:
        descriptions_non_vides = df['Description'].notna().sum()
        print(f"Lignes avec description: {descriptions_non_vides}/{len(df)}")
    
    print(f"\nTotal de lignes dans le fichier: {len(df)}")

"""
if __name__ == "__main__":
    try:
        print("=== ALIGNEMENT DES DONNÉES ===")
        result_df = align_breguet_daytona_data()
        
        print("\n=== VÉRIFICATION DU STATUT ===")
        check_file_status()
        
        print("\n=== INSTRUCTIONS SUIVANTES ===")
        print("1. Vous pouvez maintenant exécuter description_analysis.py")
        print("2. Il ne traitera que les nouvelles lignes ou celles non marquées comme 'success'")
        print("3. Les données déjà traitées seront préservées")
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
"""