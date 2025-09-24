#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NavPro - Navigation Profile Command Line Tool
Access airspace services and generate KML volumes with consistent subcommand structure
"""

import argparse
import sys
import os
from pathlib import Path

# Add production directory to path
sys.path.append(str(Path(__file__).parent / "production"))

from visualization.kml_generator import KMLVolumeService


def create_parser():
    """Create the main argument parser with subcommands"""
    parser = argparse.ArgumentParser(
        prog="navpro",
        description="NavPro - Navigation Profile Command Line Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  navpro list --name "CHEVREUSE"                    # List airspaces matching pattern
  navpro list --profile flight.kml                  # List relevant airspaces crossed (filtered)
  navpro list --profile flight.kml --filter-types ""     # List ALL airspaces crossed (no filter)
  navpro list --profile flight.kml --corridor-height 2000 # Custom corridor ±2000ft
  navpro list --id 4749                             # Show details for specific ID
  navpro list --all                                 # List all airspaces (limited)
  
  navpro generate --id 4749                         # Generate KML for single airspace  
  navpro generate --profile flight.kml              # Generate KML for relevant airspaces crossed
  navpro generate --profile flight.kml --filter-types "SECTOR"  # Filter only SECTOR types
  navpro generate --name "CHEVREUSE"                # Generate KML for all matching
  navpro generate --ids 4749 4750 4751              # Generate combined KML
  
  navpro stats                             # Show database statistics
  navpro help                              # Show detailed help

NavPro provides professional navigation services including:
- Airspace search and listing with flight path analysis
- 3D KML volume visualization  
- Flight path airspace crossing analysis with 3D corridors
- Chronological crossing detection for flight planning
- TMAs, RAS, and Restricted zone detection
- Batch operations and automation
        """
    )
    
    # Global options
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Verbose output with detailed information'
    )
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Quiet mode - minimal output'
    )
    
    # Create subparsers
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # LIST subcommand
    list_parser = subparsers.add_parser(
        'list',
        help='List and search airspaces',
        description='Search and list airspaces by various criteria or analyze flight paths'
    )
    list_group = list_parser.add_mutually_exclusive_group(required=False)
    list_group.add_argument(
        '--name', type=str,
        help='List airspaces matching name pattern'
    )
    list_group.add_argument(
        '--id', type=int,
        help='Show detailed information for specific airspace ID'
    )
    list_group.add_argument(
        '--type', type=str,
        help='List airspaces of specific type (RAS, TMA, CTR, etc.)'
    )
    list_group.add_argument(
        '--all', action='store_true',
        help='List all airspaces (limited to first 100)'
    )
    
    list_parser.add_argument(
        '--profile', type=str,
        help='Analyze KML flight path and list airspaces chronologically crossed'
    )
    list_parser.add_argument(
        '--limit', '-l', type=int, default=50,
        help='Limit number of results (default: 50)'
    )
    list_parser.add_argument(
        '--summary', '-s', action='store_true',
        help='Show compact summary format'
    )
    list_parser.add_argument(
        '--corridor-height', type=int, default=1000,
        help='Vertical corridor height in feet (±altitude, default: 1000) - used with --profile'
    )
    list_parser.add_argument(
        '--corridor-width', type=float, default=10.0,
        help='Horizontal corridor width in nautical miles (±track, default: 10.0) - used with --profile'
    )
    list_parser.add_argument(
        '--database', type=str, default='data/airspaces.db',
        help='Airspace database path (default: data/airspaces.db) - used with --profile'
    )
    list_parser.add_argument(
        '--filter-types', type=str, default='SECTOR,FIR,D-OTHER',
        help='Comma-separated list of airspace types to filter out (default: SECTOR,FIR,D-OTHER) - used with --profile'
    )
    
    # GENERATE subcommand
    gen_parser = subparsers.add_parser(
        'generate',
        help='Generate KML volumes',
        description='Generate 3D KML volumes for airspaces or flight path crossings'
    )
    gen_group = gen_parser.add_mutually_exclusive_group(required=False)
    gen_group.add_argument(
        '--id', type=int,
        help='Generate KML for single airspace ID'
    )
    gen_group.add_argument(
        '--ids', type=int, nargs='+',
        help='Generate combined KML for multiple airspace IDs'
    )
    gen_group.add_argument(
        '--name', type=str,
        help='Generate KML for all airspaces matching name pattern'
    )
    gen_group.add_argument(
        '--type', type=str,
        help='Generate KML for all airspaces of specific type'
    )
    
    gen_parser.add_argument(
        '--profile', type=str,
        help='Analyze KML flight path and generate KML volumes for airspaces crossed'
    )
    gen_parser.add_argument(
        '--output', '-o', type=str,
        help='Output filename (default: auto-generated)'
    )
    gen_parser.add_argument(
        '--directory', '-d', type=str, default='.',
        help='Output directory (default: current directory)'
    )
    gen_parser.add_argument(
        '--individual', action='store_true',
        help='Generate individual files even for multiple airspaces'
    )
    gen_parser.add_argument(
        '--combined-only', action='store_true',
        help='Generate only combined file for multiple airspaces'
    )
    gen_parser.add_argument(
        '--corridor-height', type=int, default=1000,
        help='Vertical corridor height in feet (±altitude, default: 1000) - used with --profile'
    )
    gen_parser.add_argument(
        '--corridor-width', type=float, default=10.0,
        help='Horizontal corridor width in nautical miles (±track, default: 10.0) - used with --profile'
    )
    gen_parser.add_argument(
        '--database', type=str, default='data/airspaces.db',
        help='Airspace database path (default: data/airspaces.db) - used with --profile'
    )
    gen_parser.add_argument(
        '--filter-types', type=str, default='SECTOR,FIR,D-OTHER',
        help='Comma-separated list of airspace types to filter out (default: SECTOR,FIR,D-OTHER) - used with --profile'
    )
    
    # STATS subcommand
    stats_parser = subparsers.add_parser(
        'stats',
        help='Show database statistics',
        description='Display database statistics and health information'
    )
    stats_parser.add_argument(
        '--detailed', action='store_true',
        help='Show detailed statistics'
    )
    
    # HELP subcommand
    help_parser = subparsers.add_parser(
        'help',
        help='Show detailed help',
        description='Show comprehensive help and examples'
    )
    help_parser.add_argument(
        'topic', nargs='?', choices=['list', 'generate', 'stats'],
        help='Show help for specific command'
    )
    
    return parser


