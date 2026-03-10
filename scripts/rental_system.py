"""
Vehicle Rental Management System Module
Handles rental calculations, pricing, and discounts
"""

from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import config
import utils


class RentalCalculator:
    """Calculates rental fees for parked vehicles"""
    
    def __init__(self):
        """Initialize rental calculator with pricing"""
        self.pricing = config.RENTAL_PRICES
        self.discount_rate = config.DAILY_CUSTOMER_DISCOUNT
    
    def get_base_price(self, vehicle_type):
        """
        Get base price for vehicle type
        
        Args:
            vehicle_type: Type of vehicle
        
        Returns:
            Base price in PKR
        """
        return self.pricing.get(vehicle_type.lower(), 100)
    
    def calculate_rent(self, vehicle_type, duration_minutes, is_daily_customer=False):
        """
        Calculate total rent for a vehicle
        
        Args:
            vehicle_type: Type of vehicle
            duration_minutes: Parking duration in minutes
            is_daily_customer: Whether customer gets daily discount
        
        Returns:
            Dictionary with rent details
        """
        # Get base price
        base_price = self.get_base_price(vehicle_type)
        
        # Calculate rent (base price per hour)
        hours = duration_minutes / 60.0
        
        # If less than 1 hour, charge minimum 1 hour
        if hours < 1:
            hours = 1
        
        base_rent = base_price * hours
        
        # Apply discount if applicable
        discount_amount = 0
        if is_daily_customer:
            discount_amount = base_rent * self.discount_rate
        
        # Calculate total
        total_rent = base_rent - discount_amount
        
        return {
            'vehicle_type': vehicle_type,
            'duration_minutes': duration_minutes,
            'duration_hours': hours,
            'base_price': base_price,
            'base_rent': base_rent,
            'discount_rate': self.discount_rate if is_daily_customer else 0,
            'discount_amount': discount_amount,
            'total_rent': total_rent,
            'is_daily_customer': is_daily_customer
        }
    
    def calculate_from_timestamps(self, vehicle_type, entry_time, exit_time=None, 
                                  is_daily_customer=False):
        """
        Calculate rent from entry and exit timestamps
        
        Args:
            vehicle_type: Type of vehicle
            entry_time: Entry timestamp (string or datetime)
            exit_time: Exit timestamp (string or datetime), defaults to now
            is_daily_customer: Whether customer gets daily discount
        
        Returns:
            Dictionary with rent details
        """
        duration = utils.calculate_time_difference(entry_time, exit_time)
        return self.calculate_rent(vehicle_type, duration, is_daily_customer)
    
    def format_rent_receipt(self, rent_details):
        """
        Format rent details as a receipt
        
        Args:
            rent_details: Dictionary from calculate_rent
        
        Returns:
            Formatted receipt string
        """
        receipt = []
        receipt.append("=" * 40)
        receipt.append("      PARKING RENTAL RECEIPT")
        receipt.append("=" * 40)
        receipt.append(f"Vehicle Type: {rent_details['vehicle_type'].capitalize()}")
        receipt.append(f"Duration: {rent_details['duration_hours']:.2f} hours")
        receipt.append(f"Base Price: {rent_details['base_price']} PKR/hour")
        receipt.append("-" * 40)
        receipt.append(f"Base Rent: {rent_details['base_rent']:.2f} PKR")
        
        if rent_details['discount_amount'] > 0:
            receipt.append(f"Discount ({rent_details['discount_rate']*100:.0f}%): -{rent_details['discount_amount']:.2f} PKR")
        
        receipt.append("-" * 40)
        receipt.append(f"TOTAL RENT: {rent_details['total_rent']:.2f} PKR")
        receipt.append("=" * 40)
        
        return "\n".join(receipt)


