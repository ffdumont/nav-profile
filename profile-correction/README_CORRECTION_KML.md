# Correction des Profils d'Altitude KML SDVFR

## Résumé des Programmes Développés

### 1. Programme de Correction KML (`kml_altitude_corrector.py`)
Corrige automatiquement les profils d'altitude KML SDVFR pour représenter des trajectoires de navigation réalistes.

#### Fonctionnalités :
- **Récupération automatique des altitudes terrain** via API d'élévation (Open Elevation, USGS, Google)
- **Calcul des points de montée/descente** avec taux configurables (défaut: 500 ft/min)
- **Affichage en unités aéronautiques** : pieds (ft) pour les altitudes, miles nautiques (NM) pour les distances
- **Correction des altitudes incohérentes** : départ et arrivée à l'altitude du terrain

#### Utilisation :
```bash
python kml_altitude_corrector.py input.kml -o output_corrected.kml
```

#### Options :
- `--climb-rate` : Taux de montée en ft/min (défaut: 500)
- `--descent-rate` : Taux de descente en ft/min (défaut: 500)
- `--api-key` : Clé API Google pour l'élévation (optionnel)

### 2. Visualiseur de Profils (`kml_altitude_viewer.py`)
Visualise graphiquement les profils d'altitude des fichiers KML avec noms et altitudes des points.

#### Fonctionnalités :
- **Graphiques détaillés** avec noms des waypoints et altitudes
- **Résumés textuels** avec distances et altitudes
- **Comparaison de profils** multiples
- **Unités aéronautiques** : pieds et miles nautiques

#### Utilisation :
```bash
# Résumé textuel
python kml_altitude_viewer.py --summary input.kml

# Graphique
python kml_altitude_viewer.py input.kml -o graph.png

# Comparaison
python kml_altitude_viewer.py --compare file1.kml file2.kml -o comparison.png
```

### 3. Correcteur Spécialisé (`lfxu_lffu_corrector.py`)
Version spécialisée du correcteur pour le vol LFXU-LFFU avec corrections manuelles spécifiques.

#### Corrections appliquées :
- **BEVRO maintenu à 3100 ft** (au lieu de 2900 ft dans le profil SDVFR original)
- **Segment LFFF/OE → BEVRO stable** à 3100 ft
- **Descente uniquement à la fin** vers l'altitude du terrain de destination

### 4. Analyseur de Profils (`kml_analyzer.py`)
Outil d'analyse détaillée et de comparaison des profils KML.

#### Fonctionnalités :
- **Analyse détaillée** point par point avec changements d'altitude
- **Comparaison visuelle** entre profils original et corrigé
- **Détection des incohérences** dans les profils SDVFR

### 5. Module Utilitaire (`aviation_utils.py`)
Module de support avec conversions d'unités et API d'élévation.

#### Fonctionnalités :
- **Conversions d'unités** : mètres ↔ pieds, kilomètres ↔ miles nautiques
- **API d'élévation** : Open Elevation, USGS, Google Maps
- **Cache et gestion des limites** de taux de requêtes

## Résultats de la Correction

### Profil Original SDVFR (Problématique)
```
LFXU - LES MUREAUX        1400 ft  (devrait être altitude terrain ~79 ft)
LFFF/OE → BEVRO          -200 ft  (descente prématurée)
LFFU - CHATEAUNEUF        0 ft     (devrait être altitude terrain ~548 ft)
```

### Profil Corrigé
```
LFXU - LES MUREAUX        79 ft    ✓ Altitude du terrain (API)
LFFF/OE → BEVRO          stable   ✓ Pas de descente prématurée
BEVRO                     3100 ft  ✓ Maintient l'altitude de croisière
LFFU - CHATEAUNEUF        548 ft   ✓ Altitude du terrain (API)
```

## Amélirations Apportées

1. **Altitudes réalistes** : départ et arrivée aux altitudes du terrain réel
2. **Profils cohérents** : maintien des altitudes de croisière sur les segments appropriés
3. **Points de transition** : calcul automatique des points de montée/descente
4. **Unités aéronautiques** : pieds et miles nautiques pour la navigation
5. **API d'élévation** : récupération automatique des altitudes terrain
6. **Visualisation** : graphiques et comparaisons pour validation

## Fichiers de Test Générés

- `LFXU-LFFU-corrected-manual.kml` : Profil corrigé avec corrections spécifiques
- `comparison.png` : Comparaison visuelle original vs corrigé

## Utilisation Recommandée

Pour corriger un fichier KML SDVFR :

1. **Correction automatique** :
   ```bash
   python kml_altitude_corrector.py input.kml -o corrected.kml
   ```

2. **Visualisation du résultat** :
   ```bash
   python kml_altitude_viewer.py --summary corrected.kml
   ```

3. **Comparaison** :
   ```bash
   python kml_analyzer.py --compare input.kml corrected.kml -o comparison.png
   ```

4. **Pour des corrections spécifiques**, modifier le correcteur spécialisé selon les besoins du vol.