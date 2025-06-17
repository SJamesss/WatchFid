import pandas as pd
import json
import openai
import time
import os

def process_watches(api_key, input_file="watches_details.xlsx", max_items=300, sleep_time=1.0, save_interval=25):
    """
    Traite les descriptions de montres et extrait les données structurées
    
    Args:
        api_key: Clé API OpenAI
        input_file: Fichier Excel d'entrée (défaut: watches_details.xlsx)
        max_items: Nombre maximum d'éléments à traiter (défaut: 300)
        sleep_time: Pause entre les appels API en secondes (défaut: 1.0)
        save_interval: Intervalle pour sauvegarder progressivement (défaut: 25)
    
    Returns:
        DataFrame avec les données extraites et originales combinées
    """
    client = openai.OpenAI(api_key=api_key)

    # Vérifier l'existence des fichiers de prompt
    prompt_files = ['extraction_prompt_part1.md', 'extraction_prompt_part2.md']
    for file in prompt_files:
        if not os.path.exists(file):
            print(f"Erreur: Le fichier {file} est requis mais n'existe pas.")
            return None

    # Charger les prompts
    try:
        with open('extraction_prompt_part1.md', 'r', encoding='utf-8') as f:
            md_part1 = f.read()
        
        with open('extraction_prompt_part2.md', 'r', encoding='utf-8') as f:
            md_part2 = f.read()
    except Exception as e:
        print(f"Erreur lors du chargement des prompts: {e}")
        return None

    # Vérifier l'existence du fichier d'entrée
    if not os.path.exists(input_file):
        print(f"Erreur: Le fichier {input_file} n'existe pas.")
        print("Veuillez d'abord exécuter match_columns.py pour créer le fichier.")
        return None

    # Charger les données Excel complètes
    try:
        watches_details = pd.read_excel(input_file)
        print(f"Fichier {input_file} chargé avec succès: {len(watches_details)} lignes")
    except Exception as e:
        print(f"Erreur lors du chargement de {input_file}: {e}")
        return None
    
    # Créer une colonne processing_status si elle n'existe pas
    if 'processing_status' not in watches_details.columns:
        watches_details['processing_status'] = ""
        print("Colonne 'processing_status' créée")
    
    # Filtrer seulement les lignes qui n'ont pas processing_status = "success"
    lines_to_process = []
    for idx, row in watches_details.iterrows():
        current_status = row.get('processing_status', '')
        if current_status != 'success':
            lines_to_process.append(idx)
    
    print(f"Nombre total de lignes: {len(watches_details)}")
    print(f"Lignes à traiter: {len(lines_to_process)}")
    
    # Afficher le statut actuel si des lignes ont déjà été traitées
    if 'processing_status' in watches_details.columns:
        status_counts = watches_details['processing_status'].value_counts()
        if len(status_counts) > 0:
            print("\nStatut actuel des lignes:")
            for status, count in status_counts.items():
                if status != "":
                    print(f"  {status}: {count}")
    
    # Limiter le nombre d'éléments à traiter
    max_to_process = min(max_items, len(lines_to_process))
    lines_to_process = lines_to_process[:max_to_process]
    
    if len(lines_to_process) == 0:
        print("Aucune ligne à traiter. Toutes les descriptions ont déjà été analysées avec succès.")
        return watches_details
    
    print(f"Traitement de {len(lines_to_process)} lignes dans cette session...")
    
    # Structure JSON de base pour les champs extraits
    blank_extracted_json = {
        "case #": "",
        "movement #": "", 
        "caliber": "",
        "Dial clssification": "",
        "Dial 6": "",
        "Dial text": "", 
        "SWISS": "",
        "Dial detail": "",
        "Bezel": "",
        "Pushers": "", 
        "Hands": "", 
        "caseback inside": "",
        "crown": "",
        "sold on": "",
        "AD": "",
        "1st owner": "",
        "confidence_score": 0.0,
        "analysis_notes": "",
        "processing_status": "processed"
    }

    # Compteur pour la sauvegarde progressive
    processed_count = 0
    
    for idx in lines_to_process:
        try:
            # Récupérer la ligne à traiter
            original_row = watches_details.loc[idx].copy()
            
            # Obtenir la description
            description = original_row.get("Description", "")
            
            if pd.isna(description) or description == "":
                # Pour les descriptions vides, on garde les données originales et on ajoute les champs vides
                extracted_data = blank_extracted_json.copy()
                extracted_data["processing_status"] = "empty_description"
                print(f"[{processed_count+1}/{len(lines_to_process)}] Description vide pour la ligne {idx}")
            else:
                print(f"[{processed_count+1}/{len(lines_to_process)}] Traitement de la ligne {idx}...")
                
                # Construire le prompt avec instruction JSON
                prompt = f"{md_part1}{description}{md_part2}\n\nRéponds uniquement avec un objet JSON valide, sans texte avant ou après:"
                
                # Utiliser GPT-4o avec response_format JSON
                response = client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=3000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"}
                )
                
                # Récupérer et parser la réponse JSON
                json_response = response.choices[0].message.content
                
                try:
                    extracted_data = json.loads(json_response)
                    
                    # S'assurer que tous les champs requis sont présents
                    for key in blank_extracted_json:
                        if key not in extracted_data:
                            extracted_data[key] = blank_extracted_json[key]
                    
                    # Nettoyer les valeurs null
                    for key in extracted_data:
                        if extracted_data[key] is None:
                            extracted_data[key] = ""
                    
                    extracted_data["processing_status"] = "success"
                    
                except json.JSONDecodeError as e:
                    print(f"Erreur JSON pour la ligne {idx}: {e}")
                    extracted_data = blank_extracted_json.copy()
                    extracted_data["analysis_notes"] = f"Erreur JSON: {str(e)}"
                    extracted_data["processing_status"] = "json_error"
            
            # Mettre à jour directement dans le DataFrame principal
            for key, value in extracted_data.items():
                # Ajouter la colonne si elle n'existe pas
                if key not in watches_details.columns:
                    watches_details[key] = ""
                
                # Si la colonne existe et est vide/NaN, ou si c'est une nouvelle colonne
                current_value = watches_details.loc[idx, key]
                if pd.isna(current_value) or current_value == "":
                    # Conversion explicite pour éviter le warning dtype
                    watches_details.loc[idx, key] = str(value) if value is not None else ""
            
            processed_count += 1
            
            # Sauvegarde progressive - tous les X éléments OU si c'est le dernier
            if processed_count % save_interval == 0 or processed_count == len(lines_to_process):
                watches_details.to_excel(input_file, index=False)
                print(f"Sauvegarde: {processed_count}/{len(lines_to_process)} lignes traitées")
        
        except Exception as e:
            print(f"Erreur pour la ligne {idx}: {e}")
            
            # En cas d'erreur, marquer la ligne avec le statut d'erreur
            error_data = blank_extracted_json.copy()
            error_data["analysis_notes"] = f"Erreur de traitement: {str(e)}"
            error_data["processing_status"] = "error"
            
            for key, value in error_data.items():
                # Ajouter la colonne si elle n'existe pas
                if key not in watches_details.columns:
                    watches_details[key] = ""
                
                # Même logique : ne pas écraser les données existantes
                current_value = watches_details.loc[idx, key]
                if pd.isna(current_value) or current_value == "":
                    # Conversion explicite pour éviter le warning dtype
                    watches_details.loc[idx, key] = str(value) if value is not None else ""
            
            processed_count += 1
            
            # Sauvegarde progressive même en cas d'erreur
            if processed_count % save_interval == 0 or processed_count == len(lines_to_process):
                watches_details.to_excel(input_file, index=False)
                print(f"Sauvegarde: {processed_count}/{len(lines_to_process)} lignes traitées")
        
        # Pause entre les appels
        if processed_count < len(lines_to_process):
            time.sleep(sleep_time)

    # Retourner le DataFrame final (déjà sauvegardé)
    return watches_details