def cmd_list(args, kml_service):
    """Handle list subcommand"""
    
    # Check if --profile option is used
    if args.profile:
        return cmd_list_profile(args)
    
    # Check if any search criteria is provided
    if not (args.name or args.id or args.type or args.all):
        print("❌ Error: Must specify search criteria (--name, --id, --type, or --all)")
        return
    
    if not args.quiet:
        print("🔍 Searching airspaces...")
    
    results = []
    
    if args.name:
        results = kml_service.get_airspace_by_name(args.name)
        search_desc = f"matching pattern '{args.name}'"
    elif args.id:
        # Get single airspace details
        all_airspaces = kml_service.get_airspace_by_name("")  # Get all
        result = next((a for a in all_airspaces if a['id'] == args.id), None)
        results = [result] if result else []
        search_desc = f"with ID {args.id}"
    elif args.type:
        # Get airspaces by type (need to implement this in service)
        all_airspaces = kml_service.get_airspace_by_name("")
        results = [a for a in all_airspaces if a.get('code_type', '').upper() == args.type.upper()]
        search_desc = f"of type '{args.type}'"
    elif args.all:
        all_airspaces = kml_service.get_airspace_by_name("")
        results = all_airspaces[:args.limit]
        search_desc = f"(showing first {args.limit})"
    
    if not results:
        print(f"❌ No airspaces found {search_desc}")
        return
    
    # Apply limit
    if len(results) > args.limit:
        results = results[:args.limit]
        truncated = True
    else:
        truncated = False
    
    if not args.quiet:
        print(f"✅ Found {len(results)} airspace(s) {search_desc}")
        if truncated:
            print(f"   (Limited to {args.limit} results)")
        print()
    
    # Display results
    if args.summary:
        # Compact summary format
        for airspace in results:
            geometry_info = ""
            try:
                geometry_data = kml_service._get_airspace_geometry(airspace['id'])
                if geometry_data:
                    geometry_info = f" [Geometry: {len(geometry_data)} components]"
                else:
                    geometry_info = " [No geometry]"
            except:
                geometry_info = " [Geometry error]"
            
            alt_info = ""
            if airspace.get('max_altitude'):
                alt_info = f" | {airspace['min_altitude']}-{airspace['max_altitude']} {airspace.get('max_altitude_unit', 'FT')}"
            
            print(f"{airspace['id']:>6} | {airspace.get('code_type', 'Unknown'):>6} | {airspace['name']:<40}{alt_info}{geometry_info}")
    else:
        # Detailed format
        for i, airspace in enumerate(results):
            print(f"🏷️  {airspace['name']} (ID: {airspace['id']})")
            print(f"   Type: {airspace.get('code_type', 'Unknown')} | Class: {airspace.get('airspace_class', 'Unknown')}")
            
            # Altitude information
            min_alt = airspace.get('min_altitude', 'N/A')
            max_alt = airspace.get('max_altitude', 'N/A')
            min_unit = airspace.get('min_altitude_unit', '')
            max_unit = airspace.get('max_altitude_unit', '')
            print(f"   Altitude: {min_alt} {min_unit} to {max_alt} {max_unit}")
            
            # Geometry information
            if args.verbose:
                try:
                    geometry_data = kml_service._get_airspace_geometry(airspace['id'])
                    if geometry_data:
                        print(f"   Geometry: {len(geometry_data)} component(s)")
                        for j, geom in enumerate(geometry_data):
                            if geom['type'] == 'circle':
                                print(f"     - Circle: radius {geom['radius_km']} km")
                            elif geom['type'] == 'polygon':
                                vertex_count = len(geom.get('vertices', []))
                                print(f"     - Polygon: {vertex_count} vertices")
                    else:
                        print(f"   Geometry: ⚠️  No geometry data")
                except Exception as e:
                    print(f"   Geometry: ❌ Error: {e}")
                    
                # Operating information
                if airspace.get('operating_hours'):
                    print(f"   Hours: {airspace['operating_hours']}")
                if airspace.get('operating_remarks'):
                    print(f"   Remarks: {airspace['operating_remarks'][:100]}...")
                    
            print()


