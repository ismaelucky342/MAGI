#!/usr/bin/env python3
"""
🔋 MAGI Power Save Mode Controller
Automatically manage system power states for energy efficiency
"""

import os
import sys
import time
import subprocess
import psutil
import json
import threading
from datetime import datetime, timedelta

class MAGIPowerManager:
    def __init__(self):
        self.config = {
            "idle_threshold_minutes": 30,     # Enter power save after 30 min idle
            "low_power_threshold_minutes": 60,  # Enter low power after 60 min idle
            "cpu_threshold": 10,              # Below 10% CPU = idle
            "check_interval": 60,             # Check every minute
            "services_to_manage": [
                "docker",
                "nginx", 
                "apache2",
                "mysql",
                "postgresql"
            ],
            "log_file": "/tmp/magi-power.log"
        }
        
        self.current_state = "normal"
        self.last_activity = datetime.now()
        self.running = True
        
        print("🔋 MAGI Power Save Mode - Initialized")
        print(f"📊 Idle threshold: {self.config['idle_threshold_minutes']} minutes")
        print(f"🔋 Low power threshold: {self.config['low_power_threshold_minutes']} minutes")
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        try:
            with open(self.config["log_file"], "a") as f:
                f.write(log_msg + "\n")
        except:
            pass
    
    def get_system_activity(self):
        """Check system activity level"""
        try:
            # CPU usage over 5 seconds
            cpu_percent = psutil.cpu_percent(interval=5)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Network I/O
            net_before = psutil.net_io_counters()
            time.sleep(1)
            net_after = psutil.net_io_counters()
            
            net_activity = (net_after.bytes_sent - net_before.bytes_sent + 
                          net_after.bytes_recv - net_before.bytes_recv)
            
            # Disk I/O
            disk_before = psutil.disk_io_counters()
            time.sleep(1)
            disk_after = psutil.disk_io_counters()
            
            disk_activity = (disk_after.read_bytes - disk_before.read_bytes + 
                           disk_after.write_bytes - disk_before.write_bytes)
            
            return {
                "cpu": cpu_percent,
                "memory": memory.percent,
                "network_bytes": net_activity,
                "disk_bytes": disk_activity,
                "processes": len(psutil.pids())
            }
            
        except Exception as e:
            self.log(f"❌ Error checking activity: {e}")
            return None
    
    def is_system_idle(self, activity):
        """Determine if system is idle"""
        if not activity:
            return False
            
        # System is idle if:
        # - CPU < threshold
        # - Low network activity (< 1MB/minute)
        # - Low disk activity (< 10MB/minute)
        
        return (activity["cpu"] < self.config["cpu_threshold"] and
                activity["network_bytes"] < 1024*1024 and  # 1MB
                activity["disk_bytes"] < 10*1024*1024)     # 10MB
    
    def manage_services(self, action):
        """Manage system services for power saving"""
        if action == "stop_non_essential":
            services_to_stop = ["docker", "mysql", "postgresql"]
            for service in services_to_stop:
                try:
                    result = subprocess.run(
                        ["systemctl", "is-active", service], 
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:  # Service is running
                        subprocess.run(["sudo", "systemctl", "stop", service])
                        self.log(f"🛑 Stopped service: {service}")
                except Exception as e:
                    self.log(f"❌ Error stopping {service}: {e}")
                    
        elif action == "start_essential":
            services_to_start = ["ssh", "network-manager"]
            for service in services_to_start:
                try:
                    subprocess.run(["sudo", "systemctl", "start", service])
                    self.log(f"🟢 Started service: {service}")
                except Exception as e:
                    self.log(f"❌ Error starting {service}: {e}")
    
    def apply_power_state(self, new_state):
        """Apply power management settings"""
        if new_state == self.current_state:
            return
            
        self.log(f"🔄 Changing power state: {self.current_state} → {new_state}")
        
        try:
            if new_state == "power_save":
                # Set CPU governor to powersave
                subprocess.run([
                    "sudo", "bash", "-c", 
                    "echo powersave | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
                ], capture_output=True)
                
                # Reduce screen brightness (if available)
                try:
                    subprocess.run([
                        "sudo", "bash", "-c",
                        "echo 30 > /sys/class/backlight/*/brightness 2>/dev/null || true"
                    ])
                except:
                    pass
                
                self.log("🔋 Applied power save settings")
                
            elif new_state == "low_power":
                # More aggressive power saving
                subprocess.run([
                    "sudo", "bash", "-c", 
                    "echo powersave | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
                ], capture_output=True)
                
                # Stop non-essential services
                self.manage_services("stop_non_essential")
                
                # Sync and drop caches
                subprocess.run(["sync"])
                subprocess.run([
                    "sudo", "bash", "-c",
                    "echo 3 > /proc/sys/vm/drop_caches"
                ])
                
                self.log("🔋 Applied low power settings")
                
            elif new_state == "normal":
                # Restore performance
                subprocess.run([
                    "sudo", "bash", "-c", 
                    "echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || echo ondemand | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
                ], capture_output=True)
                
                # Restore screen brightness
                try:
                    subprocess.run([
                        "sudo", "bash", "-c",
                        "echo 100 > /sys/class/backlight/*/brightness 2>/dev/null || true"
                    ])
                except:
                    pass
                
                self.log("⚡ Restored normal performance")
                
        except Exception as e:
            self.log(f"❌ Error applying power state: {e}")
        
        self.current_state = new_state
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.log("🔋 Starting power monitoring loop")
        
        while self.running:
            try:
                activity = self.get_system_activity()
                
                if activity:
                    current_time = datetime.now()
                    
                    if self.is_system_idle(activity):
                        # System is idle
                        idle_minutes = (current_time - self.last_activity).total_seconds() / 60
                        
                        if idle_minutes >= self.config["low_power_threshold_minutes"]:
                            self.apply_power_state("low_power")
                        elif idle_minutes >= self.config["idle_threshold_minutes"]:
                            self.apply_power_state("power_save")
                            
                    else:
                        # System is active
                        self.last_activity = current_time
                        self.apply_power_state("normal")
                        
                    # Log current status every 10 minutes
                    if int(current_time.timestamp()) % 600 == 0:
                        idle_time = (current_time - self.last_activity).total_seconds() / 60
                        self.log(f"📊 Status: {self.current_state} | CPU: {activity['cpu']:.1f}% | Idle: {idle_time:.1f}min")
                
                time.sleep(self.config["check_interval"])
                
            except KeyboardInterrupt:
                self.log("🛑 Power manager stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Error in monitoring loop: {e}")
                time.sleep(30)  # Wait before retrying
    
    def get_status(self):
        """Get current power status"""
        idle_time = (datetime.now() - self.last_activity).total_seconds() / 60
        return {
            "state": self.current_state,
            "idle_minutes": idle_time,
            "last_activity": self.last_activity.isoformat()
        }
    
    def force_state(self, state):
        """Force a specific power state"""
        if state in ["normal", "power_save", "low_power"]:
            self.apply_power_state(state)
            self.log(f"🔧 Forced power state: {state}")
            return True
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MAGI Power Save Mode Controller")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--force", choices=["normal", "power_save", "low_power"], 
                       help="Force specific power state")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    power_manager = MAGIPowerManager()
    
    if args.status:
        status = power_manager.get_status()
        print(f"🔋 Power State: {status['state']}")
        print(f"⏱️  Idle Time: {status['idle_minutes']:.1f} minutes")
        print(f"📅 Last Activity: {status['last_activity']}")
        return
    
    if args.force:
        if power_manager.force_state(args.force):
            print(f"✅ Power state changed to: {args.force}")
        else:
            print(f"❌ Invalid power state: {args.force}")
        return
    
    if args.daemon:
        print("🔋 Starting MAGI Power Manager as daemon...")
        try:
            power_manager.monitor_loop()
        except KeyboardInterrupt:
            print("\n🛑 Power manager stopped")
    else:
        print("🔋 MAGI Power Save Mode")
        print("Usage:")
        print("  python3 power-save-mode.py --daemon     # Run as daemon")
        print("  python3 power-save-mode.py --status     # Show status")
        print("  python3 power-save-mode.py --force normal  # Force normal mode")

if __name__ == "__main__":
    main()
