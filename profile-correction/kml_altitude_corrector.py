#!/usr/bin/env python3
"""
Module de correction des profils d'altitude KML SDVFR
Corrige les altitudes pour représenter un profil de navigation réaliste avec montées et descentes graduelles
"""

import xml.etree.ElementTree as ET
import re
import math
from typing import List, Tuple, Optional, Dict
from aviation_utils import UnitConverter, ElevationAPI, extract_airport_coordinates_from_kml


class KMLPoint:
    """Représente un point de navigation avec ses coordonnées et métadonnées"""
    
    def __init__(self, name: str, longitude: float, latitude: float, altitude: float):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.ground_altitude: Optional[float] = None  # Altitude du terrain (à définir manuellement)
    
    def __repr__(self):
        return f"KMLPoint({self.name}, lon={self.longitude:.6f}, lat={self.latitude:.6f}, alt={self.altitude:.1f}m)"


class AltitudeProfile:
    """Gère les profils d'altitude et les corrections de trajectoire"""
    
    def __init__(self, climb_rate: float = 500, descent_rate: float = 500):
        """
        Initialize altitude profile corrector
        
        Args:
            climb_rate: Taux de montée en ft/min (défaut: 500 ft/min)
            descent_rate: Taux de descente en ft/min (défaut: 500 ft/min)
        """
        self.climb_rate = climb_rate  # ft/min
        self.descent_rate = descent_rate  # ft/min
        self.ground_speed = 100  # vitesse sol en kts (défaut: 100 kt)
        
    def calculate_distance(self, p1: KMLPoint, p2: KMLPoint) -> float:
        """Calcule la distance orthodromique entre deux points en NM"""
        lat1, lon1 = math.radians(p1.latitude), math.radians(p1.longitude)
        lat2, lon2 = math.radians(p2.latitude), math.radians(p2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Rayon de la Terre en km, puis conversion en NM
        R_km = 6371.0
        distance_km = R_km * c
        return UnitConverter.km_to_nautical_miles(distance_km)
    
    def interpolate_point(self, p1: KMLPoint, p2: KMLPoint, fraction: float) -> Tuple[float, float]:
        """
        Interpole une position géographique entre deux points
        
        Args:
            p1: Point de départ
            p2: Point d'arrivée
            fraction: Fraction du chemin (0.0 = p1, 1.0 = p2)
            
        Returns:
            Tuple (longitude, latitude) du point interpolé
        """
        lon = p1.longitude + (p2.longitude - p1.longitude) * fraction
        lat = p1.latitude + (p2.latitude - p1.latitude) * fraction
        return lon, lat
    
    def calculate_climb_descent_points(self, segment_start: KMLPoint, segment_end: KMLPoint,
                                     start_altitude: float, target_altitude: float) -> List[Tuple[float, float, float]]:
        """
        Calcule les points intermédiaires pour une montée ou descente
        
        Args:
            segment_start: Point de début du segment
            segment_end: Point de fin du segment
            start_altitude: Altitude de départ en mètres
            target_altitude: Altitude cible en mètres
            
        Returns:
            Liste de tuples (longitude, latitude, altitude_en_mètres) des points intermédiaires
        """
        # Convertir les altitudes en pieds pour les calculs
        start_alt_ft = UnitConverter.meters_to_feet(start_altitude)
        target_alt_ft = UnitConverter.meters_to_feet(target_altitude)
        altitude_change = target_alt_ft - start_alt_ft
        
        if abs(altitude_change) < 50:  # Pas de changement significatif (moins de 50 ft)
            return []
        
        # Calculer la distance nécessaire pour la montée/descente
        rate = self.climb_rate if altitude_change > 0 else self.descent_rate
        time_needed = abs(altitude_change) / rate  # en minutes
        distance_needed = (self.ground_speed / 60) * time_needed  # en NM
        
        # Distance totale du segment en NM
        total_distance = self.calculate_distance(segment_start, segment_end)
        
        if distance_needed >= total_distance:
            # La montée/descente prend tout le segment
            return []
        
        # Calculer la fraction du segment utilisée pour la montée/descente
        fraction = distance_needed / total_distance
        
        # Point où la montée/descente se termine
        end_lon, end_lat = self.interpolate_point(segment_start, segment_end, fraction)
        
        # S'assurer que l'altitude cible n'est jamais négative
        safe_target_altitude = max(target_altitude, UnitConverter.feet_to_meters(100))  # Minimum 100 ft
        
        return [(end_lon, end_lat, safe_target_altitude)]


class KMLAltitudeCorrector:
    """Classe principale pour corriger les fichiers KML"""
    
    def __init__(self, climb_rate: float = 500, descent_rate: float = 500, api_key: Optional[str] = None):
        self.altitude_profile = AltitudeProfile(climb_rate, descent_rate)
        self.ground_altitudes: Dict[str, float] = {}
        self.cruise_altitudes: Dict[str, float] = {}  # Altitudes de croisière forcées
        self.elevation_api = ElevationAPI()
        self.api_key = api_key
    
    def set_ground_altitude(self, point_name: str, ground_altitude: float):
        """Définit l'altitude du terrain pour un point donné"""
        self.ground_altitudes[point_name] = ground_altitude
    
    def set_cruise_altitude(self, point_name: str, cruise_altitude: float):
        """Définit l'altitude de croisière forcée pour un point donné"""
        self.cruise_altitudes[point_name] = cruise_altitude
    
    def parse_kml(self, kml_file: str) -> Tuple[List[KMLPoint], str]:
        """
        Parse un fichier KML et extrait les points de navigation
        
        Returns:
            Tuple (liste des points, contenu XML original)
        """
        tree = ET.parse(kml_file)
        root = tree.getroot()
        
        # Gérer les namespaces KML
        namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        points = []
        
        # Extraire la ligne de navigation principale
        navigation_coords = None
        for linestring in root.findall('.//kml:LineString', namespaces):
            coords_elem = linestring.find('kml:coordinates', namespaces)
            if coords_elem is not None:
                navigation_coords = coords_elem.text.strip()
                break
        
        if navigation_coords:
            # Parser les coordonnées de la ligne de navigation
            coords_list = navigation_coords.split(',')
            for i in range(0, len(coords_list), 3):
                if i + 2 < len(coords_list):
                    try:
                        lon = float(coords_list[i])
                        lat = float(coords_list[i + 1])
                        alt = float(coords_list[i + 2])
                        points.append(KMLPoint(f"Point_{i//3}", lon, lat, alt))
                    except ValueError:
                        continue
        
        # Récupérer les noms des points depuis les Placemark
        placemark_names = []
        for placemark in root.findall('.//kml:Placemark', namespaces):
            name_elem = placemark.find('kml:name', namespaces)
            if name_elem is not None and name_elem.text != "Navigation":
                placemark_names.append(name_elem.text)
        
        # Associer les noms aux points
        for i, point in enumerate(points):
            if i < len(placemark_names):
                point.name = placemark_names[i]
        
        # Lire le fichier original comme string pour les modifications
        with open(kml_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        return points, original_content
    
    def correct_altitude_profile(self, points: List[KMLPoint]) -> List[Tuple[str, float, float, float]]:
        """
        Corrige le profil d'altitude et génère les points intermédiaires
        
        Returns:
            Liste de tuples (nom, longitude, latitude, altitude) avec points corrigés et intermédiaires
        """
        if len(points) < 2:
            return [(p.name, p.longitude, p.latitude, p.altitude) for p in points]

        corrected_points = []
        # Garder trace des altitudes corrigées pour chaque point
        corrected_altitudes = {}
        
        for i in range(len(points)):
            current_point = points[i]
            
            if i == 0:  # Point de départ
                ground_alt = self.ground_altitudes.get(current_point.name, 100.0)  # défaut 100m
                # Convention : départ à terrain + 1000 ft
                departure_alt = ground_alt + UnitConverter.feet_to_meters(1000)
                corrected_altitudes[current_point.name] = departure_alt
                corrected_points.append((current_point.name, current_point.longitude, 
                                       current_point.latitude, departure_alt))
                
                # Calculer la montée vers l'altitude de croisière du premier segment
                if i + 1 < len(points):
                    next_point = points[i + 1]
                    # L'altitude cible est celle du point actuel dans le KML original (altitude de croisière)
                    target_altitude = current_point.altitude
                    
                    climb_points = self.altitude_profile.calculate_climb_descent_points(
                        current_point, next_point, departure_alt, target_altitude
                    )
                    
                    for j, (lon, lat, alt) in enumerate(climb_points):
                        corrected_points.append((f"End_Climb_{i}_{j}", lon, lat, alt))
            
            elif i == len(points) - 1:  # Point d'arrivée
                ground_alt = self.ground_altitudes.get(current_point.name, 200.0)  # défaut 200m
                # Convention : arrivée à terrain + 1000 ft
                arrival_alt = ground_alt + UnitConverter.feet_to_meters(1000)
                corrected_altitudes[current_point.name] = arrival_alt
                
                # Calculer la descente depuis l'altitude CORRIGÉE du point précédent vers l'altitude terrain + 1000ft
                prev_point = points[i - 1]
                prev_corrected_alt = corrected_altitudes.get(prev_point.name, prev_point.altitude)
                descent_points = self.altitude_profile.calculate_climb_descent_points(
                    prev_point, current_point, prev_corrected_alt, arrival_alt
                )
                
                for j, (lon, lat, alt) in enumerate(descent_points):
                    corrected_points.append((f"Start_Descent_{i-1}_{j}", lon, lat, alt))
                
                # Point d'arrivée à terrain + 1000 ft
                corrected_points.append((current_point.name, current_point.longitude, 
                                       current_point.latitude, arrival_alt))
            
            else:  # Points intermédiaires
                # Utiliser l'altitude de croisière forcée si définie, sinon utiliser celle du KML
                cruise_alt = self.cruise_altitudes.get(current_point.name, current_point.altitude)
                corrected_altitudes[current_point.name] = cruise_alt
                
                # Le point garde son altitude de croisière (forcée ou originale)
                corrected_points.append((current_point.name, current_point.longitude, 
                                       current_point.latitude, cruise_alt))
                
                # Vérifier s'il y a un changement d'altitude vers le prochain point
                if i + 1 < len(points):
                    next_point = points[i + 1]
                    next_cruise_alt = self.cruise_altitudes.get(next_point.name, next_point.altitude)
                    
                    # Si changement d'altitude significatif, ajouter des points de transition
                    if abs(cruise_alt - next_cruise_alt) > 10:  # > 10m de différence
                        climb_desc_points = self.altitude_profile.calculate_climb_descent_points(
                            current_point, next_point, cruise_alt, next_cruise_alt
                        )
                        
                        for j, (lon, lat, alt) in enumerate(climb_desc_points):
                            if next_cruise_alt > cruise_alt:
                                corrected_points.append((f"End_Climb_{i}_{j}", lon, lat, alt))
                            else:
                                corrected_points.append((f"Start_Descent_{i}_{j}", lon, lat, alt))
        
        return corrected_points

    def generate_corrected_kml(self, original_content: str, corrected_points: List[Tuple[str, float, float, float]]) -> str:
        """
        Génère le contenu KML corrigé avec les nouveaux points d'altitude
        """
        # Générer les nouvelles coordonnées pour la LineString
        new_coords = []
        new_placemarks = []
        
        for name, lon, lat, alt in corrected_points:
            new_coords.append(f"{lon},{lat},{alt}")
            
            # Créer un Placemark pour les points intermédiaires s'ils n'existent pas
            if name.startswith(("End_Climb_", "Start_Descent_")):
                new_placemarks.append(f'''
                <Placemark>
                    <name>{name}</name>
                    <visibility>0</visibility>
                    <description>Point de transition d'altitude</description>
                    <styleUrl>#msn_ylw-pushpin0</styleUrl>
                    <Point>
                        <extrude>1</extrude>
                        <altitudeMode>absolute</altitudeMode>
                        <gx:drawOrder>1</gx:drawOrder>
                        <coordinates>{lon},{lat},{alt},</coordinates>
                    </Point>
                </Placemark>
                ''')
        
        new_coordinates_string = ",".join(new_coords)
        
        # Remplacer les coordonnées de navigation
        coord_pattern = r'<coordinates>[^<]*</coordinates>'
        new_content = re.sub(coord_pattern, f'<coordinates>{new_coordinates_string}</coordinates>', 
                           original_content, count=1)
        
        # Mettre à jour les coordonnées des points existants
        for name, lon, lat, alt in corrected_points:
            if not name.startswith(("End_Climb_", "Start_Descent_")) and not name.endswith("_CRUISE"):
                # Pattern pour trouver le Placemark correspondant et mettre à jour ses coordonnées
                placemark_pattern = rf'(<Placemark>.*?<name>{re.escape(name)}</name>.*?<coordinates>)[^<]*(</coordinates>.*?</Placemark>)'
                replacement = rf'\g<1>{lon},{lat},{alt},\g<2>'
                new_content = re.sub(placemark_pattern, replacement, new_content, flags=re.DOTALL)
        
        # Ajouter les nouveaux placemarks avant la fermeture du Folder Points
        if new_placemarks:
            folder_end_pattern = r'(</Folder>\s*</Document>)'
            placemarks_text = "\n".join(new_placemarks)
            new_content = re.sub(folder_end_pattern, placemarks_text + r'\n\g<1>', new_content)
        
        return new_content
    
    def correct_kml_file(self, input_file: str, output_file: str, ground_altitudes: Dict[str, float] = None):
        """
        Fonction principale pour corriger un fichier KML
        
        Args:
            input_file: Chemin du fichier KML d'entrée
            output_file: Chemin du fichier KML de sortie corrigé
            ground_altitudes: Dictionnaire des altitudes du terrain {nom_point: altitude} (optionnel)
        """
        # Parser le KML
        points, original_content = self.parse_kml(input_file)
        
        print(f"Points extraits du fichier {input_file}:")
        for point in points:
            print(f"  {point.name}: {UnitConverter.format_altitude(point.altitude)} " +
                  f"({point.longitude:.6f}, {point.latitude:.6f})")
        
        # Récupérer automatiquement les altitudes du terrain si pas fournies
        if not ground_altitudes:
            print("\nRécupération automatique des altitudes du terrain...")
            
            # Extraire les coordonnées des aéroports depuis le KML
            airport_coords = extract_airport_coordinates_from_kml(original_content)
            
            if airport_coords:
                print(f"Aéroports détectés: {list(airport_coords.keys())}")
                ground_altitudes = self.elevation_api.get_elevation_for_airports(
                    airport_coords, self.api_key)
            else:
                # Fallback : utiliser le premier et dernier point
                if len(points) >= 2:
                    first_point = points[0]
                    last_point = points[-1]
                    
                    coords = {
                        first_point.name: (first_point.latitude, first_point.longitude),
                        last_point.name: (last_point.latitude, last_point.longitude)
                    }
                    
                    ground_altitudes = self.elevation_api.get_elevation_for_airports(
                        coords, self.api_key)
        
        # Définir les altitudes du terrain
        if ground_altitudes:
            for point_name, altitude in ground_altitudes.items():
                self.set_ground_altitude(point_name, altitude)
                print(f"Altitude du terrain pour {point_name}: {UnitConverter.format_altitude(altitude)}")
        
        # Corriger les altitudes
        corrected_points = self.correct_altitude_profile(points)
        
        print(f"\nProfil d'altitude corrigé:")
        for name, lon, lat, alt in corrected_points:
            print(f"  {name}: {UnitConverter.format_altitude(alt)}")
        
        # Générer le KML corrigé
        corrected_content = self.generate_corrected_kml(original_content, corrected_points)
        
        # Sauvegarder le fichier corrigé
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(corrected_content)
        
        print(f"\nFichier KML corrigé sauvegardé: {output_file}")
        
        # Afficher un résumé des distances
        self._print_distance_summary(corrected_points)
    
    def _print_distance_summary(self, corrected_points: List[Tuple[str, float, float, float]]):
        """Affiche un résumé des distances entre les points principaux"""
        print(f"\n{'='*60}")
        print("RÉSUMÉ DES DISTANCES ET ALTITUDES")
        print(f"{'='*60}")
        
        # Filtrer pour ne garder que les points principaux (pas les points intermédiaires ni les points de croisière)
        main_points = [(name, lon, lat, alt) for name, lon, lat, alt in corrected_points 
                      if not name.startswith(('End_Climb_', 'Start_Descent_')) and not name.endswith('_CRUISE')]
        
        if len(main_points) < 2:
            return
        
        total_distance = 0
        
        print(f"{'Point':<30} {'Dist. cumulée':<15} {'Altitude':<15}")
        print("-" * 60)
        
        for i, (name, lon, lat, alt) in enumerate(main_points):
            if i == 0:
                distance = 0
            else:
                # Calculer la distance depuis le point précédent
                prev_point = main_points[i-1]
                p1 = KMLPoint("temp1", prev_point[1], prev_point[2], 0)
                p2 = KMLPoint("temp2", lon, lat, 0)
                distance = self.altitude_profile.calculate_distance(p1, p2)
                total_distance += distance
            
            print(f"{name:<30} {UnitConverter.format_distance(UnitConverter.nautical_miles_to_km(total_distance)):<15} {UnitConverter.format_altitude(alt):<15}")
        
        print("-" * 60)
        print(f"{'TOTAL:':<30} {UnitConverter.format_distance(UnitConverter.nautical_miles_to_km(total_distance)):<15}")
        print(f"{'='*60}")


def main():
    """Fonction principale pour tester le module"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Corriger les profils d\'altitude d\'un fichier KML SDVFR')
    parser.add_argument('input_file', help='Fichier KML d\'entrée')
    parser.add_argument('-o', '--output', help='Fichier KML de sortie (défaut: input_file_corrected.kml)')
    parser.add_argument('--climb-rate', type=float, default=500, help='Taux de montée en ft/min (défaut: 500)')
    parser.add_argument('--descent-rate', type=float, default=500, help='Taux de descente en ft/min (défaut: 500)')
    parser.add_argument('--api-key', help='Clé API Google pour l\'élévation (optionnelle)')
    
    args = parser.parse_args()
    
    # Définir le fichier de sortie si pas spécifié
    if not args.output:
        base_name = os.path.splitext(args.input_file)[0]
        args.output = f"{base_name}_corrected.kml"
    
    # Créer le correcteur et corriger le fichier
    corrector = KMLAltitudeCorrector(args.climb_rate, args.descent_rate, args.api_key)
    corrector.correct_kml_file(args.input_file, args.output)


if __name__ == "__main__":
    main()