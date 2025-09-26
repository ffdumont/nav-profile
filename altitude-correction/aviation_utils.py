#!/usr/bin/env python3
"""
Module utilitaire pour les conversions d'unités et l'API d'élévation
"""

import requests
import math
from typing import Optional, Dict, Tuple
import time


class UnitConverter:
    """Classe pour les conversions d'unités aéronautiques"""
    
    @staticmethod
    def meters_to_feet(meters: float) -> float:
        """Convertit des mètres en pieds"""
        return meters * 3.28084
    
    @staticmethod
    def feet_to_meters(feet: float) -> float:
        """Convertit des pieds en mètres"""
        return feet / 3.28084
    
    @staticmethod
    def km_to_nautical_miles(km: float) -> float:
        """Convertit des kilomètres en miles nautiques"""
        return km / 1.852
    
    @staticmethod
    def nautical_miles_to_km(nm: float) -> float:
        """Convertit des miles nautiques en kilomètres"""
        return nm * 1.852
    
    @staticmethod
    def format_altitude(altitude_meters: float, unit: str = 'ft') -> str:
        """Formate une altitude avec l'unité appropriée"""
        if unit == 'ft':
            alt_ft = UnitConverter.meters_to_feet(altitude_meters)
            return f"{alt_ft:.0f} ft"
        else:
            return f"{altitude_meters:.0f} m"
    
    @staticmethod
    def format_distance(distance_km: float, unit: str = 'NM') -> str:
        """Formate une distance avec l'unité appropriée"""
        if unit == 'NM':
            dist_nm = UnitConverter.km_to_nautical_miles(distance_km)
            return f"{dist_nm:.1f} NM"
        else:
            return f"{distance_km:.1f} km"