def show_processing_summary(input_file="watches_details.xlsx"):
    """
    Affiche un résumé du statut de traitement
    """
    if not os.path.exists(input_file):
        print(f"Le fichier {input_file} n'existe pas.")
        return
    
    df = pd.read_excel(input_file)
    
    print(f"\n=== RÉSUMÉ DU TRAITEMENT - {input_file} ===")
    print(f"Total de lignes: {len(df)}")
    
    if 'processing_status' in df.columns:
        status_counts = df['processing_status'].value_counts()
        print("\nStatuts de traitement:")
        for status, count in status_counts.items():
            if status != "":
                print(f"  {status}: {count}")
        
        # Calculer les statistiques
        success_count = status_counts.get('success', 0)
        empty_desc_count = status_counts.get('empty_description', 0)
        error_count = status_counts.get('error', 0) + status_counts.get('json_error', 0)
        unprocessed_count = len(df) - status_counts.sum()
        
        print(f"\nRésumé:")
        print(f"  Traités avec succès: {success_count}")
        print(f"  Descriptions vides: {empty_desc_count}")
        print(f"  Erreurs: {error_count}")
        print(f"  Non traités: {unprocessed_count}")
        
        completion_rate = (success_count / len(df)) * 100 if len(df) > 0 else 0
        print(f"  Taux de completion: {completion_rate:.1f}%")
    else:
        print("Aucune colonne 'processing_status' trouvée - traitement non encore commencé")

"""
# Exemple d'utilisation
if __name__ == "__main__":
    # Afficher d'abord le résumé
    show_processing_summary()
    
    # Demander confirmation pour continuer
    response = input("\nVoulez-vous continuer le traitement ? (y/n): ")
    if response.lower() not in ['y', 'yes', 'o', 'oui']:
        print("Traitement annulé.")
        exit()
    
    API_KEY = "API_KEY"
    
    results = process_watches(API_KEY)
    
    if results is not None:
        print(f"\nTraitement terminé: {len(results)} éléments au total")
        print("Données mises à jour dans: watches_details.xlsx")
        
        # Afficher le résumé final
        show_processing_summary()
    else:
        print("Le traitement a échoué.")
"""