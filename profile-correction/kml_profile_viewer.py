#!/usr/bin/env python3
"""
KML Profile Viewer
Creates proper flight profile charts with NM on X-axis, ft on Y-axis
Shows original profile with branch analysis overlay
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
from typing import List, Tuple, Optional, Dict
import argparse
import os

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from aviation_utils import UnitConverter


@dataclass
class ViewerPoint:
    """Simple point for visualization (no correction logic)"""
    name: str
    longitude: float
    latitude: float
    altitude: float
    
    def __str__(self):
        return f"{self.name} @ {UnitConverter.format_altitude(self.altitude)}"


class KMLProfileViewer:
    """KML profile viewer - displays any KML file without modification"""
    
    def __init__(self):
        pass
    
    def parse_kml_for_display(self, kml_file: str) -> List[ViewerPoint]:
        """Parse KML file and extract points for display only (no correction)"""
        try:
            tree = ET.parse(kml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"Warning: XML parsing error: {e}")
            return []
        
        namespaces = {
            'kml': 'http://www.opengis.net/kml/2.2',
            'gx': 'http://www.google.com/kml/ext/2.2'
        }
        points = []
        
        # Extract main navigation line coordinates
        navigation_coords = None
        for linestring in root.findall('.//kml:LineString', namespaces):
            coords_elem = linestring.find('kml:coordinates', namespaces)
            if coords_elem is not None:
                navigation_coords = coords_elem.text.strip()
                break
        
        if navigation_coords:
            # Parse navigation line coordinates  
            coords_list = navigation_coords.split(',')
            for i in range(0, len(coords_list), 3):
                if i + 2 < len(coords_list):
                    try:
                        lon = float(coords_list[i])
                        lat = float(coords_list[i + 1])
                        alt = float(coords_list[i + 2])
                        points.append(ViewerPoint(f"Point_{i//3}", lon, lat, alt))
                    except ValueError:
                        continue
        
        # Get point names from Placemarks
        placemark_names = []
        for placemark in root.findall('.//kml:Placemark', namespaces):
            name_elem = placemark.find('kml:name', namespaces)
            if name_elem is not None and name_elem.text != "Navigation":
                placemark_names.append(name_elem.text)
        
        # Associate names with points
        for i, point in enumerate(points):
            if i < len(placemark_names):
                point.name = placemark_names[i]
        
        return points
    
    def calculate_distance_nm(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great circle distance between two points in nautical miles"""
        lat1, lon1 = math.radians(lat1), math.radians(lon1)
        lat2, lon2 = math.radians(lat2), math.radians(lon2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        R_km = 6371.0
        distance_km = R_km * c
        return UnitConverter.km_to_nautical_miles(distance_km)
    
    def visualize_profile(self, kml_file: str, output_file: str = None, title: str = None):
        """
        Create flight profile visualization with branch analysis
        X-axis: Nautical Miles
        Y-axis: Feet
        """
        print(f"Visualizing flight profile: {kml_file}")
        
        # Parse KML for display
        points = self.parse_kml_for_display(kml_file)
        if not points:
            print("No points found in KML file")
            return
        
        # Calculate cumulative distances
        cumulative_distances = [0.0]
        for i in range(1, len(points)):
            prev_point = points[i-1]
            curr_point = points[i]
            dist = self.calculate_distance_nm(prev_point.latitude, prev_point.longitude, 
                                            curr_point.latitude, curr_point.longitude)
            cumulative_distances.append(cumulative_distances[-1] + dist)
        
        # Convert altitudes to feet 
        altitudes_ft = [UnitConverter.meters_to_feet(p.altitude) for p in points]
        names = [p.name for p in points]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Separate points into original waypoints and climb/descent points
        original_waypoints = []
        climb_descent_points = []
        original_distances = []
        climb_descent_distances = []
        original_altitudes = []
        climb_descent_altitudes = []
        
        for i, (name, alt_ft, dist) in enumerate(zip(names, altitudes_ft, cumulative_distances)):
            if name.startswith(("Climb_", "Descent_")):
                climb_descent_points.append(name)
                climb_descent_distances.append(dist)
                climb_descent_altitudes.append(alt_ft)
            else:
                original_waypoints.append(name)
                original_distances.append(dist)
                original_altitudes.append(alt_ft)
        
        # Plot main profile line
        ax.plot(cumulative_distances, altitudes_ft, 'b-', linewidth=2, 
               label='Flight Profile', alpha=0.7)
        ax.fill_between(cumulative_distances, 0, altitudes_ft, alpha=0.2, color='lightblue')
        
        # Plot original waypoints with labels (red markers)
        if original_distances:
            ax.scatter(original_distances, original_altitudes, 
                      color='red', s=100, zorder=5, label='Waypoints')
        
        # Plot climb/descent points without labels (different colors)
        if climb_descent_distances:
            climb_points_x = []
            climb_points_y = []
            descent_points_x = []
            descent_points_y = []
            
            for name, dist, alt in zip(climb_descent_points, climb_descent_distances, climb_descent_altitudes):
                if name.startswith("Climb_"):
                    climb_points_x.append(dist)
                    climb_points_y.append(alt)
                else:  # Descent
                    descent_points_x.append(dist)
                    descent_points_y.append(alt)
            
            if climb_points_x:
                ax.scatter(climb_points_x, climb_points_y, 
                          color='green', s=60, marker='^', zorder=5, label='Climb Points')
            if descent_points_x:
                ax.scatter(descent_points_x, descent_points_y, 
                          color='orange', s=60, marker='v', zorder=5, label='Descent Points')
        
        # Add waypoint labels with altitudes in feet (only for original waypoints)
        max_alt = max(altitudes_ft)
        min_alt = min(altitudes_ft)
        alt_range = max_alt - min_alt if max_alt != min_alt else 1000
        
        for i, (name, alt_ft, dist) in enumerate(zip(original_waypoints, original_altitudes, original_distances)):
            # Smart label positioning to avoid overlap
            if i % 2 == 0:
                label_y = alt_ft + alt_range * 0.08
                va = 'bottom'
            else:
                label_y = alt_ft - alt_range * 0.08
                va = 'top'
            
            # Create waypoint label with altitude in feet
            label_text = f"{name}\n{alt_ft:.0f} ft"
            
            ax.annotate(label_text, 
                       xy=(dist, alt_ft), 
                       xytext=(dist, label_y),
                       ha='center', va=va,
                       fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.8),
                       arrowprops=dict(arrowstyle='->', color='darkgray', lw=1))
        
        # Formatting
        ax.set_xlabel('Distance (Nautical Miles)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Altitude (Feet)', fontsize=14, fontweight='bold')
        
        if not title:
            title = f"Flight Profile - {os.path.basename(kml_file)}"
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Set reasonable axis limits
        y_padding = alt_range * 0.15 if alt_range > 0 else 500
        ax.set_ylim(max(0, min_alt - y_padding), max_alt + y_padding)
        
        # Add legend
        ax.legend(['Flight Profile'], loc='upper left')
        
        # Print basic flight info
        print(f"\n🛩️ FLIGHT PROFILE DISPLAY")
        print(f"{'='*50}")
        print(f"Flight: {os.path.basename(kml_file)}")
        print(f"Waypoints: {len(points)}")
        print(f"Total distance: {cumulative_distances[-1]:.1f} NM")
        print(f"Altitude range: {min_alt:.0f} - {max_alt:.0f} ft")
        print(f"{'='*50}")
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"\nProfile visualization saved: {output_file}")
        else:
            plt.show()
        
        plt.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='KML Profile Viewer')
    parser.add_argument('input_file', help='Input KML file to visualize')
    parser.add_argument('-o', '--output', help='Output PNG file (if not specified, shows interactive window)')
    parser.add_argument('-t', '--title', help='Custom title for the visualization')
    
    args = parser.parse_args()
    
    # Create viewer (no parameters needed for display-only viewer)
    viewer = KMLProfileViewer()
    
    # Generate visualization
    if args.output:
        # Save to specified file
        viewer.visualize_profile(args.input_file, args.output, args.title)
    else:
        # Show interactive window
        viewer.visualize_profile(args.input_file, None, args.title)


if __name__ == "__main__":
    main()