class RentalManager:
    """Manages vehicle rental operations"""
    
    def __init__(self, database_manager):
        """
        Initialize rental manager
        
        Args:
            database_manager: Database manager instance
        """
        self.db = database_manager
        self.calculator = RentalCalculator()
        self.active_rentals = {}  # track_id -> rental_info
    
    def start_rental(self, track_id, vehicle_type, slot_id=None, is_daily_customer=False):
        """
        Start a new rental when vehicle enters parking
        
        Args:
            track_id: Vehicle tracking ID
            vehicle_type: Type of vehicle
            slot_id: Assigned parking slot
            is_daily_customer: Whether customer gets discount
        
        Returns:
            Rental ID or None
        """
        # Check if already has active rental
        if track_id in self.active_rentals:
            utils.log_event("WARNING", f"Vehicle {track_id} already has active rental")
            return self.active_rentals[track_id]['rental_id']
        
        # Create rental entry in database
        rental_id = self.db.create_rental_entry(track_id, vehicle_type, is_daily_customer)
        
        if rental_id:
            self.active_rentals[track_id] = {
                'rental_id': rental_id,
                'vehicle_type': vehicle_type,
                'entry_time': datetime.now(),
                'slot_id': slot_id,
                'is_daily_customer': is_daily_customer
            }
            
            utils.log_event("INFO", f"Started rental {rental_id} for vehicle {track_id}")
        
        return rental_id
    
    def complete_rental(self, track_id):
        """
        Complete a rental when vehicle exits parking
        
        Args:
            track_id: Vehicle tracking ID
        
        Returns:
            Rent details dictionary or None
        """
        if track_id not in self.active_rentals:
            utils.log_event("WARNING", f"No active rental found for vehicle {track_id}")
            return None
        
        rental_info = self.active_rentals[track_id]
        rental_id = rental_info['rental_id']
        vehicle_type = rental_info['vehicle_type']
        entry_time = rental_info['entry_time']
        is_daily_customer = rental_info['is_daily_customer']
        
        # Calculate rent
        rent_details = self.calculator.calculate_from_timestamps(
            vehicle_type,
            entry_time,
            is_daily_customer=is_daily_customer
        )
        
        # Update database
        success = self.db.complete_rental(
            rental_id,
            rent_details['total_rent'],
            rent_details['duration_minutes'],
            rent_details['base_rent'],
            rent_details['discount_amount']
        )
        
        if success:
            # Remove from active rentals
            del self.active_rentals[track_id]
            
            utils.log_event("INFO", f"Completed rental {rental_id} - Total: {rent_details['total_rent']:.2f} PKR")
            
            return rent_details
        
        return None
    
    def get_active_rental(self, track_id):
        """
        Get active rental information for a vehicle
        
        Args:
            track_id: Vehicle tracking ID
        
        Returns:
            Rental information or None
        """
        return self.active_rentals.get(track_id, None)
    
    def get_current_rent(self, track_id):
        """
        Get current rent for an active rental
        
        Args:
            track_id: Vehicle tracking ID
        
        Returns:
            Current rent details or None
        """
        if track_id not in self.active_rentals:
            return None
        
        rental_info = self.active_rentals[track_id]
        
        # Calculate current rent
        rent_details = self.calculator.calculate_from_timestamps(
            rental_info['vehicle_type'],
            rental_info['entry_time'],
            is_daily_customer=rental_info['is_daily_customer']
        )
        
        return rent_details
    
    def get_active_rentals_count(self):
        """Get number of active rentals"""
        return len(self.active_rentals)
    
    def get_all_active_rentals(self):
        """Get all active rentals"""
        return self.active_rentals.copy()
    
    def cancel_rental(self, track_id):
        """
        Cancel a rental (no charge)
        
        Args:
            track_id: Vehicle tracking ID
        
        Returns:
            Boolean indicating success
        """
        if track_id in self.active_rentals:
            rental_id = self.active_rentals[track_id]['rental_id']
            del self.active_rentals[track_id]
            
            utils.log_event("INFO", f"Cancelled rental {rental_id}")
            return True
        
        return False


