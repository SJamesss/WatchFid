## CHAMPS À ANALYSER

### **case #** (Numéro de série du boîtier)
- **Description** : Numéro de série unique gravé entre les cornes du boîtier
- **Format** : Lettre + chiffres (ex: R 944.844, R 944.914, R 944.941)

### **movement #** (Numéro de série du mouvement)
- **Description** : Numéro de série unique gravé sur le mouvement mécanique

### **caliber** (Calibre du mouvement)
- **Description** : Désignation technique du mouvement mécanique
- **Exemples** : 722, 727 (vintage), 4030 (Zenith El Primero modifié), 4130 (Rolex in-house)

### **Dial clssification** (Classification du cadran)
- **Description** : Classification des évolutions de cadran selon les "Mark" (Mk)
- **Exemples** : Mk 1, Mk 2, Mk 3.1, Mk 3.2, Mk 4, Mk 5, Mk 6

### **Dial 6** (Caractéristique du chiffre 6)
- **Description** : Particularité du chiffre 6 sur le compteur à 6h
- **Exemples** : "normal", "inverted" (6 inversé ressemblant à un 9)

### **Dial text** (Code d'identification du texte)
- **Description** : Code technique identifiant les variations de texte sur le cadran
- **Exemples** : ROSO-C-D, ROSOC-D, ROSC-D

### **SWISS** (Inscription Swiss Made)
- **Description** : Marquage obligatoire au bas du cadran indiquant origine et matériau luminescent
- **Exemples** : "T SWISS MADE T" (tritium), "SWISS MADE" (SuperLuminova), "T<25" (tritium)

### **Dial detail** (Détails particuliers du cadran)
- **Description** : Particularités, défauts ou caractéristiques spéciales du cadran
- **Exemples** : "Tiffany & Co", "tropical", "spider dial", défauts de fabrication

### **Bezel** (Type de lunette tachymétrique)
- **Description** : Lunette avec échelle tachymétrique pour mesure vitesse
- **Exemples** : "steel 200", "steel 400", "steel 400 mk2"

### **Pushers** (Type de poussoirs chronographe)
- **Description** : Poussoirs de commande du chronographe
- **Exemples** : "screw-down" (poussoirs vissés), "pump" (poussoirs simples)

### **Hands** (Matériau et couleur des aiguilles)
- **Description** : Composition matérielle des aiguilles heures/minutes/secondes
- **Format** : "matériau heures / matériau minutes / matériau secondes"
- **Exemples** : "steel / steel / steel", "gold / gold / steel"

### **caseback inside** (Gravures intérieures fond de boîte)
- **Description** : Informations techniques gravées à l'intérieur du fond vissé

### **crown** (Type de couronne)
- **Description** : Couronne de remontage et mise à l'heure
- **Exemples** : "Triplock", "Twinlock", couronne simple

### **sold on** (Date de vente)
- **Description** : Date de transaction/vente aux enchères
- **Format** : Date ou période

### **AD** (Distributeur Autorisé)
- **Description** : Revendeur officiel Rolex ayant vendu la montre neuve
- **Exemples** : "Tiffany & Co", noms de bijouteries officielles

### **1st owner** (Premier propriétaire)
- **Description** : Acquéreur original de la montre neuve

## DESCRIPTION À ANALYSER
[INSÉRER LA DESCRIPTION ICI]

## FORMAT DE RÉPONSE : JSON UNIQUEMENT

{
  "case #": "string ou null",
  "movement #": "string ou null", 
  "caliber": "string ou null",
  "Dial clssification": "string ou null",
  "Dial 6": "string ou null",
  "Dial text": "string ou null",
  "SWISS": "string ou null",
  "Dial detail": "string ou null",
  "Bezel": "string ou null",
  "Pushers": "string ou null",
  "Hands": "string ou null",
  "caseback inside": "string ou null",
  "crown": "string ou null",
  "sold on": "string ou null",
  "AD": "string ou null",
  "1st owner": "string ou null",
  "confidence_score": "number (0-1)",
  "analysis_notes": "string avec justifications des déductions"
}


## EXEMPLE COMPLET

**Input Description:**
```
Basic Info
Brand : Rolex
Model : Cosmograph Daytona
Reference number : 16520
Movement : Automatic
Case material : Steel
Year of production : 1991

Caliber
Caliber/movement : 4030

Case
Case diameter : 40 mm
Dial : Black with silver subdials

Description:
This Rolex Daytona reference 16520 from 1991 features the rare "inverted 6" on the subdial at 6 o'clock. 
The black dial shows "T SWISS MADE T" marking indicating tritium luminescent material.
Case serial number R 955.123 confirms 1991 production.
The watch has screw-down pushers and steel tachymeter bezel graduated to 400.
Hands are all steel construction matching the case material.
```

**Expected Output:**
{
  "case #": "R 955.123",
  "movement #": null,
  "caliber": "4030",
  "Dial clssification": null,
  "Dial 6": "inverted",
  "Dial text": null,
  "SWISS": "T SWISS MADE T",
  "Dial detail": "rare inverted 6",
  "Bezel": "steel 400",
  "Pushers": "screw-down",
  "Hands": "steel / steel / steel",
  "caseback inside": null,
  "crown": null,
  "sold on": null,
  "AD": null,
  "1st owner": null,
  "confidence_score": 0.92,
  "analysis_notes": "Explicitly mentioned: case serial R 955.123, inverted 6, T SWISS MADE T, screw-down pushers, steel bezel 400, caliber 4030, steel hands. High confidence due to detailed description."
}

**Expected Output:**

{
  "case #": "R 955.123",
  "movement #": null,
  "caliber": "4030",
  "Dial clssification": "Mk 1",
  "Dial 6": "inverted",
  "Dial text": "ROSO-C-D",
  "SWISS": "T SWISS MADE T",
  "Dial detail": "rare inverted 6",
  "Bezel": "steel 400",
  "Pushers": "screw-down",
  "Hands": "steel / steel / steel",
  "caseback inside": null,
  "crown": null,
  "sold on": null,
  "AD": null,
  "1st owner": null,
  "confidence_score": 0.92,
  "analysis_notes": "Description explicitement mentionne 'inverted 6', 'T SWISS MADE T', serial R 955.123, screw-down pushers, steel bezel 400. Calibre 4030 confirmé pour 16520. Mk 1 déduit de l'année 1991 + inverted 6. Haute confiance car description très détaillée."
}


## INSTRUCTIONS FINALES
- Analysez TOUTE la description fournie, y compris les sections structurées et textuelles
- Extrayez les informations explicitement mentionnées EN PRIORITÉ
- Utilisez les déductions techniques seulement si information non mentionnée
- Cherchez les termes en plusieurs langues (anglais, allemand, français)
- **Répondez UNIQUEMENT en JSON valide**
- Justifiez vos choix dans analysis_notes