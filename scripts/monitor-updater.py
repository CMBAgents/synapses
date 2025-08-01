#!/usr/bin/env python3
"""
Monitoring script for the automated context updater.
Checks the status and provides statistics.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import subprocess
import sys

class ContextUpdaterMonitor:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.state_file = self.base_dir / "context_update_state.json"
        self.log_file = self.base_dir / "auto_update.log"

    def check_service_status(self):
        """Checks if the systemd service is running."""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "context-updater"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == "active"
        except Exception:
            return False

    def get_service_logs(self, lines: int = 20):
        """Gets recent service logs."""
        try:
            result = subprocess.run(
                ["journalctl", "-u", "context-updater", "-n", str(lines), "--no-pager"],
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e:
            return f"Error getting logs: {e}"

    def load_state(self):
        """Loads the update state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading state: {e}")
        
        return {}

    def get_context_stats(self):
        """Gets statistics about existing contexts."""
        context_dir = self.base_dir / "app" / "context"
        stats = {}
        
        if context_dir.exists():
            for domain_dir in context_dir.iterdir():
                if domain_dir.is_dir():
                    domain = domain_dir.name
                    context_files = list(domain_dir.glob("*.txt"))
                    stats[domain] = len(context_files)
        
        return stats

    def get_latest_log_entries(self, lines: int = 10):
        """Gets latest log entries from the log file."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    return all_lines[-lines:] if len(all_lines) > lines else all_lines
            except Exception as e:
                return [f"Error reading log file: {e}"]
        return ["No log file found"]

    def display_status(self):
        """Displays comprehensive status information."""
        print("=" * 60)
        print("CONTEXT AUTO UPDATER MONITOR")
        print("=" * 60)
        
        # Service status
        service_running = self.check_service_status()
        status_icon = "🟢" if service_running else "🔴"
        print(f"{status_icon} Service Status: {'Running' if service_running else 'Stopped'}")
        
        # State information
        state = self.load_state()
        if state:
            print(f"\n📊 State Information:")
            if state.get("last_check"):
                last_check = datetime.fromisoformat(state["last_check"])
                print(f"   Last check: {last_check.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if state.get("last_update"):
                last_update = datetime.fromisoformat(state["last_update"])
                print(f"   Last update: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
            
            update_count = state.get("update_count", 0)
            print(f"   Total updates: {update_count}")
            
            repo_count = len(state.get("repository_hashes", {}))
            print(f"   Tracked repositories: {repo_count}")
        else:
            print(f"\n📊 State Information: No state file found")
        
        # Context statistics
        context_stats = self.get_context_stats()
        if context_stats:
            print(f"\n📁 Context Statistics:")
            total_contexts = sum(context_stats.values())
            print(f"   Total contexts: {total_contexts}")
            for domain, count in context_stats.items():
                print(f"   {domain}: {count} contexts")
        else:
            print(f"\n📁 Context Statistics: No contexts found")
        
        # Recent logs
        print(f"\n📋 Recent Log Entries:")
        log_entries = self.get_latest_log_entries(5)
        for entry in log_entries:
            print(f"   {entry.strip()}")
        
        print("\n" + "=" * 60)

    def display_service_logs(self, lines: int = 20):
        """Displays service logs."""
        print(f"\n📋 Service Logs (last {lines} lines):")
        print("-" * 60)
        logs = self.get_service_logs(lines)
        print(logs)

    def restart_service(self):
        """Restarts the service."""
        try:
            print("🔄 Restarting context-updater service...")
            subprocess.run(["sudo", "systemctl", "restart", "context-updater"], check=True)
            print("✅ Service restarted successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error restarting service: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def start_service(self):
        """Starts the service."""
        try:
            print("🚀 Starting context-updater service...")
            subprocess.run(["sudo", "systemctl", "start", "context-updater"], check=True)
            print("✅ Service started successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error starting service: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def stop_service(self):
        """Stops the service."""
        try:
            print("🛑 Stopping context-updater service...")
            subprocess.run(["sudo", "systemctl", "stop", "context-updater"], check=True)
            print("✅ Service stopped successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error stopping service: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function."""
    monitor = ContextUpdaterMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            monitor.display_status()
        elif command == "logs":
            lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            monitor.display_service_logs(lines)
        elif command == "restart":
            monitor.restart_service()
        elif command == "start":
            monitor.start_service()
        elif command == "stop":
            monitor.stop_service()
        else:
            print("Available commands:")
            print("  status   - Show comprehensive status")
            print("  logs [n] - Show service logs (default: 20 lines)")
            print("  restart  - Restart the service")
            print("  start    - Start the service")
            print("  stop     - Stop the service")
    else:
        # Show status by default
        monitor.display_status()

if __name__ == "__main__":
    main() 