class RevenueTracker:
    """Tracks revenue and financial statistics"""
    
    def __init__(self, database_manager):
        """
        Initialize revenue tracker
        
        Args:
            database_manager: Database manager instance
        """
        self.db = database_manager
    
    def get_today_revenue(self):
        """Get total revenue for today"""
        return self.db.get_total_revenue_today()
    
    def get_revenue_summary(self):
        """
        Get revenue summary
        
        Returns:
            Dictionary with revenue statistics
        """
        today_revenue = self.get_today_revenue()
        
        return {
            'today': today_revenue,
            'currency': 'PKR'
        }
    
    def format_revenue_report(self):
        """
        Format revenue report
        
        Returns:
            Formatted report string
        """
        summary = self.get_revenue_summary()
        
        report = []
        report.append("=" * 40)
        report.append("       REVENUE REPORT")
        report.append("=" * 40)
        report.append(f"Today's Revenue: {summary['today']:.2f} {summary['currency']}")
        report.append("=" * 40)
        
        return "\n".join(report)


class DiscountManager:
    """Manages customer discounts"""
    
    def __init__(self):
        """Initialize discount manager"""
        self.daily_customers = set()  # Set of track IDs
    
    def add_daily_customer(self, track_id):
        """
        Mark a customer as daily customer
        
        Args:
            track_id: Vehicle tracking ID
        """
        self.daily_customers.add(track_id)
        utils.log_event("INFO", f"Vehicle {track_id} marked as daily customer")
    
    def remove_daily_customer(self, track_id):
        """Remove daily customer status"""
        if track_id in self.daily_customers:
            self.daily_customers.remove(track_id)
    
    def is_daily_customer(self, track_id):
        """Check if vehicle is a daily customer"""
        return track_id in self.daily_customers
    
    def get_daily_customer_count(self):
        """Get number of daily customers"""
        return len(self.daily_customers)
    
    def clear_daily_customers(self):
        """Clear all daily customer statuses"""
        self.daily_customers.clear()
        utils.log_event("INFO", "Daily customer list cleared")


class RentalVisualizer:
    """Visualize rental information"""
    
    def __init__(self, rental_manager):
        """
        Initialize visualizer
        
        Args:
            rental_manager: RentalManager instance
        """
        self.rental_manager = rental_manager
    
    def draw_rental_info(self, frame, position=(10, 30)):
        """
        Draw rental information on frame
        
        Args:
            frame: Input frame
            position: Starting position
        
        Returns:
            Annotated frame
        """
        active_rentals = self.rental_manager.get_active_rentals_count()
        
        info_text = [
            "=== RENTAL INFO ===",
            f"Active Rentals: {active_rentals}"
        ]
        
        return utils.draw_info_panel(frame, info_text, position)
    
    def display_receipt(self, rent_details):
        """
        Display rental receipt
        
        Args:
            rent_details: Rent details dictionary
        """
        calculator = RentalCalculator()
        receipt = calculator.format_rent_receipt(rent_details)
        print(receipt)


# Test function
if __name__ == "__main__":
    print("Testing Rental Management System...")
    
    # Test calculator
    calculator = RentalCalculator()
    
    # Test 1: Regular customer, 2 hours
    print("\nTest 1: Regular customer, car, 2 hours")
    rent1 = calculator.calculate_rent('car', 120, is_daily_customer=False)
    print(calculator.format_rent_receipt(rent1))
    
    # Test 2: Daily customer, 3 hours
    print("\nTest 2: Daily customer, car, 3 hours")
    rent2 = calculator.calculate_rent('car', 180, is_daily_customer=True)
    print(calculator.format_rent_receipt(rent2))
    
    # Test 3: Motorcycle, 1.5 hours
    print("\nTest 3: Regular customer, motorcycle, 1.5 hours")
    rent3 = calculator.calculate_rent('motorcycle', 90, is_daily_customer=False)
    print(calculator.format_rent_receipt(rent3))
    
    # Test 4: Bus, 0.5 hours (minimum 1 hour charge)
    print("\nTest 4: Regular customer, bus, 0.5 hours")
    rent4 = calculator.calculate_rent('bus', 30, is_daily_customer=False)
    print(calculator.format_rent_receipt(rent4))
    
    print("\n✓ Rental system test completed!")
