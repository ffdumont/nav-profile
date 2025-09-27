"""
Airspace Checker - Analyseur de profil de navigation et d'espace aérien

Airspace Checker est un outil d'analyse de profils de navigation aéronautique qui permet :
- L'analyse de fichiers KML de navigation
- La détection d'intersections avec l'espace aérien
- La génération de rapports de conformité
- L'interface graphique pour l'analyse interactive

## Modules

- `navpro.py` - Interface en ligne de commande (airchk)
- `navpro_gui.py` - Interface graphique utilisateur (Airspace Checker)
- `core/` - Moteur d'analyse des profils de vol
- `data_processing/` - Traitement des données AIXM
- `utils/` - Utilitaires généraux
- `visualization/` - Génération de visualisations KML
"""

__version__ = "1.2.1.2"