class ElevationAPI:
    """Classe pour récupérer les altitudes du terrain via API"""
    
    def __init__(self):
        self.cache: Dict[Tuple[float, float], float] = {}
        self.rate_limit_delay = 0.1  # 100ms entre les requêtes
        self.last_request_time = 0
    
    def _respect_rate_limit(self):
        """Respecte la limite de taux de requêtes"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def get_elevation_open_elevation(self, latitude: float, longitude: float) -> Optional[float]:
        """
        Récupère l'altitude du terrain via l'API Open Elevation
        
        Args:
            latitude: Latitude en degrés décimaux
            longitude: Longitude en degrés décimaux
            
        Returns:
            Altitude du terrain en mètres, ou None en cas d'erreur
        """
        # Vérifier le cache
        cache_key = (round(latitude, 6), round(longitude, 6))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        self._respect_rate_limit()
        
        try:
            url = "https://api.open-elevation.com/api/v1/lookup"
            params = {
                'locations': f"{latitude},{longitude}"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                elevation = data['results'][0].get('elevation')
                if elevation is not None:
                    self.cache[cache_key] = float(elevation)
                    return float(elevation)
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'altitude via Open Elevation: {e}")
        
        return None
    
    def get_elevation_usgs(self, latitude: float, longitude: float) -> Optional[float]:
        """
        Récupère l'altitude du terrain via l'API USGS (pour les USA uniquement)
        
        Args:
            latitude: Latitude en degrés décimaux
            longitude: Longitude en degrés décimaux
            
        Returns:
            Altitude du terrain en mètres, ou None en cas d'erreur
        """
        # Vérifier le cache
        cache_key = (round(latitude, 6), round(longitude, 6))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        self._respect_rate_limit()
        
        try:
            url = "https://nationalmap.gov/epqs/pqs.php"
            params = {
                'x': longitude,
                'y': latitude,
                'units': 'Meters',
                'output': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'USGS_Elevation_Point_Query_Service' in data:
                result = data['USGS_Elevation_Point_Query_Service']
                elevation = result.get('Elevation_Query', {}).get('Elevation')
                if elevation is not None and elevation != -1000000:
                    self.cache[cache_key] = float(elevation)
                    return float(elevation)
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'altitude via USGS: {e}")
        
        return None
    
    def get_elevation_google(self, latitude: float, longitude: float, api_key: str) -> Optional[float]:
        """
        Récupère l'altitude du terrain via l'API Google Elevation
        Nécessite une clé API Google
        
        Args:
            latitude: Latitude en degrés décimaux
            longitude: Longitude en degrés décimaux
            api_key: Clé API Google
            
        Returns:
            Altitude du terrain en mètres, ou None en cas d'erreur
        """
        # Vérifier le cache
        cache_key = (round(latitude, 6), round(longitude, 6))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        self._respect_rate_limit()
        
        try:
            url = "https://maps.googleapis.com/maps/api/elevation/json"
            params = {
                'locations': f"{latitude},{longitude}",
                'key': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                elevation = data['results'][0].get('elevation')
                if elevation is not None:
                    self.cache[cache_key] = float(elevation)
                    return float(elevation)
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'altitude via Google: {e}")
        
        return None
    
    def get_elevation(self, latitude: float, longitude: float, api_key: Optional[str] = None) -> Optional[float]:
        """
        Récupère l'altitude du terrain en essayant plusieurs APIs
        
        Args:
            latitude: Latitude en degrés décimaux
            longitude: Longitude en degrés décimaux
            api_key: Clé API Google (optionnelle)
            
        Returns:
            Altitude du terrain en mètres, ou None en cas d'erreur
        """
        print(f"Récupération de l'altitude pour {latitude:.6f}, {longitude:.6f}")
        
        # Essayer d'abord Open Elevation (gratuit)
        elevation = self.get_elevation_open_elevation(latitude, longitude)
        if elevation is not None:
            print(f"  -> {elevation:.1f}m (Open Elevation)")
            return elevation
        
        # Si on a une clé API Google, l'essayer
        if api_key:
            elevation = self.get_elevation_google(latitude, longitude, api_key)
            if elevation is not None:
                print(f"  -> {elevation:.1f}m (Google)")
                return elevation
        
        # En dernier recours, essayer USGS (USA uniquement)
        elevation = self.get_elevation_usgs(latitude, longitude)
        if elevation is not None:
            print(f"  -> {elevation:.1f}m (USGS)")
            return elevation
        
        print(f"  -> Échec de récupération de l'altitude")
        return None
    
    def get_elevation_for_airports(self, airport_codes: Dict[str, Tuple[float, float]], 
                                 api_key: Optional[str] = None) -> Dict[str, float]:
        """
        Récupère les altitudes pour plusieurs aéroports
        
        Args:
            airport_codes: Dictionnaire {code_aéroport: (latitude, longitude)}
            api_key: Clé API Google (optionnelle)
            
        Returns:
            Dictionnaire {code_aéroport: altitude_en_mètres}
        """
        altitudes = {}
        
        for airport_code, (lat, lon) in airport_codes.items():
            print(f"\nRécupération de l'altitude pour {airport_code}")
            elevation = self.get_elevation(lat, lon, api_key)
            if elevation is not None:
                altitudes[airport_code] = elevation
            else:
                # Valeurs par défaut si l'API échoue
                default_elevations = {
                    'LFXU': 100.0,  # Les Mureaux - environ 100m
                    'LFFU': 200.0,  # Châteauneuf-sur-Cher - environ 200m
                }
                altitudes[airport_code] = default_elevations.get(airport_code, 150.0)
                print(f"  -> Utilisation de l'altitude par défaut: {altitudes[airport_code]:.1f}m")
        
        return altitudes


def extract_airport_coordinates_from_kml(kml_content: str) -> Dict[str, Tuple[float, float]]:
    """
    Extrait les coordonnées des aéroports depuis le contenu KML
    
    Args:
        kml_content: Contenu du fichier KML
        
    Returns:
        Dictionnaire {nom_aéroport: (latitude, longitude)}
    """
    import xml.etree.ElementTree as ET
    import re
    
    airports = {}
    
    try:
        root = ET.fromstring(kml_content)
        namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        # Rechercher les Placemark qui correspondent à des aéroports (commencent par LF)
        for placemark in root.findall('.//kml:Placemark', namespaces):
            name_elem = placemark.find('kml:name', namespaces)
            if name_elem is not None:
                name = name_elem.text
                
                # Vérifier si c'est un aéroport (commence par LF suivi de 2 lettres)
                if re.match(r'LF[A-Z]{2}', name):
                    point_elem = placemark.find('.//kml:coordinates', namespaces)
                    if point_elem is not None:
                        coords = point_elem.text.strip().rstrip(',').split(',')
                        if len(coords) >= 2:
                            try:
                                lon, lat = float(coords[0]), float(coords[1])
                                airports[name] = (lat, lon)
                            except ValueError:
                                continue
    
    except Exception as e:
        print(f"Erreur lors de l'extraction des coordonnées d'aéroports: {e}")
    
    return airports


if __name__ == "__main__":
    # Test des conversions d'unités
    print("Tests des conversions d'unités:")
    print(f"1000m = {UnitConverter.format_altitude(1000)}")
    print(f"100km = {UnitConverter.format_distance(100)}")
    
    # Test de l'API d'élévation
    print("\nTest de l'API d'élévation:")
    api = ElevationAPI()
    
    # Test avec les coordonnées de Les Mureaux (LFXU)
    elevation = api.get_elevation(48.998611, 1.941667)
    if elevation:
        print(f"Altitude Les Mureaux: {elevation:.1f}m ({UnitConverter.format_altitude(elevation)})")