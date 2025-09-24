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

from kml_volume_service import KMLVolumeService


def create_parser():
    """Create the main argument parser with subcommands"""
    parser = argparse.ArgumentParser(
        prog="navpro",
        description="NavPro - Navigation Profile Command Line Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  navpro list --name "CHEVREUSE"           # List airspaces matching pattern
  navpro list --id 4749                   # Show details for specific ID
  navpro list --all                       # List all airspaces (limited)
  
  navpro generate --id 4749               # Generate KML for single airspace
  navpro generate --name "CHEVREUSE"      # Generate KML for all matching
  navpro generate --ids 4749 4750 4751    # Generate combined KML
  
  navpro stats                             # Show database statistics
  navpro help                              # Show detailed help

NavPro provides professional navigation services including:
- Airspace search and listing
- 3D KML volume visualization  
- Batch operations and automation
- Future: Route planning, obstacle analysis, and more
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
        description='Search and list airspaces by various criteria'
    )
    list_group = list_parser.add_mutually_exclusive_group(required=True)
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
        '--limit', '-l', type=int, default=50,
        help='Limit number of results (default: 50)'
    )
    list_parser.add_argument(
        '--summary', '-s', action='store_true',
        help='Show compact summary format'
    )
    
    # GENERATE subcommand
    gen_parser = subparsers.add_parser(
        'generate',
        help='Generate KML volumes',
        description='Generate 3D KML volumes for airspaces'
    )
    gen_group = gen_parser.add_mutually_exclusive_group(required=True)
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


