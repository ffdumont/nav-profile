# NavPro PowerShell Wrapper
# Windows-friendly interface for NavPro navigation services

param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [string]$Name,
    [int]$Id,
    [int[]]$Ids,
    [string]$Type,
    [string]$Output,
    [string]$Directory = ".",
    [int]$Limit = 50,
    [switch]$All,
    [switch]$Individual,
    [switch]$CombinedOnly,
    [switch]$Summary,
    [switch]$Detailed,
    [switch]$VerboseOutput,
    [switch]$Quiet,
    [switch]$Help
)

function Show-Help {
    Write-Host @"
🛩️ NavPro - Navigation Profile PowerShell Interface

Usage: .\navpro.ps1 COMMAND [OPTIONS]

COMMANDS:
  list        Search and display airspaces
  generate    Create 3D KML volumes
  stats       Show database statistics  
  help        Show detailed help

EXAMPLES:
  .\navpro.ps1 list -Name "CHEVREUSE"
  .\navpro.ps1 generate -Id 4749 -Output "my_airspace.kml"
  .\navpro.ps1 generate -Name "PARIS" -Directory "kml_output"
  .\navpro.ps1 stats -Detailed

LIST OPTIONS:
  -Name <pattern>     List airspaces matching name pattern
  -Id <id>           Show details for specific airspace ID
  -Type <type>       List airspaces of specific type (RAS, TMA, etc.)
  -All               List all airspaces (limited)
  -Limit <n>         Limit results (default: 50)
  -Summary           Show compact summary format
  
GENERATE OPTIONS:
  -Id <id>           Generate KML for single airspace
  -Ids <id1>,<id2>   Generate combined KML for multiple IDs  
  -Name <pattern>    Generate KML for matching airspaces
  -Type <type>       Generate KML for airspaces of type
  -Output <file>     Custom output filename
  -Directory <dir>   Output directory (default: current)
  -Individual        Generate individual files for each airspace
  -CombinedOnly      Generate only combined file

STATS OPTIONS:
  -Detailed          Show detailed analysis

GLOBAL OPTIONS:
  -VerboseOutput    Show detailed output
  -Quiet            Minimal output
  -Help             Show this help

For detailed command help: .\navpro.ps1 help <command>
"@
}

function Show-CommandHelp {
    param([string]$CommandName)
    
    $pythonArgs = @("help")
    if ($CommandName) {
        $pythonArgs += $CommandName
    }
    
    & python.exe ..\navpro\navpro.py @pythonArgs
}

# Show help if no command or -Help specified
if (-not $Command -or $Help) {
    if ($Command -eq "help") {
        Show-CommandHelp $Name
    } else {
        Show-Help
    }
    exit 0
}

# Validate command
$validCommands = @("list", "generate", "stats", "help")
if ($Command -notin $validCommands) {
    Write-Error "Invalid command '$Command'. Valid commands: $($validCommands -join ', ')"
    Write-Host "Use '.\navpro.ps1 -Help' for usage information."
    exit 1
}

# Build arguments for Python script
$pythonArgs = @($Command)

# Handle command-specific arguments
switch ($Command) {
    "list" {
        if ($Name) { $pythonArgs += "--name"; $pythonArgs += $Name }
        if ($Id) { $pythonArgs += "--id"; $pythonArgs += $Id }
        if ($Type) { $pythonArgs += "--type"; $pythonArgs += $Type }
        if ($All) { $pythonArgs += "--all" }
        if ($Limit -ne 50) { $pythonArgs += "--limit"; $pythonArgs += $Limit }
        if ($Summary) { $pythonArgs += "--summary" }
    }
    "generate" {
        if ($Id) { $pythonArgs += "--id"; $pythonArgs += $Id }
        if ($Ids) { 
            $pythonArgs += "--ids"
            $pythonArgs += $Ids
        }
        if ($Name) { $pythonArgs += "--name"; $pythonArgs += $Name }
        if ($Type) { $pythonArgs += "--type"; $pythonArgs += $Type }
        if ($Output) { $pythonArgs += "--output"; $pythonArgs += $Output }
        if ($Directory -ne ".") { $pythonArgs += "--directory"; $pythonArgs += $Directory }
        if ($Individual) { $pythonArgs += "--individual" }
        if ($CombinedOnly) { $pythonArgs += "--combined-only" }
    }
    "stats" {
        if ($Detailed) { $pythonArgs += "--detailed" }
    }
    "help" {
        if ($Name) { $pythonArgs += $Name }
    }
}

# Add global options
if ($VerboseOutput) { $pythonArgs += "--verbose" }
if ($Quiet) { $pythonArgs += "--quiet" }

# Execute Python script
try {
    & python.exe ..\navpro\navpro.py @pythonArgs
    exit $LASTEXITCODE
} catch {
    Write-Error "Failed to execute NavPro: $_"
    exit 1
}