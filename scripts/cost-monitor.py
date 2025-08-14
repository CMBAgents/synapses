#!/usr/bin/env python3
"""
GCP Cost Monitoring and Tracking Script
Monitors and tracks costs for the CMB Agent Info project.
"""

import os
import json
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path
import csv
import sqlite3
from typing import Dict, List, Optional, Tuple
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cost-monitor.log'),
        logging.StreamHandler()
    ]
)

class GCPCostMonitor:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.cost_data_dir = self.base_dir / "cost-data"
        self.cost_data_dir.mkdir(exist_ok=True)
        
        # Database for cost tracking
        self.db_path = self.cost_data_dir / "costs.db"
        self.init_database()
        
        # Configuration files
        self.config_file = self.base_dir / "gestion" / "config" / "budget-config.json"
        self.cost_history_file = self.cost_data_dir / "cost-history.json"
        self.budget_alerts_file = self.cost_data_dir / "budget-alerts.json"
        
        # Load configuration
        self.config = self.load_config()
        
        # Cost thresholds
        self.monthly_budget = 15.0  # USD
        self.daily_budget = 0.50    # USD
        self.alert_threshold = 0.8  # 80% of budget

    def init_database(self):
        """Initialize SQLite database for cost tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_costs (
                date TEXT PRIMARY KEY,
                cloud_run REAL DEFAULT 0,
                cloud_functions REAL DEFAULT 0,
                cloud_storage REAL DEFAULT 0,
                cloud_scheduler REAL DEFAULT 0,
                total REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_usage (
                date TEXT,
                service TEXT,
                metric TEXT,
                value REAL,
                unit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (date, service, metric)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                alert_type TEXT,
                message TEXT,
                threshold REAL,
                actual REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def load_config(self) -> Dict:
        """Load project configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading config: {e}")
        
        return {}

    def get_project_id(self) -> Optional[str]:
        """Get GCP project ID."""
        try:
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logging.error(f"Error getting project ID: {e}")
        
        return self.config.get('project_id')

    def get_billing_account(self) -> Optional[str]:
        """Get billing account ID."""
        try:
            result = subprocess.run(
                ["gcloud", "billing", "accounts", "list", "--format=value(ACCOUNT_ID)"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
        except Exception as e:
            logging.error(f"Error getting billing account: {e}")
        
        return None

    def get_daily_costs(self, date: str = None) -> Dict:
        """Get daily costs from GCP Billing API."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        project_id = self.get_project_id()
        billing_account = self.get_billing_account()
        
        if not project_id or not billing_account:
            logging.error("Project ID or billing account not found")
            return {}
        
        try:
            # Get costs for the specific date
            cmd = [
                "gcloud", "billing", "budgets", "list",
                "--billing-account", billing_account,
                "--format", "json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse billing data
                costs = self.parse_billing_data(result.stdout, date)
                return costs
            else:
                logging.error(f"Error getting billing data: {result.stderr}")
                
        except Exception as e:
            logging.error(f"Error getting daily costs: {e}")
        
        return {}

    def parse_billing_data(self, billing_json: str, date: str) -> Dict:
        """Parse billing data from GCP."""
        try:
            data = json.loads(billing_json)
            
            # Initialize cost structure
            costs = {
                'cloud_run': 0.0,
                'cloud_functions': 0.0,
                'cloud_storage': 0.0,
                'cloud_scheduler': 0.0,
                'total': 0.0
            }
            
            # Parse costs by service
            for item in data:
                service = item.get('service', '').lower()
                amount = float(item.get('cost', 0))
                
                if 'cloud run' in service:
                    costs['cloud_run'] += amount
                elif 'cloud functions' in service:
                    costs['cloud_functions'] += amount
                elif 'cloud storage' in service:
                    costs['cloud_storage'] += amount
                elif 'cloud scheduler' in service:
                    costs['cloud_scheduler'] += amount
                
                costs['total'] += amount
            
            return costs
            
        except Exception as e:
            logging.error(f"Error parsing billing data: {e}")
            return {}

    def get_service_usage(self, date: str = None) -> Dict:
        """Get service usage metrics."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        project_id = self.get_project_id()
        if not project_id:
            return {}
        
        usage = {}
        
        try:
            # Cloud Run usage
            cmd = [
                "gcloud", "run", "services", "list",
                "--region", "us-central1",
                "--format", "value(metadata.name,status.url)"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                services = result.stdout.strip().split('\n')
                usage['cloud_run_services'] = len(services) if services[0] else 0
            
            # Cloud Storage usage
            cmd = [
                "gsutil", "du", "-sh", f"gs://{project_id}-contexts"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                usage['storage_size'] = result.stdout.strip()
            
            # Cloud Functions usage
            cmd = [
                "gcloud", "functions", "list",
                "--format", "value(name)"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                functions = result.stdout.strip().split('\n')
                usage['cloud_functions_count'] = len(functions) if functions[0] else 0
            
        except Exception as e:
            logging.error(f"Error getting service usage: {e}")
        
        return usage

    def save_daily_costs(self, date: str, costs: Dict, usage: Dict):
        """Save daily costs to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert daily costs
            cursor.execute('''
                INSERT OR REPLACE INTO daily_costs 
                (date, cloud_run, cloud_functions, cloud_storage, cloud_scheduler, total)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                date,
                costs.get('cloud_run', 0),
                costs.get('cloud_functions', 0),
                costs.get('cloud_storage', 0),
                costs.get('cloud_scheduler', 0),
                costs.get('total', 0)
            ))
            
            # Insert service usage
            for service, metrics in usage.items():
                if isinstance(metrics, dict):
                    for metric, value in metrics.items():
                        cursor.execute('''
                            INSERT OR REPLACE INTO service_usage 
                            (date, service, metric, value, unit)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (date, service, metric, value, 'count'))
                else:
                    cursor.execute('''
                        INSERT OR REPLACE INTO service_usage 
                        (date, service, metric, value, unit)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (date, 'general', service, metrics, 'count'))
            
            conn.commit()
            
        except Exception as e:
            logging.error(f"Error saving daily costs: {e}")
        finally:
            conn.close()

    def check_budget_alerts(self, costs: Dict, date: str):
        """Check if costs exceed budget thresholds."""
        total_cost = costs.get('total', 0)
        
        # Daily budget alert
        if total_cost > self.daily_budget:
            self.create_alert(
                date, 'daily_budget_exceeded',
                f"Daily budget exceeded: ${total_cost:.2f} > ${self.daily_budget}",
                self.daily_budget, total_cost
            )
        
        # Monthly budget alert (estimate)
        monthly_estimate = total_cost * 30
        if monthly_estimate > self.monthly_budget:
            self.create_alert(
                date, 'monthly_budget_warning',
                f"Monthly budget warning: estimated ${monthly_estimate:.2f} > ${self.monthly_budget}",
                self.monthly_budget, monthly_estimate
            )

    def create_alert(self, date: str, alert_type: str, message: str, threshold: float, actual: float):
        """Create a budget alert."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO cost_alerts (date, alert_type, message, threshold, actual)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, alert_type, message, threshold, actual))
            
            conn.commit()
            
            # Log alert
            logging.warning(f"BUDGET ALERT: {message}")
            
        except Exception as e:
            logging.error(f"Error creating alert: {e}")
        finally:
            conn.close()

    def get_cost_summary(self, days: int = 30) -> Dict:
        """Get cost summary for the last N days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get daily costs
            cursor.execute('''
                SELECT date, cloud_run, cloud_functions, cloud_storage, cloud_scheduler, total
                FROM daily_costs
                WHERE date >= date('now', '-{} days')
                ORDER BY date DESC
            '''.format(days))
            
            rows = cursor.fetchall()
            
            summary = {
                'period_days': days,
                'total_cost': 0.0,
                'daily_average': 0.0,
                'services': {
                    'cloud_run': 0.0,
                    'cloud_functions': 0.0,
                    'cloud_storage': 0.0,
                    'cloud_scheduler': 0.0
                },
                'daily_costs': []
            }
            
            for row in rows:
                date, cloud_run, cloud_functions, cloud_storage, cloud_scheduler, total = row
                
                summary['total_cost'] += total
                summary['services']['cloud_run'] += cloud_run
                summary['services']['cloud_functions'] += cloud_functions
                summary['services']['cloud_storage'] += cloud_storage
                summary['services']['cloud_scheduler'] += cloud_scheduler
                
                summary['daily_costs'].append({
                    'date': date,
                    'total': total,
                    'cloud_run': cloud_run,
                    'cloud_functions': cloud_functions,
                    'cloud_storage': cloud_storage,
                    'cloud_scheduler': cloud_scheduler
                })
            
            if rows:
                summary['daily_average'] = summary['total_cost'] / len(rows)
            
            return summary
            
        except Exception as e:
            logging.error(f"Error getting cost summary: {e}")
            return {}
        finally:
            conn.close()

    def generate_cost_report(self, days: int = 30) -> str:
        """Generate a detailed cost report."""
        summary = self.get_cost_summary(days)
        
        if not summary:
            return "No cost data available."
        
        report = []
        report.append("=" * 60)
        report.append("💰 GCP COST REPORT")
        report.append("=" * 60)
        report.append(f"Period: Last {days} days")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Total costs
        report.append("📊 TOTAL COSTS:")
        report.append(f"  Total: ${summary['total_cost']:.2f}")
        report.append(f"  Daily Average: ${summary['daily_average']:.2f}")
        report.append(f"  Monthly Estimate: ${summary['daily_average'] * 30:.2f}")
        report.append("")
        
        # Service breakdown
        report.append("🔧 SERVICE BREAKDOWN:")
        services = summary['services']
        for service, cost in services.items():
            percentage = (cost / summary['total_cost'] * 100) if summary['total_cost'] > 0 else 0
            report.append(f"  {service.replace('_', ' ').title()}: ${cost:.2f} ({percentage:.1f}%)")
        report.append("")
        
        # Budget comparison
        report.append("🎯 BUDGET COMPARISON:")
        monthly_estimate = summary['daily_average'] * 30
        budget_usage = (monthly_estimate / self.monthly_budget * 100) if self.monthly_budget > 0 else 0
        report.append(f"  Monthly Budget: ${self.monthly_budget}")
        report.append(f"  Monthly Estimate: ${monthly_estimate:.2f}")
        report.append(f"  Budget Usage: {budget_usage:.1f}%")
        
        if budget_usage > 100:
            report.append("  ⚠️  OVER BUDGET!")
        elif budget_usage > 80:
            report.append("  ⚠️  APPROACHING BUDGET LIMIT")
        else:
            report.append("  ✅ WITHIN BUDGET")
        report.append("")
        
        # Recent daily costs
        report.append("📅 RECENT DAILY COSTS:")
        for daily in summary['daily_costs'][:7]:  # Last 7 days
            report.append(f"  {daily['date']}: ${daily['total']:.2f}")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        if summary['daily_average'] > 0.5:
            report.append("  • Consider reducing Cloud Run resources")
            report.append("  • Optimize Cloud Functions frequency")
        if services['cloud_storage'] > 2.0:
            report.append("  • Review Cloud Storage usage")
            report.append("  • Consider lifecycle policies")
        if budget_usage > 80:
            report.append("  • Set up budget alerts")
            report.append("  • Review resource allocation")
        
        report.append("=" * 60)
        
        return "\n".join(report)

    def export_cost_data(self, format: str = 'csv', days: int = 30):
        """Export cost data to CSV or JSON."""
        summary = self.get_cost_summary(days)
        
        if not summary:
            logging.error("No cost data to export")
            return
        
        if format.lower() == 'csv':
            filename = self.cost_data_dir / f"cost-report-{datetime.now().strftime('%Y%m%d')}.csv"
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Date', 'Total', 'Cloud Run', 'Cloud Functions', 'Cloud Storage', 'Cloud Scheduler'])
                
                for daily in summary['daily_costs']:
                    writer.writerow([
                        daily['date'],
                        daily['total'],
                        daily['cloud_run'],
                        daily['cloud_functions'],
                        daily['cloud_storage'],
                        daily['cloud_scheduler']
                    ])
            
            logging.info(f"Cost data exported to {filename}")
            
        elif format.lower() == 'json':
            filename = self.cost_data_dir / f"cost-report-{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(filename, 'w') as jsonfile:
                json.dump(summary, jsonfile, indent=2)
            
            logging.info(f"Cost data exported to {filename}")

    def run_daily_check(self):
        """Run daily cost check and save data."""
        logging.info("🔄 Running daily cost check...")
        
        date = datetime.now().strftime('%Y-%m-%d')
        
        # Get costs and usage
        costs = self.get_daily_costs(date)
        usage = self.get_service_usage(date)
        
        # Save data
        self.save_daily_costs(date, costs, usage)
        
        # Check budget alerts
        self.check_budget_alerts(costs, date)
        
        # Generate report
        report = self.generate_cost_report(1)
        logging.info(f"Daily cost check completed:\n{report}")
        
        return costs

def main():
    """Main function."""
    import sys
    
    monitor = GCPCostMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "daily":
            monitor.run_daily_check()
        elif command == "report":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            report = monitor.generate_cost_report(days)
            print(report)
        elif command == "export":
            format = sys.argv[2] if len(sys.argv) > 2 else 'csv'
            days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
            monitor.export_cost_data(format, days)
        elif command == "summary":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            summary = monitor.get_cost_summary(days)
            print(json.dumps(summary, indent=2))
        else:
            print("Available commands:")
            print("  daily   - Run daily cost check")
            print("  report [days] - Generate cost report")
            print("  export [format] [days] - Export cost data (csv/json)")
            print("  summary [days] - Get cost summary")
    else:
        # Run daily check by default
        monitor.run_daily_check()

if __name__ == "__main__":
    main() 