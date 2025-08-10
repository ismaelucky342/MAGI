#!/usr/bin/env python3
"""
🧙‍♂️ MAGI EXE Builder - Python Script
Creates standalone Windows executables using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    print("""
🧙‍♂️ ═══════════════════════════════════════════════════════════════
    MAGI EXE Builder - Creating Windows Executables
    
    No Python needed on target machines after building!
═══════════════════════════════════════════════════════════════
""")

def check_prerequisites():
    """Check if all required tools are available"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 6):
        print(f"❌ Python {major}.{minor} detected. Python 3.6+ required.")
        return False
    print(f"✅ Python {major}.{minor} - Compatible")
    
    # Check if magi-node.py exists
    if not Path('magi-node.py').exists():
        print("❌ magi-node.py not found in current directory")
        return False
    print("✅ magi-node.py found")
    
    return True

def install_pyinstaller():
    """Install PyInstaller and dependencies"""
    print("🔧 Installing PyInstaller...")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'pyinstaller>=5.0', 'pillow>=8.0', 'requests>=2.25'
        ], check=True, capture_output=True)
        print("✅ PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install PyInstaller: {e}")
        return False

def create_icon():
    """Create Windows icon from SVG if possible"""
    print("🎨 Creating icon...")
    
    icon_svg = Path('magi-icon.svg')
    icon_ico = Path('magi-icon.ico')
    
    if not icon_svg.exists():
        print("⚠️  magi-icon.svg not found, using default icon")
        return None
    
    # Try to convert SVG to ICO using Pillow
    try:
        from PIL import Image
        import cairosvg
        
        # Convert SVG to PNG first
        png_data = cairosvg.svg2png(url=str(icon_svg), output_width=256, output_height=256)
        
        # Convert PNG to ICO
        image = Image.open(io.BytesIO(png_data))
        image.save(str(icon_ico), format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        
        print(f"✅ Icon created: {icon_ico}")
        return str(icon_ico)
        
    except ImportError:
        print("⚠️  PIL/cairosvg not available for icon conversion")
        return None
    except Exception as e:
        print(f"⚠️  Icon conversion failed: {e}")
        return None

def create_version_file():
    """Create Windows version info file"""
    print("🔧 Creating version info...")
    
    version_content = """VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'MAGI Project'),
        StringStruct(u'FileDescription', u'MAGI Distributed Monitoring System'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'MAGI'),
        StringStruct(u'LegalCopyright', u'Copyright © 2025 MAGI Project'),
        StringStruct(u'OriginalFilename', u'MAGI.exe'),
        StringStruct(u'ProductName', u'MAGI Distributed Monitoring'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""
    
    with open('version.txt', 'w') as f:
        f.write(version_content)
    
    print("✅ Version info created")
    return 'version.txt'

def build_executable(name, script, icon_path=None, version_file=None, windowed=True):
    """Build a single executable"""
    print(f"🧙‍♂️ Building {name} executable...")
    
    # Prepare PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', name,
        '--distpath', 'dist',
        '--workpath', 'build',
        '--specpath', 'build'
    ]
    
    if windowed:
        cmd.append('--windowed')
    
    if icon_path:
        cmd.extend(['--icon', icon_path])
    
    if version_file:
        cmd.extend(['--version-file', version_file])
    
    cmd.append(script)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {name} executable created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build {name}: {e}")
        print(f"   Error output: {e.stderr}")
        return False

def create_launchers():
    """Create batch file launchers for each node"""
    print("🔧 Creating node launchers...")
    
    dist_dir = Path('dist')
    dist_dir.mkdir(exist_ok=True)
    
    nodes = ['GASPAR', 'MELCHIOR', 'BALTASAR']
    
    for node in nodes:
        launcher_content = f"""@echo off
title 🧙‍♂️ MAGI {node} Node
color 0C
echo.
echo 🧙‍♂️ ═══════════════════════════════════════
echo      MAGI {node} Node Starting...
echo ═══════════════════════════════════════
echo.
echo 🌐 Dashboard: http://localhost:8081
echo ⏱️  Starting server...
echo.
"%~dp0MAGI-{node}.exe" {node}
echo.
echo 🛑 MAGI {node} stopped
pause
"""
        
        launcher_file = dist_dir / f'Start-MAGI-{node}.bat'
        launcher_file.write_text(launcher_content)
        print(f"✅ Created launcher: {launcher_file}")
    
    # Create dashboard opener
    dashboard_content = """@echo off
echo 🌐 Opening MAGI Dashboard...
timeout /t 1 /nobreak >nul
start http://localhost:8081
exit
"""
    
    dashboard_file = dist_dir / 'Open-MAGI-Dashboard.bat'
    dashboard_file.write_text(dashboard_content)
    print(f"✅ Created dashboard opener: {dashboard_file}")

def copy_additional_files():
    """Copy additional files to distribution"""
    print("📁 Copying additional files...")
    
    dist_dir = Path('dist')
    files_to_copy = [
        'README-Windows.md',
        'magi.conf',
        'magi-icon.svg',
        'magi-icon.ico'
    ]
    
    for file_name in files_to_copy:
        src_file = Path(file_name)
        if src_file.exists():
            shutil.copy2(src_file, dist_dir)
            print(f"✅ Copied: {file_name}")

def create_distribution_readme():
    """Create README for the distribution"""
    print("📝 Creating distribution README...")
    
    readme_content = """# 🧙‍♂️ MAGI Windows Executables

This folder contains standalone MAGI executables for Windows.
**No Python installation required on target machines!**

## 🚀 Quick Start

### Choose Your Node:
- **GASPAR** (Multimedia): Double-click `Start-MAGI-GASPAR.bat`
- **MELCHIOR** (Backup): Double-click `Start-MAGI-MELCHIOR.bat`  
- **BALTASAR** (Automation): Double-click `Start-MAGI-BALTASAR.bat`

### Access Dashboard:
- Double-click `Open-MAGI-Dashboard.bat`
- Or go to: http://localhost:8081

## 📁 Files Included

- `MAGI-*.exe` - Standalone node executables
- `Start-MAGI-*.bat` - Easy launcher scripts
- `Open-MAGI-Dashboard.bat` - Dashboard opener
- `MAGI-Installer.exe` - Universal installer
- `README.txt` - This file

## 🔧 Advanced Usage

Run directly from command line:
```cmd
MAGI-GASPAR.exe GASPAR
MAGI-MELCHIOR.exe MELCHIOR
MAGI-BALTASAR.exe BALTASAR
```

## 🌐 Network Setup

By default, nodes use these IPs:
- GASPAR: 192.168.1.100:8081
- MELCHIOR: 192.168.1.101:8081
- BALTASAR: 192.168.1.102:8081

Edit the executable's config if needed.

## 🎯 Deployment

1. Copy this entire folder to target Windows machine
2. Run the appropriate launcher
3. Open dashboard in browser
4. Enjoy your Evangelion-themed monitoring!

🧙‍♂️ The MAGI system is ready for operation!
"""
    
    readme_file = Path('dist') / 'README.txt'
    readme_file.write_text(readme_content)
    print(f"✅ Distribution README created: {readme_file}")

def show_results():
    """Show build results"""
    print("\n🎉 MAGI Windows Executables Created Successfully!")
    print("═" * 63)
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ Distribution directory not found")
        return
    
    print(f"\n📁 Location: {dist_dir.absolute()}")
    
    # List executables
    exe_files = list(dist_dir.glob('*.exe'))
    if exe_files:
        print(f"\n🎯 Executables created:")
        for exe_file in exe_files:
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"   {exe_file.name}: {size_mb:.1f} MB")
    
    # List batch files
    bat_files = list(dist_dir.glob('*.bat'))
    if bat_files:
        print(f"\n🚀 Launchers created:")
        for bat_file in bat_files:
            print(f"   {bat_file.name}")
    
    print(f"\n💾 Total distribution size: {get_folder_size(dist_dir):.1f} MB")
    print(f"\n🌐 Ready for deployment! Copy '{dist_dir}' folder to any Windows machine.")
    print("🧙‍♂️ No Python installation required on target machines!")

def get_folder_size(folder_path):
    """Get folder size in MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = Path(dirpath) / filename
            total_size += filepath.stat().st_size
    return total_size / (1024 * 1024)

def main():
    """Main build function"""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Create icon and version info
    icon_path = create_icon()
    version_file = create_version_file()
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for dir_name in ['build', 'dist']:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
    
    # Build executables
    success = True
    
    # Build node executables
    nodes = ['GASPAR', 'MELCHIOR', 'BALTASAR']
    for node in nodes:
        if not build_executable(f'MAGI-{node}', 'magi-node.py', icon_path, version_file, windowed=False):
            success = False
    
    # Build installer
    if not build_executable('MAGI-Installer', 'install-universal.py', icon_path, version_file, windowed=False):
        success = False
    
    if not success:
        print("❌ Some builds failed. Check errors above.")
        return False
    
    # Create additional files
    create_launchers()
    copy_additional_files()
    create_distribution_readme()
    
    # Show results
    show_results()
    
    # Cleanup
    for temp_file in ['version.txt']:
        if Path(temp_file).exists():
            Path(temp_file).unlink()
    
    print(f"\n🎉 Build complete! All files ready in 'dist' folder.")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build error: {e}")
        sys.exit(1)
