#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KML Color Configuration for Airspace Types
Defines colors for different airspace types and classes in KML generation
"""

# KML Colors in AABBGGRR format (Alpha, Blue, Green, Red)
# Note: KML uses AABBGGRR format, not the typical RRGGBB

KML_COLORS = {
    # Default color (grey) for unspecified airspace types
    'default': '40808080',  # 25% transparent grey
    
    # Red colors for Class A airspaces and restricted zones
    'class_A': '400000ff',  # 25% transparent red
    'R': '400000ff',        # Restricted areas - red
    'P': '400000ff',        # Prohibited areas - red
    
    # Blue colors for Class D airspaces (AABBGGRR: AA=40, BB=ff, GG=00, RR=00)
    'D': '40ff0000',        # Class D airspace - blue
    'D-OTHER': '40ff0000',  # Class D other - blue
    
    # Magenta/Purple colors for Class E airspaces (AABBGGRR: AA=40, BB=ff, GG=00, RR=ff)
    'E': '40ff00ff',        # Class E airspace - magenta
    
    # Green colors for RAS airspaces (AABBGGRR: AA=40, BB=00, GG=ff, RR=00)
    'RAS': '4000ff00',      # RAS airspace - green
    
    # You can add more specific colors here as needed
    # Examples of other colors:
    # 'TMA': '4000ff00',    # Green for Terminal Control Areas
    # 'CTR': '40ffff00',    # Yellow for Control Zones
    # 'CTA': '4000ffff',    # Cyan for Control Areas
}

# Color intensity/transparency settings
TRANSPARENCY = {
    'fill': 0x40,      # Fill transparency (25% opacity: 0x40)
    'line': 0xff,      # Line transparency (usually opaque)
}

# Line width for KML boundaries
LINE_WIDTH = 2

def get_airspace_color(airspace_type: str = None, airspace_class: str = None) -> str:
    """
    Get the appropriate KML color for an airspace based on its type and class
    
    Args:
        airspace_type (str): The airspace type (R, P, D, TMA, etc.)
        airspace_class (str): The airspace class (A, B, C, D, E, etc.)
    
    Returns:
        str: KML color string in AABBGGRR format
    """
    # Priority 1: Check for class A airspaces (should be red)
    if airspace_class and airspace_class.upper() == 'A':
        return KML_COLORS['class_A']
    
    # Priority 2: Check for class D airspaces (should be blue)
    if airspace_class and airspace_class.upper() == 'D':
        return KML_COLORS['D']
    
    # Priority 3: Check for class E airspaces (should be magenta)
    if airspace_class and airspace_class.upper() == 'E':
        return KML_COLORS['E']
    
    # Priority 4: Check for specific airspace types
    if airspace_type and airspace_type.upper() in KML_COLORS:
        return KML_COLORS[airspace_type.upper()]
    
    # Priority 5: Default grey color
    return KML_COLORS['default']

def get_line_color(fill_color: str) -> str:
    """
    Generate a line color based on fill color (usually with full opacity)
    
    Args:
        fill_color (str): Fill color in AABBGGRR format
    
    Returns:
        str: Line color in AABBGGRR format with full opacity
    """
    # Replace alpha channel with full opacity (ff)
    return 'ff' + fill_color[2:]

def get_color_info() -> dict:
    """
    Get information about all configured colors
    
    Returns:
        dict: Dictionary with color configuration info
    """
    return {
        'colors': KML_COLORS.copy(),
        'transparency': TRANSPARENCY.copy(),
        'line_width': LINE_WIDTH,
        'color_format': 'AABBGGRR (Alpha, Blue, Green, Red)'
    }

# Example usage and testing
if __name__ == "__main__":
    print("KML Color Configuration")
    print("=" * 40)
    
    # Test different airspace combinations
    test_cases = [
        ('TMA', 'A'),      # Should be red (class A)
        ('D', None),       # Should be blue (type D)
        ('R', None),       # Should be red (restricted)
        ('P', None),       # Should be red (prohibited)
        ('RAS', None),     # Should be green (RAS)
        ('TMA', 'C'),      # Should be grey (default)
        (None, None),      # Should be grey (default)
    ]
    
    for airspace_type, airspace_class in test_cases:
        color = get_airspace_color(airspace_type, airspace_class)
        line_color = get_line_color(color)
        print(f"Type: {airspace_type or 'None':>8} | Class: {airspace_class or 'None':>4} | Fill: {color} | Line: {line_color}")
    
    print(f"\nAvailable colors: {list(KML_COLORS.keys())}")