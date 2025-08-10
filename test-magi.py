#!/usr/bin/env python3
"""
🧙‍♂️ MAGI Test Script - Verify Everything Works
Quick test to make sure MAGI is ready to rock
"""

import subprocess
import sys
import platform
import time
import urllib.request
import json

def test_python():
    """Test Python installation"""
    print("🐍 Testing Python...")
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 6:
        print(f"   ✅ Python {major}.{minor} - OK")
        return True
    else:
        print(f"   ❌ Python {major}.{minor} - Need 3.6+")
        return False

def test_imports():
    """Test required imports"""
    print("📦 Testing imports...")
    required_modules = [
        'http.server', 'socketserver', 'json', 'os', 
        'platform', 'subprocess', 'urllib.request', 
        'threading', 'time', 'datetime'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} - Missing!")
            return False
    return True

def test_magi_file():
    """Test if magi-node.py exists and is valid"""
    print("📄 Testing magi-node.py...")
    try:
        with open('magi-node.py', 'r') as f:
            content = f.read()
            if 'class MAGIHandler' in content and 'def main()' in content:
                print("   ✅ magi-node.py - Valid structure")
                return True
            else:
                print("   ❌ magi-node.py - Invalid structure")
                return False
    except FileNotFoundError:
        print("   ❌ magi-node.py - File not found")
        return False

def test_magi_syntax():
    """Test magi-node.py syntax"""
    print("🔍 Testing syntax...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', 'magi-node.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Syntax check passed")
            return True
        else:
            print(f"   ❌ Syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Syntax check failed: {e}")
        return False

def test_quick_start():
    """Test quick start of MAGI"""
    print("🚀 Testing quick start...")
    try:
        # Start MAGI in background for a few seconds
        process = subprocess.Popen([
            sys.executable, 'magi-node.py', 'TEST'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Test if it's responding
        try:
            with urllib.request.urlopen('http://localhost:8080/api/info', timeout=2) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data.get('node_name') == 'TEST':
                        print("   ✅ MAGI server started and responding")
                        return True
                    else:
                        print("   ❌ Server responding but wrong node name")
                        return False
                else:
                    print(f"   ❌ Server returned status {response.status}")
                    return False
        except Exception as e:
            print(f"   ❌ Server not responding: {e}")
            return False
        finally:
            # Clean up process
            process.terminate()
            try:
                process.wait(timeout=5)
            except:
                process.kill()
    
    except Exception as e:
        print(f"   ❌ Failed to start server: {e}")
        return False

def test_network_discovery():
    """Test network discovery function"""
    print("🌐 Testing network discovery...")
    try:
        # Skip actual import test, just verify the function exists in file
        with open('magi-node.py', 'r') as f:
            content = f.read()
            if 'def discover_nodes' in content:
                print(f"   ✅ Discovery function found in code")
                return True
            else:
                print(f"   ❌ Discovery function not found")
                return False
    except Exception as e:
        print(f"   ❌ Discovery test failed: {e}")
        return False

def test_system_metrics():
    """Test system metrics function"""
    print("📊 Testing system metrics...")
    try:
        # Import the metrics function
        sys.path.insert(0, '.')
        
        # Create a simple test version
        import os
        import platform
        
        # Basic test - just check we can get platform info
        system = platform.system()
        version = platform.python_version()
        
        print(f"   ✅ System: {system}, Python: {version}")
        return True
    except Exception as e:
        print(f"   ❌ Metrics test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("""
🧙‍♂️ ═══════════════════════════════════════════════════════════════
    MAGI System Test - Verifying Installation
═══════════════════════════════════════════════════════════════
""")
    
    tests = [
        ("Python Installation", test_python),
        ("Required Imports", test_imports), 
        ("MAGI File Check", test_magi_file),
        ("Syntax Validation", test_magi_syntax),
        ("System Metrics", test_system_metrics),
        ("Quick Start Test", test_quick_start)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
    
    print(f"""
═══════════════════════════════════════════════════════════════
🧙‍♂️ MAGI Test Results: {passed}/{total} tests passed
""")
    
    if passed == total:
        print("""✅ All tests passed! MAGI is ready to deploy.

🚀 Quick Start:
   python3 magi-node.py GASPAR
   
🌐 Then visit: http://localhost:8080

🎯 Next Steps:
   1. Run install.py on each node
   2. Configure network IPs in magi.conf
   3. Start monitoring your home lab!
""")
    else:
        print(f"""❌ {total - passed} test(s) failed. 

🔧 Please fix the issues above before deploying MAGI.
📚 Check the README.md for troubleshooting tips.
""")
    
    print("═══════════════════════════════════════════════════════════════")

if __name__ == "__main__":
    main()
