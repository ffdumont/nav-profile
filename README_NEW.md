# 🛩️ Nav-Profile - Suite d'Analyse de Navigation Aéronautique

Suite complète d'outils pour l'analyse de fichiers KML de navigation contre les données d'espace aérien français.

## 🏗️ Structure du Projet

```
nav-profile/
├── navpro/                          # 🛩️ Application NavPro principale
│   ├── navpro.py                   # Interface ligne de commande
│   ├── navpro_gui.py               # Interface graphique
│   ├── core/                       # Moteur d'analyse de vol
│   ├── data_processing/            # Traitement données AIXM
│   ├── utils/                      # Utilitaires généraux
│   └── visualization/              # Génération KML
│
├── altitude-correction/             # ✈️ Outils correction d'altitude
│   ├── kml_altitude_corrector.py   # Correcteur principal
│   ├── kml_altitude_viewer.py      # Visualiseur graphique
│   ├── aviation_utils.py           # Utilitaires aéronautiques
│   ├── kml_analyzer.py             # Analyseur de profils
│   └── lfxu_lffu_corrector.py     # Correcteur spécialisé
│
├── scripts/                         # 📋 Scripts de lancement
│   ├── navpro.bat / navpro.ps1     # Lanceurs NavPro
│   ├── kml_corrector.bat           # Lanceur correcteur KML
│   └── kml_viewer.bat              # Lanceur visualiseur KML
│
├── distribution/                    # 📦 Distribution et build
│   ├── build_scripts/              # Scripts de build
│   └── releases/                   # Packages de release
│
├── data/                           # 📁 Données de test
├── docs/                           # 📚 Documentation
└── README.md                       # Ce fichier
```

## 🚀 Démarrage Rapide

### NavPro - Analyse de Navigation

```bash
# Interface graphique
python navpro/navpro_gui.py

# Ligne de commande
./navpro.bat help
```

### Correction d'Altitude KML

```bash
# Corriger un fichier KML
./scripts/kml_corrector.bat input.kml -o output.kml

# Visualiser un profil d'altitude
./scripts/kml_viewer.bat flight.kml
```

## 📋 Fonctionnalités

### NavPro
- ✅ Analyse de fichiers KML de navigation
- ✅ Détection d'intersections avec l'espace aérien français
- ✅ Génération de rapports de conformité
- ✅ Interface graphique Windows

### Correction d'Altitude
- ✅ Correction des profils d'altitude SDVFR erronés
- ✅ Récupération automatique des altitudes terrain (API)
- ✅ Visualisation graphique des profils (unités aéronautiques)
- ✅ Convention altitude départ/arrivée = terrain + 1000 ft
- ✅ Calculs de montée/descente réalistes (500 ft/min)

## 📖 Documentation

- `altitude-correction/README_CORRECTION_KML.md` - Documentation correction KML
- `distribution/README_DIST.md` - Guide de distribution
- `docs/` - Documentation complète du projet

## 🛠️ Installation

1. Cloner le repository
2. Installer les dépendances : `pip install -r requirements.txt`
3. Lancer via les scripts dans `scripts/` ou directement

## 📝 License

Ce projet est développé pour l'analyse de navigation aéronautique en France.