def cmd_list_profile(args):
    """Handle list --profile subcommand for flight path analysis"""
    from core.flight_analyzer import FlightProfileAnalyzer
    
    if not args.profile:
        print("❌ Error: --profile requires KML flight path file")
        return
    
    kml_file = args.profile
    if not os.path.exists(kml_file):
        print(f"❌ Error: KML file not found: {kml_file}")
        return
    
    print(f"🛩️ Analyzing flight path: {os.path.basename(kml_file)}")
    print(f"   Corridor: ±{args.corridor_height} ft, ±{args.corridor_width} NM")
    print()
    
    try:
        # Initialize analyzer
        analyzer = FlightProfileAnalyzer(
            args.database, 
            args.corridor_height, 
            args.corridor_width
        )
        
        # Get chronological crossings
        crossings = analyzer.get_chronological_crossings(kml_file, sample_distance_km=5.0)
        
        if not crossings:
            print("❌ No airspace crossings found")
            return
            
        # Apply type filtering
        filter_types = set()
        if args.filter_types:
            filter_types = {t.strip().upper() for t in args.filter_types.split(',') if t.strip()}
        
        # Filter out unwanted airspace types
        filtered_crossings = []
        filtered_count = 0
        for crossing in crossings:
            airspace = crossing['airspace']
            code_type = airspace.get('code_type', 'Unknown').upper()
            
            if code_type not in filter_types:
                filtered_crossings.append(crossing)
            else:
                filtered_count += 1
        
        if filter_types:
            print(f"✅ Found {len(crossings)} airspace crossings (filtered out {filtered_count} {'/'.join(filter_types)} zones)")
        else:
            print(f"✅ Found {len(crossings)} airspace crossings (no filtering applied)")
            
        if not filtered_crossings:
            print("❌ No airspace crossings remaining after filtering")
            return
            
        print(f"📋 Displaying {len(filtered_crossings)} relevant airspaces (chronological order):")
        print("=" * 80)
        
        # Display filtered chronological crossings
        for i, crossing in enumerate(filtered_crossings, 1):
            airspace = crossing['airspace']
            distance = crossing['distance_km']
            
            # Classify airspace type
            code_type = airspace.get('code_type', 'Unknown').upper()
            if code_type in ['TMA']:
                type_emoji = "🛬"
            elif code_type in ['RAS']:
                type_emoji = "📡"
            elif code_type in ['R', 'P', 'D']:
                type_emoji = "⛔"
            elif code_type in ['CTR']:
                type_emoji = "🏢"
            else:
                type_emoji = "🌐"
            
            print(f"{i:2d}. {type_emoji} {airspace['name']} ({airspace.get('code_id', 'N/A')})")
            print(f"     Type: {airspace.get('code_type', 'Unknown')} - Class: {airspace.get('airspace_class', 'Unknown')}")
            
            # Altitude conversion for display
            lower_alt = airspace.get('lower_limit_ft_converted', airspace.get('lower_limit_ft', 'N/A'))
            upper_alt = airspace.get('upper_limit_ft_converted', airspace.get('upper_limit_ft', 'N/A'))
            print(f"     Altitude: {lower_alt} - {upper_alt} ft")
            print(f"     Distance: {distance:.1f} km from start")
            print()
        
        print("=" * 80)
        if filter_types and filtered_count > 0:
            print(f"🏁 Analysis complete - {len(filtered_crossings)} relevant airspaces shown ({filtered_count} filtered out)")
        else:
            print(f"🏁 Analysis complete - {len(filtered_crossings)} airspaces crossed along flight path")
        
    except Exception as e:
        print(f"❌ Error during flight analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def cmd_generate(args, kml_service):
    """Handle generate subcommand"""
    
    # Check if --profile option is used
    if args.profile:
        return cmd_generate_profile(args)
    
    # Check if any generation criteria is provided
    if not (args.id or args.ids or args.name or args.type):
        print("❌ Error: Must specify generation criteria (--id, --ids, --name, or --type)")
        return
    
    # Original generate functionality continues here...
    print("🛩️ Standard KML generation not yet updated in this version")
    print("   Use the --profile option for flight path based generation")


def cmd_generate_profile(args):
    """Handle generate --profile subcommand for flight path KML generation"""
    from core.flight_analyzer import FlightProfileAnalyzer
    
    if not args.profile:
        print("❌ Error: --profile requires KML flight path file")
        return
    
    kml_file = args.profile
    if not os.path.exists(kml_file):
        print(f"❌ Error: KML file not found: {kml_file}")
        return
    
    print(f"🛩️ Analyzing flight path for KML generation: {os.path.basename(kml_file)}")
    print(f"   Corridor: ±{args.corridor_height} ft, ±{args.corridor_width} NM")
    print()
    
    # Create output directory
    output_dir = Path(args.directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize analyzer
        analyzer = FlightProfileAnalyzer(
            args.database, 
            args.corridor_height, 
            args.corridor_width
        )
        
        # Get chronological crossings
        crossings = analyzer.get_chronological_crossings(kml_file, sample_distance_km=5.0)
        
        if not crossings:
            print("❌ No airspace crossings found - no KML files to generate")
            return
            
        # Apply type filtering
        filter_types = set()
        if args.filter_types:
            filter_types = {t.strip().upper() for t in args.filter_types.split(',') if t.strip()}
        
        # Filter out unwanted airspace types
        filtered_crossings = []
        filtered_count = 0
        for crossing in crossings:
            airspace = crossing['airspace']
            code_type = airspace.get('code_type', 'Unknown').upper()
            
            if code_type not in filter_types:
                filtered_crossings.append(crossing)
            else:
                filtered_count += 1
        
        if not filtered_crossings:
            print("❌ No airspace crossings remaining after filtering - no KML files to generate")
            return
        
        # Extract unique airspace IDs from filtered crossings
        airspace_ids = [crossing['airspace']['id'] for crossing in filtered_crossings]
        unique_ids = list(dict.fromkeys(airspace_ids))  # Preserve order, remove duplicates
        
        if filter_types:
            print(f"✅ Found {len(crossings)} crossings across {len(unique_ids)} unique airspaces (filtered out {filtered_count} {'/'.join(filter_types)} zones)")
        else:
            print(f"✅ Found {len(crossings)} crossings across {len(unique_ids)} unique airspaces (no filtering applied)")
        print(f"🎯 Generating KML volumes for crossed airspaces...")
        print()
        
        # Initialize KML service for generation
        kml_service_gen = KMLVolumeService()
        
        generated_files = []
        
        # Generate individual KML files for each crossed airspace
        for i, airspace_id in enumerate(unique_ids, 1):
            try:
                # Find corresponding crossing info from filtered crossings
                crossing = next(c for c in filtered_crossings if c['airspace']['id'] == airspace_id)
                airspace = crossing['airspace']
                
                print(f"   [{i:2d}/{len(unique_ids)}] Generating {airspace['name']}...")
                
                # Generate filename
                safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in airspace['name'])
                output_filename = f"flight_profile_{safe_name}_{airspace_id}.kml"
                output_path = output_dir / output_filename
                
                # Generate KML
                try:
                    kml_service_gen.save_airspace_kml(airspace_id, str(output_path))
                    success = True
                    generated_files.append({
                        'file': str(output_path),
                        'airspace': airspace,
                        'distance': crossing['distance_km']
                    })
                    if args.verbose:
                        print(f"      ✅ {output_filename} (crossed at {crossing['distance_km']:.1f} km)")
                except Exception as e:
                    success = False
                    print(f"      ❌ Error: {e}")
                
            except Exception as e:
                print(f"      ❌ Error generating {airspace['name']}: {e}")
                continue
        
        # Generate combined KML if requested or by default
        if not args.individual or len(unique_ids) > 1:
            try:
                flight_name = os.path.splitext(os.path.basename(kml_file))[0]
                combined_filename = f"flight_profile_{flight_name}_combined.kml"
                combined_path = output_dir / combined_filename
                
                print(f"   📦 Generating combined KML: {combined_filename}...")
                
                # Parse flight coordinates for inclusion in combined KML
                from core.spatial_query import KMLFlightPathParser
                flight_coordinates = KMLFlightPathParser.parse_kml_coordinates(kml_file)
                
                # Use generate_multiple_airspaces_kml method with flight path info
                kml_content = kml_service_gen.generate_multiple_airspaces_kml(
                    unique_ids, 
                    flight_name=flight_name,
                    flight_coordinates=flight_coordinates if flight_coordinates else None
                )
                
                # Write to file
                with open(combined_path, 'w', encoding='utf-8') as f:
                    f.write(kml_content)
                
                generated_files.append({
                    'file': str(combined_path),
                    'type': 'combined',
                    'count': len(unique_ids)
                })
                print(f"      ✅ Combined KML saved")
            
            except Exception as e:
                print(f"      ❌ Error generating combined KML: {e}")
        
        # Summary
        print()
        print("=" * 60)
        print(f"🎉 KML generation complete!")
        print(f"   Generated: {len([f for f in generated_files if 'type' not in f])} individual files")
        if any('type' in f for f in generated_files):
            print(f"   Combined: 1 file with {len(unique_ids)} airspaces")
        print(f"   Output directory: {output_dir}")
        
        if args.verbose and generated_files:
            print("\n📁 Generated files:")
            for file_info in generated_files:
                if 'type' in file_info:
                    print(f"   📦 {os.path.basename(file_info['file'])} (combined)")
                else:
                    airspace = file_info['airspace'] 
                    print(f"   🎯 {os.path.basename(file_info['file'])} - {airspace['name']}")
        
    except Exception as e:
        print(f"❌ Error during flight analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def cmd_stats(args, kml_service):
    """Handle stats subcommand"""
    if not args.quiet:
        print("📊 Gathering database statistics...")
    
    try:
        total_count = len(kml_service.get_airspace_by_name(""))
        print(f"✅ Database contains {total_count} airspaces")
        
        if args.detailed:
            # Count by types
            all_airspaces = kml_service.get_airspace_by_name("")
            type_counts = {}
            for airspace in all_airspaces:
                airspace_type = airspace.get('code_type', 'Unknown')
                type_counts[airspace_type] = type_counts.get(airspace_type, 0) + 1
            
            print("\n📊 Breakdown by type:")
            for airspace_type, count in sorted(type_counts.items()):
                print(f"   {airspace_type}: {count}")
    
    except Exception as e:
        print(f"❌ Error accessing database: {e}")


def show_help(topic=None):
    """Show comprehensive help information"""
    if topic == 'list':
        print("""
🔍 LIST COMMAND HELP

Search and list airspaces by various criteria, or analyze flight paths.

BASIC USAGE:
  navpro list --name PATTERN       # List airspaces matching name pattern
  navpro list --id ID              # Show details for specific airspace
  navpro list --type TYPE          # List airspaces of specific type
  navpro list --all                # List all airspaces (limited)

FLIGHT PATH ANALYSIS:
  navpro list --profile flight.kml # List airspaces crossed chronologically
  
  Optional corridor settings:
  --corridor-height 1500           # Vertical corridor ±1500 ft (default: 1000)
  --corridor-width 15              # Horizontal corridor ±15 NM (default: 10)

OUTPUT OPTIONS:
  --summary, -s                    # Compact summary format
  --limit 100, -l 100              # Limit results (default: 50)
  --verbose, -v                    # Show detailed geometry information
  --quiet, -q                      # Minimal output

EXAMPLES:
  navpro list --name "CHEVREUSE"           # Find CHEVREUSE airspaces
  navpro list --type TMA --limit 20        # Show 20 TMAs
  navpro list --profile route.kml --verbose # Analyze flight with details
""")
    elif topic == 'generate':
        print("""
🛩️ GENERATE COMMAND HELP

Generate 3D KML volumes for airspaces or flight path crossings.

BASIC USAGE:
  navpro generate --id ID          # Generate KML for single airspace
  navpro generate --ids ID1 ID2    # Generate for multiple airspaces  
  navpro generate --name PATTERN   # Generate for matching airspaces
  navpro generate --type TYPE      # Generate for airspace type

FLIGHT PATH GENERATION:
  navpro generate --profile flight.kml # Generate KML for crossed airspaces
  
  Optional corridor settings:
  --corridor-height 1500           # Vertical corridor ±1500 ft (default: 1000)
  --corridor-width 15              # Horizontal corridor ±15 NM (default: 10)

OUTPUT OPTIONS:
  --output FILE, -o FILE           # Specific output filename
  --directory DIR, -d DIR          # Output directory (default: current)
  --individual                     # Generate separate files
  --combined-only                  # Generate only combined file

EXAMPLES:
  navpro generate --id 4749                     # Single airspace
  navpro generate --profile route.kml           # Flight path analysis
  navpro generate --name "PARIS" --individual   # All PARIS airspaces
""")
    elif topic == 'stats':
        print("""
📊 STATS COMMAND HELP

Display database statistics and health information.

USAGE:
  navpro stats                     # Basic statistics
  navpro stats --detailed          # Detailed breakdown by type

OUTPUT:
  - Total airspace count
  - Breakdown by airspace type (detailed mode)
  - Database health information
""")
    else:
        print("""
📚 NavPro - Navigation Profile Command Line Tool

🔧 MAIN COMMANDS:
  list        Search and display airspaces, or analyze flight paths
  generate    Create 3D KML volumes for airspaces or flight crossings
  stats       Show database statistics  
  help        Show this help or help for specific commands

🚀 QUICK START:
  navpro list --name "CHEVREUSE"           # Find CHEVREUSE airspaces
  navpro list --profile data/flight.kml    # Analyze flight path chronologically
  navpro generate --id 4749               # Generate KML for ID 4749
  navpro generate --profile flight.kml    # Generate KML for crossed airspaces
  navpro stats                             # Show database overview

📖 DETAILED HELP:
  navpro help list                         # Help for list command
  navpro help generate                     # Help for generate command  
  navpro help stats                        # Help for stats command

🌍 KEY FEATURES:
  - Professional airspace search and listing
  - Flight path analysis with chronological crossing detection
  - 3D KML volume generation for Google Earth
  - Configurable corridor analysis (±height, ±width)
  - TMAs, RAS, Restricted zone detection with Flight Level support
  - Batch operations for multiple airspaces

Use 'navpro COMMAND --help' for specific command options.
""")


def main():
    """Main entry point"""
    parser = create_parser()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # Handle help command
    if args.command == 'help':
        show_help(args.topic)
        return
    
    # Handle commands that need KML service
    if args.command in ['list', 'generate', 'stats']:
        if args.command == 'list' and args.profile:
            # Profile mode doesn't need KML service
            cmd_list(args, None)
        elif args.command == 'generate' and args.profile:
            # Profile mode doesn't need KML service
            cmd_generate(args, None)
        else:
            # Regular commands need KML service
            try:
                kml_service = KMLVolumeService()
                if args.command == 'list':
                    cmd_list(args, kml_service)
                elif args.command == 'generate':
                    cmd_generate(args, kml_service)
                elif args.command == 'stats':
                    cmd_stats(args, kml_service)
            except Exception as e:
                print(f"❌ Error initializing services: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()