"""
Report Generation Module
Generates Vehicle Count, Parking Usage, Daily Revenue, and Overall Statistics Reports
"""

import csv
import os
from datetime import datetime, timedelta
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import config


class ReportGenerator:
    """Generate various reports from traffic and rental data"""
    
    def __init__(self, database):
        """
        Initialize report generator
        
        Args:
            database: CSVDatabase instance
        """
        self.database = database
        self.reports_dir = os.path.join(config.BASE_DIR, 'reports')
        
        # Create reports directory
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_vehicle_count_report(self, date=None):
        """
        Generate vehicle count report
        
        Args:
            date: Date for report (defaults to today)
        
        Returns:
            Report file path
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        report_path = os.path.join(
            self.reports_dir,
            f'vehicle_count_report_{date}.txt'
        )
        
        # Get statistics
        stats = self.database.get_today_stats()
        
        # Generate report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(" " * 15 + "VEHICLE COUNT REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Date: {date}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("-" * 60 + "\n")
            f.write("VEHICLE TYPE BREAKDOWN:\n")
            f.write("-" * 60 + "\n\n")
            f.write(f"🚗 Cars:        {stats['car']:>5}\n")
            f.write(f"🏍️  Motorcycles: {stats['motorcycle']:>5}\n")
            f.write(f"🚌 Buses:       {stats['bus']:>5}\n")
            f.write(f"🚚 Trucks:      {stats['truck']:>5}\n")
            f.write("-" * 60 + "\n")
            f.write(f"📊 TOTAL:       {stats['total']:>5}\n")
            f.write("=" * 60 + "\n")
        
        print(f"✓ Vehicle count report generated: {report_path}")
        return report_path
    
    def generate_parking_usage_report(self, date=None):
        """
        Generate parking usage report
        
        Args:
            date: Date for report (defaults to today)
        
        Returns:
            Report file path
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        report_path = os.path.join(
            self.reports_dir,
            f'parking_usage_report_{date}.txt'
        )
        
        # Get parking records
        logs = self.database.get_traffic_logs()
        
        # Count parking entries
        parking_entries = [
            log for log in logs 
            if log['action'] == 'entered' and log['timestamp'].startswith(date)
        ]
        
        parking_exits = [
            log for log in logs 
            if log['action'] == 'exited' and log['timestamp'].startswith(date)
        ]
        
        # Generate report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(" " * 15 + "PARKING USAGE REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Date: {date}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("-" * 60 + "\n")
            f.write("PARKING STATISTICS:\n")
            f.write("-" * 60 + "\n\n")
            f.write(f"Total Entries:     {len(parking_entries):>5}\n")
            f.write(f"Total Exits:       {len(parking_exits):>5}\n")
            f.write(f"Currently Parked:  {len(parking_entries) - len(parking_exits):>5}\n\n")
            f.write(f"Total Slots:       {config.TOTAL_PARKING_SLOTS:>5}\n")
            f.write(f"Occupancy Rate:    {((len(parking_entries) - len(parking_exits)) / config.TOTAL_PARKING_SLOTS * 100):.1f}%\n")
            f.write("=" * 60 + "\n")
        
        print(f"✓ Parking usage report generated: {report_path}")
        return report_path
    
    def generate_daily_revenue_report(self, date=None):
        """
        Generate daily rental revenue report
        
        Args:
            date: Date for report (defaults to today)
        
        Returns:
            Report file path
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        report_path = os.path.join(
            self.reports_dir,
            f'daily_revenue_report_{date}.txt'
        )
        
        # Get rental records
        rentals = self.database.get_rental_records()
        
        # Filter by date
        daily_rentals = [
            r for r in rentals 
            if r['entry_time'].startswith(date)
        ]
        
        # Calculate revenue by vehicle type
        revenue_breakdown = {
            'motorcycle': {'count': 0, 'revenue': 0.0},
            'car': {'count': 0, 'revenue': 0.0},
            'bus': {'count': 0, 'revenue': 0.0},
            'truck': {'count': 0, 'revenue': 0.0},
            'van': {'count': 0, 'revenue': 0.0}
        }
        
        total_revenue = 0.0
        total_discount = 0.0
        
        for rental in daily_rentals:
            vtype = rental.get('vehicle_type', '').lower()
            if vtype in revenue_breakdown:
                revenue_breakdown[vtype]['count'] += 1
                revenue_breakdown[vtype]['revenue'] += float(rental.get('total_rent', 0))
                total_revenue += float(rental.get('total_rent', 0))
                total_discount += float(rental.get('discount', 0))
        
        # Generate report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(" " * 15 + "DAILY REVENUE REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Date: {date}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("-" * 60 + "\n")
            f.write("REVENUE BY VEHICLE TYPE:\n")
            f.write("-" * 60 + "\n\n")
            
            for vtype, data in revenue_breakdown.items():
                if data['count'] > 0:
                    f.write(f"{vtype.capitalize():<15} Count: {data['count']:>3}  Revenue: {data['revenue']:>8.2f} PKR\n")
            
            f.write("\n" + "-" * 60 + "\n")
            f.write(f"Total Transactions: {len(daily_rentals)}\n")
            f.write(f"Total Discount:     {total_discount:>8.2f} PKR\n")
            f.write(f"TOTAL REVENUE:      {total_revenue:>8.2f} PKR\n")
            f.write("=" * 60 + "\n")
        
        print(f"✓ Daily revenue report generated: {report_path}")
        return report_path
    
    def generate_overall_statistics_report(self):
        """
        Generate overall traffic statistics report
        
        Returns:
            Report file path
        """
        date = datetime.now().strftime('%Y-%m-%d')
        
        report_path = os.path.join(
            self.reports_dir,
            f'overall_statistics_{date}.txt'
        )
        
        # Get all data
        all_logs = self.database.get_traffic_logs(limit=None)
        all_rentals = self.database.get_rental_records(limit=None)
        
        # Calculate statistics
        total_vehicles = len([log for log in all_logs if log['action'] == 'counted'])
        total_revenue = sum(float(r.get('total_rent', 0)) for r in all_rentals)
        total_rentals = len(all_rentals)
        
        # Vehicle type breakdown
        vehicle_counts = {
            'car': 0,
            'motorcycle': 0,
            'bus': 0,
            'truck': 0
        }
        
        for log in all_logs:
            if log['action'] == 'counted':
                vtype = log.get('vehicle_type', '').lower()
                if vtype in vehicle_counts:
                    vehicle_counts[vtype] += 1
        
        # Generate report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(" " * 12 + "OVERALL TRAFFIC STATISTICS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("-" * 60 + "\n")
            f.write("CUMULATIVE VEHICLE COUNTS:\n")
            f.write("-" * 60 + "\n\n")
            f.write(f"Total Vehicles Counted:  {total_vehicles}\n\n")
            f.write(f"  Cars:        {vehicle_counts['car']}\n")
            f.write(f"  Motorcycles: {vehicle_counts['motorcycle']}\n")
            f.write(f"  Buses:       {vehicle_counts['bus']}\n")
            f.write(f"  Trucks:      {vehicle_counts['truck']}\n\n")
            f.write("-" * 60 + "\n")
            f.write("RENTAL STATISTICS:\n")
            f.write("-" * 60 + "\n\n")
            f.write(f"Total Rentals:       {total_rentals}\n")
            f.write(f"Total Revenue:       {total_revenue:>10.2f} PKR\n")
            if total_rentals > 0:
                f.write(f"Average per Rental:  {(total_revenue/total_rentals):>10.2f} PKR\n")
            f.write("\n" + "=" * 60 + "\n")
        
        print(f"✓ Overall statistics report generated: {report_path}")
        return report_path
    
    def generate_all_reports(self, date=None):
        """
        Generate all reports
        
        Args:
            date: Date for reports (defaults to today)
        
        Returns:
            Dictionary of report paths
        """
        print("\nGenerating all reports...")
        
        reports = {
            'vehicle_count': self.generate_vehicle_count_report(date),
            'parking_usage': self.generate_parking_usage_report(date),
            'daily_revenue': self.generate_daily_revenue_report(date),
            'overall_statistics': self.generate_overall_statistics_report()
        }
        
        print(f"\n✓ All reports generated in: {self.reports_dir}")
        
        return reports


# Test function
if __name__ == "__main__":
    print("Testing Report Generator...")
    
    # Import database
    from database.csv_database import CSVDatabase
    
    # Initialize
    db = CSVDatabase('database')
    generator = ReportGenerator(db)
    
    # Generate all reports
    reports = generator.generate_all_reports()
    
    print(f"\nGenerated reports:")
    for report_type, path in reports.items():
        print(f"  - {report_type}: {os.path.basename(path)}")
    
    print("\n✓ Report generator test completed!")
