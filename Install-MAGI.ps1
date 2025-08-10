# 🧙‍♂️ MAGI PowerShell Installer for Windows
# Modern installation with proper Windows integration

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("GASPAR", "MELCHIOR", "BALTASAR")]
    [string]$NodeName = ""
)

# Function to write colored output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Banner
Write-Host ""
Write-ColorOutput Red @"
🧙‍♂️ ═══════════════════════════════════════════════════════════════
    MAGI PowerShell Installer - Windows Integration
    Distributed Monitoring System for Home Labs
═══════════════════════════════════════════════════════════════
"@
Write-Host ""

# Check PowerShell version
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-ColorOutput Red "❌ PowerShell 5.0+ required. Current version: $($PSVersionTable.PSVersion)"
    Write-Host "Please update PowerShell from: https://github.com/PowerShell/PowerShell"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-ColorOutput Green "✅ PowerShell $($PSVersionTable.PSVersion.Major).$($PSVersionTable.PSVersion.Minor) - Compatible"

# Check Python
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput Green "✅ $pythonVersion"
    } else {
        throw "Python not found"
    }
} catch {
    Write-ColorOutput Red "❌ Python not found!"
    Write-Host ""
    Write-Host "📥 Install Python from: https://python.org"
    Write-Host "   ✅ Check 'Add Python to PATH' during installation"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Get installation directory
$MAGIHome = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "📁 Installation Directory: $MAGIHome"

# Check MAGI file
if (-not (Test-Path "$MAGIHome\magi-node.py")) {
    Write-ColorOutput Red "❌ magi-node.py not found in $MAGIHome"
    Write-Host "Please run this installer from the MAGI directory"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-ColorOutput Green "✅ magi-node.py found"

# Select node if not provided
if (-not $NodeName) {
    Write-Host ""
    Write-Host "🎯 Choose your MAGI node:"
    Write-Host "   1. GASPAR  - Multimedia & Entertainment Node"
    Write-Host "   2. MELCHIOR - Backup & Storage Node"
    Write-Host "   3. BALTASAR - Home Automation Node"
    Write-Host ""
    
    do {
        $choice = Read-Host "Enter choice (1-3)"
        switch ($choice) {
            "1" { $NodeName = "GASPAR"; break }
            "2" { $NodeName = "MELCHIOR"; break }
            "3" { $NodeName = "BALTASAR"; break }
            default { Write-Host "❌ Invalid choice. Please enter 1, 2, or 3." }
        }
    } while (-not $NodeName)
}

Write-ColorOutput Green "✅ Selected node: $NodeName"

# Create startup script
Write-Host "🔧 Creating startup scripts..."

$startupScript = @"
@echo off
title 🧙‍♂️ MAGI $NodeName Monitoring Node
color 0C
echo.
echo 🧙‍♂️ ═══════════════════════════════════════════════════════════════
echo      MAGI $NodeName Node - Distributed Monitoring System
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📡 Starting MAGI server...
echo 🌐 Dashboard will be available at: http://localhost:8081
echo.
cd /d "$MAGIHome"
python magi-node.py $NodeName
echo.
echo 🛑 MAGI server stopped
pause
"@

$startupScript | Out-File -FilePath "$MAGIHome\Start-MAGI-$NodeName.bat" -Encoding ASCII
Write-ColorOutput Green "✅ Created: Start-MAGI-$NodeName.bat"

# Create dashboard launcher
$dashboardScript = @"
@echo off
echo 🌐 Opening MAGI Dashboard...
start http://localhost:8081
exit
"@

$dashboardScript | Out-File -FilePath "$MAGIHome\Open-MAGI-Dashboard.bat" -Encoding ASCII
Write-ColorOutput Green "✅ Created: Open-MAGI-Dashboard.bat"

# Create PowerShell service script
$serviceScript = @"
# 🧙‍♂️ MAGI PowerShell Service Manager
param([string]`$Action = "start")

`$MAGIHome = "$MAGIHome"
`$NodeName = "$NodeName"
`$ProcessName = "MAGI_$NodeName"

switch (`$Action.ToLower()) {
    "start" {
        Write-Host "🚀 Starting MAGI $NodeName..."
        Start-Process -FilePath "python" -ArgumentList "`$MAGIHome\magi-node.py", `$NodeName -WorkingDirectory `$MAGIHome -WindowStyle Minimized
        Start-Sleep 2
        Write-Host "🌐 Dashboard: http://localhost:8081"
    }
    "stop" {
        Write-Host "🛑 Stopping MAGI $NodeName..."
        Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { `$_.CommandLine -like "*magi-node.py*" } | Stop-Process -Force
        Write-Host "✅ MAGI stopped"
    }
    "status" {
        `$process = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { `$_.CommandLine -like "*magi-node.py*" }
        if (`$process) {
            Write-Host "✅ MAGI $NodeName is running (PID: `$(`$process.Id))"
        } else {
            Write-Host "❌ MAGI $NodeName is not running"
        }
    }
    default {
        Write-Host "Usage: .\magi-service.ps1 [start|stop|status]"
    }
}
"@

$serviceScript | Out-File -FilePath "$MAGIHome\magi-service.ps1" -Encoding UTF8
Write-ColorOutput Green "✅ Created: magi-service.ps1"

# Create desktop shortcuts
Write-Host "🖥️ Creating desktop shortcuts..."

$desktop = [Environment]::GetFolderPath("Desktop")

# Copy batch files to desktop
try {
    Copy-Item "$MAGIHome\Start-MAGI-$NodeName.bat" -Destination $desktop -ErrorAction Stop
    Copy-Item "$MAGIHome\Open-MAGI-Dashboard.bat" -Destination $desktop -ErrorAction Stop
    Write-ColorOutput Green "✅ Desktop shortcuts created"
} catch {
    Write-ColorOutput Yellow "⚠️  Could not create desktop shortcuts: $($_.Exception.Message)"
    Write-Host "   Shortcuts are available in the MAGI folder"
}

# Create Start Menu shortcut
Write-Host "📋 Creating Start Menu entries..."
try {
    $startMenu = [Environment]::GetFolderPath("StartMenu") + "\Programs"
    $magiFolder = "$startMenu\MAGI"
    
    if (-not (Test-Path $magiFolder)) {
        New-Item -ItemType Directory -Path $magiFolder -Force | Out-Null
    }
    
    Copy-Item "$MAGIHome\Start-MAGI-$NodeName.bat" -Destination "$magiFolder\" -ErrorAction Stop
    Copy-Item "$MAGIHome\Open-MAGI-Dashboard.bat" -Destination "$magiFolder\" -ErrorAction Stop
    
    Write-ColorOutput Green "✅ Start Menu entries created in Programs\MAGI"
} catch {
    Write-ColorOutput Yellow "⚠️  Could not create Start Menu entries: $($_.Exception.Message)"
}

# Auto-start option
Write-Host ""
$autostart = Read-Host "Add MAGI to Windows startup? (y/n)"
if ($autostart -eq "y" -or $autostart -eq "Y") {
    try {
        $startupFolder = [Environment]::GetFolderPath("Startup")
        $autostartScript = @"
@echo off
cd /d "$MAGIHome"
start /min python magi-node.py $NodeName
"@
        $autostartScript | Out-File -FilePath "$startupFolder\MAGI-$NodeName-AutoStart.bat" -Encoding ASCII
        Write-ColorOutput Green "✅ Auto-start enabled"
    } catch {
        Write-ColorOutput Yellow "⚠️  Could not enable auto-start: $($_.Exception.Message)"
    }
}

# Configure Windows Firewall
Write-Host "🔥 Configuring Windows Firewall..."
try {
    $firewallRule = "MAGI $NodeName Monitoring"
    
    # Remove existing rule if it exists
    netsh advfirewall firewall delete rule name="$firewallRule" | Out-Null
    
    # Add new rule
    $result = netsh advfirewall firewall add rule name="$firewallRule" dir=in action=allow protocol=TCP localport=8081
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput Green "✅ Firewall rule added for port 8081"
    } else {
        throw "Firewall rule creation failed"
    }
} catch {
    Write-ColorOutput Yellow "⚠️  Firewall configuration failed (may need Administrator rights)"
    Write-Host "   Manually allow port 8081 in Windows Firewall if needed"
}

# Test installation
Write-Host ""
Write-Host "🧪 Testing MAGI installation..."

# Start MAGI in background for test
$testProcess = Start-Process -FilePath "python" -ArgumentList "$MAGIHome\magi-node.py", $NodeName -WorkingDirectory $MAGIHome -WindowStyle Hidden -PassThru

Start-Sleep 3

# Test connection
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8081/api/info" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-ColorOutput Green "✅ MAGI is responding correctly"
    }
} catch {
    Write-ColorOutput Yellow "⚠️  Test connection failed, but installation completed"
} finally {
    # Stop test process
    if ($testProcess -and -not $testProcess.HasExited) {
        $testProcess.Kill()
    }
    # Clean up any remaining python processes
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*magi-node.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Installation complete
Write-Host ""
Write-ColorOutput Red @"
🎉 MAGI $NodeName Installation Complete!
════════════════════════════════════════════════════════════════
"@
Write-Host ""
Write-Host "🚀 Quick Start Options:"
Write-Host "   • Desktop: Double-click 'Start-MAGI-$NodeName.bat'"
Write-Host "   • Start Menu: Programs → MAGI → Start-MAGI-$NodeName"
Write-Host "   • PowerShell: .\magi-service.ps1 start"
Write-Host ""
Write-Host "🌐 Dashboard Access:"
Write-Host "   • Desktop: Double-click 'Open-MAGI-Dashboard.bat'"
Write-Host "   • Browser: http://localhost:8081"
Write-Host ""
Write-Host "🔧 Management Commands:"
Write-Host "   • Start:  .\magi-service.ps1 start"
Write-Host "   • Stop:   .\magi-service.ps1 stop"
Write-Host "   • Status: .\magi-service.ps1 status"
Write-Host ""
Write-ColorOutput Green "🧙‍♂️ The MAGI system is ready for Windows operation!"
Write-Host ""
Read-Host "Press Enter to exit"