def cmd_generate(args, kml_service):
    """Handle generate subcommand"""
    if not args.quiet:
        print("🛩️ Preparing KML generation...")
    
    # Create output directory
    output_dir = Path(args.directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    airspace_ids = []
    
    # Determine which airspaces to process
    if args.id:
        airspace_ids = [args.id]
        operation_desc = f"airspace ID {args.id}"
    elif args.ids:
        airspace_ids = args.ids
        operation_desc = f"{len(args.ids)} airspace IDs"
    elif args.name:
        airspaces = kml_service.get_airspace_by_name(args.name)
        # Filter for valid geometry
        valid_airspaces = []
        for airspace in airspaces:
            try:
                geometry_data = kml_service._get_airspace_geometry(airspace['id'])
                if geometry_data:
                    valid_airspaces.append(airspace)
            except:
                pass
        airspace_ids = [a['id'] for a in valid_airspaces]
        operation_desc = f"airspaces matching '{args.name}' ({len(airspace_ids)} with geometry)"
    elif args.type:
        all_airspaces = kml_service.get_airspace_by_name("")
        type_airspaces = [a for a in all_airspaces if a.get('code_type', '').upper() == args.type.upper()]
        # Filter for valid geometry
        valid_airspaces = []
        for airspace in type_airspaces:
            try:
                geometry_data = kml_service._get_airspace_geometry(airspace['id'])
                if geometry_data:
                    valid_airspaces.append(airspace)
            except:
                pass
        airspace_ids = [a['id'] for a in valid_airspaces]
        operation_desc = f"airspaces of type '{args.type}' ({len(airspace_ids)} with geometry)"
    
    if not airspace_ids:
        print(f"❌ No airspaces found for {operation_desc}")
        return
    
    if not args.quiet:
        print(f"🎯 Generating KML for {operation_desc}")
    
    generated_files = []
    
    # Generate files
    if len(airspace_ids) == 1 or args.individual:
        # Individual files
        if not args.quiet and len(airspace_ids) > 1:
            print("📦 Generating individual KML files...")
            
        for airspace_id in airspace_ids:
            try:
                # Get airspace info for filename
                all_airspaces = kml_service.get_airspace_by_name("")
                airspace = next((a for a in all_airspaces if a['id'] == airspace_id), None)
                
                if not airspace:
                    if not args.quiet:
                        print(f"   ⚠️  Airspace ID {airspace_id} not found")
                    continue
                
                # Generate filename
                if args.output and len(airspace_ids) == 1:
                    output_path = output_dir / args.output
                else:
                    safe_name = airspace['name'].replace(' ', '_').replace('/', '_')
                    output_path = output_dir / f"{safe_name}_{airspace_id}.kml"
                
                # Generate KML
                kml_service.save_airspace_kml(airspace_id, str(output_path))
                generated_files.append(output_path)
                
                if not args.quiet:
                    file_size = output_path.stat().st_size
                    print(f"   ✅ {airspace['name']}: {output_path.name} ({file_size} bytes)")
                    
            except Exception as e:
                if not args.quiet:
                    print(f"   ❌ Error generating KML for airspace {airspace_id}: {e}")
    
    # Generate combined file if multiple airspaces and not individual-only
    if len(airspace_ids) > 1 and not args.individual:
        if not args.quiet:
            print("🔗 Generating combined KML file...")
        
        try:
            # Determine combined filename
            if args.output:
                combined_path = output_dir / args.output
            else:
                if args.name:
                    safe_name = args.name.replace(' ', '_').replace('/', '_')
                    combined_path = output_dir / f"{safe_name}_combined.kml"
                elif args.type:
                    combined_path = output_dir / f"{args.type}_combined.kml"
                else:
                    combined_path = output_dir / f"combined_{len(airspace_ids)}_airspaces.kml"
            
            # Generate combined KML
            combined_kml = kml_service.generate_multiple_airspaces_kml(airspace_ids)
            with open(combined_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(combined_kml)
            
            generated_files.append(combined_path)
            
            if not args.quiet:
                file_size = combined_path.stat().st_size
                placemark_count = combined_kml.count('<Placemark>') + combined_kml.count('<ns0:Placemark>')
                print(f"   ✅ Combined: {combined_path.name} ({file_size} bytes, {placemark_count} volumes)")
                
        except Exception as e:
            if not args.quiet:
                print(f"   ❌ Error generating combined KML: {e}")
    
    # Summary
    if not args.quiet:
        print(f"\n🎉 Generated {len(generated_files)} KML file(s)")
        print(f"📁 Output directory: {output_dir.absolute()}")
        
        if args.verbose:
            print("🌍 KML features:")
            print("   - 3D volumes with altitude extrusion")
            print("   - Google Earth compatible")
            print("   - Professional aviation visualization")


def cmd_stats(args, kml_service):
    """Handle stats subcommand"""
    if not args.quiet:
        print("📊 Gathering database statistics...")
    
    try:
        # Get all airspaces for analysis
        all_airspaces = kml_service.get_airspace_by_name("")
        
        print(f"\n📈 NavPro Database Statistics")
        print(f"{'='*50}")
        print(f"Total airspaces: {len(all_airspaces)}")
        
        # Count by type
        type_counts = {}
        geometry_count = 0
        altitude_info = {'with_max': 0, 'without_max': 0}
        
        for airspace in all_airspaces:
            airspace_type = airspace.get('code_type', 'Unknown')
            type_counts[airspace_type] = type_counts.get(airspace_type, 0) + 1
            
            # Check geometry
            try:
                geometry_data = kml_service._get_airspace_geometry(airspace['id'])
                if geometry_data:
                    geometry_count += 1
            except:
                pass
            
            # Check altitude info
            if airspace.get('max_altitude'):
                altitude_info['with_max'] += 1
            else:
                altitude_info['without_max'] += 1
        
        print(f"\nAirspace Types:")
        for airspace_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {airspace_type:>10}: {count:>4} airspaces")
        
        print(f"\nGeometry Information:")
        print(f"  With geometry: {geometry_count:>4} airspaces ({geometry_count/len(all_airspaces)*100:.1f}%)")
        print(f"  No geometry:   {len(all_airspaces)-geometry_count:>4} airspaces")
        
        print(f"\nAltitude Information:")
        print(f"  With max alt:  {altitude_info['with_max']:>4} airspaces")
        print(f"  No max alt:    {altitude_info['without_max']:>4} airspaces")
        
        if args.detailed:
            print(f"\nDetailed Analysis:")
            
            # Altitude ranges
            altitudes = []
            for airspace in all_airspaces:
                if airspace.get('max_altitude') and airspace.get('max_altitude_unit') == 'FT':
                    altitudes.append(airspace['max_altitude'])
            
            if altitudes:
                print(f"  Max altitude range: {min(altitudes)} - {max(altitudes)} FT")
                print(f"  Average max altitude: {sum(altitudes)/len(altitudes):.0f} FT")
            
            # Operating hours analysis
            with_hours = sum(1 for a in all_airspaces if a.get('operating_hours'))
            print(f"  With operating hours: {with_hours} airspaces")
        
        print(f"\n🌍 KML Generation Capability:")
        print(f"  Ready for KML: {geometry_count:>4} airspaces")
        print(f"  3D volumes available for professional visualization")
        
    except Exception as e:
        print(f"❌ Error gathering statistics: {e}")


def cmd_help(args, kml_service):
    """Handle help subcommand"""
    if args.topic:
        print(f"📚 Detailed help for '{args.topic}' command:\n")
        
        if args.topic == 'list':
            print("""🔍 LIST Command - Search and display airspaces

Usage:
  navpro list --name "CHEVREUSE"     # Find airspaces by name pattern
  navpro list --id 4749             # Show details for specific ID  
  navpro list --type RAS            # List airspaces of specific type
  navpro list --all                 # List all airspaces (limited)

Options:
  --limit N, -l N     Limit results to N entries (default: 50)
  --summary, -s       Show compact summary format
  --verbose, -v       Show detailed information including geometry
  --quiet, -q         Minimal output

Examples:
  navpro list --name "PARIS" --limit 10    # First 10 Paris airspaces
  navpro list --type TMA --summary          # Summary of all TMA areas  
  navpro list --id 4749 --verbose          # Detailed info for ID 4749
""")
        
        elif args.topic == 'generate':
            print("""🛩️ GENERATE Command - Create 3D KML volumes

Usage:
  navpro generate --id 4749              # Single airspace KML
  navpro generate --ids 4749 4750 4751   # Combined KML for multiple IDs
  navpro generate --name "CHEVREUSE"     # All matching airspaces
  navpro generate --type RAS             # All airspaces of type

Options:
  --output FILE, -o FILE      Custom output filename
  --directory DIR, -d DIR     Output directory (default: current)
  --individual               Generate individual files for each airspace
  --combined-only            Generate only combined file (no individuals)
  --verbose, -v              Show detailed generation progress
  --quiet, -q                Minimal output

Examples:
  navpro generate --id 4749 --output my_airspace.kml
  navpro generate --name "PARIS" --directory kml_output
  navpro generate --type TMA --individual --verbose
""")
        
        elif args.topic == 'stats':
            print("""📊 STATS Command - Database statistics and health

Usage:
  navpro stats                # Basic statistics
  navpro stats --detailed     # Detailed analysis

Shows:
  - Total airspace count
  - Breakdown by airspace type
  - Geometry availability
  - Altitude information coverage
  - KML generation readiness

Options:
  --detailed     Show additional analysis and ranges
  --quiet, -q    Minimal output
""")
    
    else:
        print("""📚 NavPro - Navigation Profile Command Line Tool

🔧 MAIN COMMANDS:
  list        Search and display airspaces
  generate    Create 3D KML volumes  
  stats       Show database statistics
  help        Show this help or help for specific commands

🚀 QUICK START:
  navpro list --name "CHEVREUSE"           # Find CHEVREUSE airspaces
  navpro generate --id 4749               # Generate KML for ID 4749
  navpro stats                             # Show database overview

📖 DETAILED HELP:
  navpro help list                         # Help for list command
  navpro help generate                     # Help for generate command
  navpro help stats                        # Help for stats command

🌍 FEATURES:
  - Professional airspace search and listing
  - 3D KML volume generation for Google Earth
  - Batch operations for multiple airspaces
  - Comprehensive database statistics
  - Consistent command-line interface

Use 'navpro COMMAND --help' for specific command options.
""")


def main():
    """Main NavPro entry point with subcommand structure"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle case where no command is provided
    if not args.command:
        parser.print_help()
        return
    
    # Validate global arguments
    if args.verbose and args.quiet:
        print("❌ Error: Cannot use --verbose and --quiet together", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Initialize KML service for most commands
        if args.command in ['list', 'generate', 'stats']:
            if not args.quiet:
                print("🛩️ Initializing NavPro services...")
            
            kml_service = KMLVolumeService()
            
            if not args.quiet:
                print("✅ NavPro services initialized successfully")
        else:
            kml_service = None
        
        # Route to appropriate command handler
        if args.command == 'list':
            cmd_list(args, kml_service)
        elif args.command == 'generate':
            cmd_generate(args, kml_service)
        elif args.command == 'stats':
            cmd_stats(args, kml_service)
        elif args.command == 'help':
            cmd_help(args, kml_service)
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()