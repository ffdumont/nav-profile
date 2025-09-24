#!/usr/bin/env python3
"""
Command-line tool for searching airspaces by keyword
"""
import sys
import argparse
from aixm_query_service import AirspaceQueryService

def format_airspace_details(airspace):
    """Format airspace details for display"""
    print(f"\n{'='*60}")
    print(f"✈️  {airspace['code_id']}: {airspace['name']}")
    print(f"{'='*60}")
    print(f"📋 Type: {airspace['code_type']}")
    
    if airspace.get('local_type'):
        print(f"📋 Local Type: {airspace['local_type']}")
    
    print(f"📏 Altitude: {airspace['altitude_display']}")
    
    if airspace.get('airspace_class') and airspace['airspace_class'] != 'UNKNOWN':
        print(f"🏷️  Class: {airspace['airspace_class']}")
    
    if airspace.get('activity_type'):
        print(f"🎯 Activity: {airspace['activity_type']}")
    
    if airspace.get('operating_hours'):
        print(f"⏰ Operating Hours: {airspace['operating_hours']}")
    
    if airspace.get('operating_remarks'):
        print(f"📝 Remarks: {airspace['operating_remarks']}")
    
    # Geometry info
    border_count = airspace.get('border_count', 0)
    vertex_count = airspace.get('vertex_count', 0)
    
    if border_count > 0:
        print(f"🗺️  Geometry: {border_count} border(s), {vertex_count} vertices")
    else:
        print(f"🗺️  Geometry: No geometric data")
    
    # Technical info
    if airspace.get('mid'):
        print(f"🔢 MID: {airspace['mid']}")
    
    print(f"📅 Last Updated: {airspace.get('updated_at', 'Unknown')}")

def main():
    parser = argparse.ArgumentParser(
        description="Search airspaces by keyword",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search_tool.py CHEVREUSE          # Find all CHEVREUSE airspaces
  python search_tool.py -c PARIS           # Case-sensitive search for PARIS
  python search_tool.py -l 5 LFR          # Find first 5 airspaces containing LFR
  python search_tool.py --summary TMA      # Summary view of TMA airspaces
        """
    )
    
    parser.add_argument('keyword', nargs='?', help='Keyword to search for in airspace names')
    parser.add_argument('-c', '--case-sensitive', action='store_true', 
                       help='Make search case-sensitive')
    parser.add_argument('-l', '--limit', type=int, 
                       help='Maximum number of results to return')
    parser.add_argument('-s', '--summary', action='store_true',
                       help='Show summary view instead of detailed view')
    parser.add_argument('--code', help='Get details for specific airspace code')
    
    args = parser.parse_args()
    
    try:
        service = AirspaceQueryService()
        
        if args.code:
            # Get specific airspace details
            airspace = service.get_airspace_details(args.code)
            if airspace:
                format_airspace_details(airspace)
            else:
                print(f"❌ Airspace with code '{args.code}' not found")
                return 1
        elif args.keyword:
            # Search by keyword
            results = service.search_by_keyword(
                args.keyword, 
                case_sensitive=args.case_sensitive,
                limit=args.limit
            )
            
            if not results:
                print(f"❌ No airspaces found containing '{args.keyword}'")
                return 1
            
            print(f"🔍 Found {len(results)} airspace(s) containing '{args.keyword}':")
            
            if args.summary:
                # Summary view
                print(f"\n{'Code':<12} {'Name':<25} {'Type':<8} {'Altitude':<20}")
                print(f"{'-'*12} {'-'*25} {'-'*8} {'-'*20}")
                
                for airspace in results:
                    name = airspace['name'][:24] + ('...' if len(airspace['name']) > 24 else '')
                    alt_display = airspace['altitude_display'][:19] + ('...' if len(airspace['altitude_display']) > 19 else '')
                    
                    print(f"{airspace['code_id']:<12} {name:<25} {airspace['code_type']:<8} {alt_display:<20}")
            else:
                # Detailed view
                for airspace in results:
                    format_airspace_details(airspace)
        else:
            print("❌ Please provide either a keyword to search or use --code for specific airspace")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())