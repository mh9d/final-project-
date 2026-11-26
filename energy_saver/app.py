"""Main application controller: runs the menu loop and each feature."""

from energy_saver.models import Appliance, Household
from energy_saver.services import EnergyAnalyzer, TariffCalculator
from energy_saver.ui.display import (
    display_appliance_table, display_bill, display_main_menu, pause, print_header,
)
from energy_saver.utils.validation import (
    get_float, get_int, get_text, get_yes_no,
)

# Sample data so users (and testers) can try the app quickly.
SAMPLE_APPLIANCES = [
    ("Air Conditioner", 1000, 1, 8, 30),
    ("Refrigerator", 150, 1, 24, 30),
    ("LED Lights", 10, 8, 6, 30),
    ("Ceiling Fan", 70, 3, 10, 30),
    ("Television", 100, 1, 5, 30),
    ("Water Heater", 3000, 1, 0.5, 30),
    ("Washing Machine", 500, 1, 1, 12),
    ("Rice Cooker", 700, 1, 1, 30),
]

DEFAULT_FILE = "appliances.csv"


class EnergyApp:
    """Connects the user interface with the household data and services."""

    def __init__(self):
        self.household = Household()
        # Service tax of 8% applied above 600 kWh (assumption; check current rules).
        self.calculator = TariffCalculator(service_tax_rate=0.08, tax_free_kwh=600)
        self.analyzer = EnergyAnalyzer()
        self.running = True

    # ------------------------------------------------------------------ #
    # Menu loop
    # ------------------------------------------------------------------ #
    def run(self):
        """Show the menu repeatedly until the user chooses to exit."""
        actions = {
            1: self.add_appliance,
            2: self.view_appliances,
            3: self.remove_appliance,
            4: self.calculate_bill,
            5: self.show_analysis,
            6: self.what_if_simulator,
            7: self.load_sample_data,
            8: self.file_menu,
            0: self.exit_app,
        }
        while self.running:
            display_main_menu()
            choice = get_int("Enter your choice (0-8): ", minimum=0, maximum=8)
            actions[choice]()

    def _require_appliances(self):
        """Return True if appliances exist; otherwise warn the user."""
        if self.household.is_empty():
            print("\n  [!] No appliances recorded yet. Use option 1 or 7 first.")
            pause()
            return False
        return True

    # ------------------------------------------------------------------ #
    # Feature 1: record information
    # ------------------------------------------------------------------ #
    def add_appliance(self):
        """Ask the user for appliance details and store them."""
        print_header("ADD AN APPLIANCE")
        adding = True
        while adding:
            name = get_text("Appliance name: ")
            watts = get_float("Power rating (watts, e.g. 1000): ", minimum=1, maximum=10000)
            quantity = get_int("Quantity: ", minimum=1, maximum=100)
            hours = get_float("Average hours used per day (0-24): ", minimum=0, maximum=24)
            days = get_int("Days used per month (1-31): ", minimum=1, maximum=31)

            appliance = Appliance(name, watts, quantity, hours, days)
            self.household.add_appliance(appliance)
            print(f"\n  [OK] Added: {appliance}")
            print(f"       Uses about {appliance.monthly_kwh():.1f} kWh per month.")
            adding = get_yes_no("\nAdd another appliance? (y/n): ")

    def view_appliances(self):
        """Show the appliance table."""
        if not self._require_appliances():
            return
        print_header("APPLIANCE LIST")
        display_appliance_table(self.household)
        pause()

    def remove_appliance(self):
        """Remove an appliance chosen by its number."""
        if not self._require_appliances():
            return
        print_header("REMOVE AN APPLIANCE")
        display_appliance_table(self.household)
        count = len(self.household.appliances)
        number = get_int(f"Number to remove (1-{count}, 0 to cancel): ", minimum=0, maximum=count)
        if number == 0:
            print("  Cancelled.")
        else:
            removed = self.household.remove_appliance(number - 1)
            print(f"  [OK] Removed {removed.name}.")
        pause()

    # ------------------------------------------------------------------ #
    # Feature 2: calculations
    # ------------------------------------------------------------------ #
    def calculate_bill(self):
        """Calculate total monthly kWh and the estimated bill."""
        if not self._require_appliances():
            return
        print_header("MONTHLY USAGE AND BILL")
        total_kwh = self.household.total_monthly_kwh()
        print(f"Total estimated usage : {total_kwh:.1f} kWh/month")
        print(f"Average per day       : {total_kwh / 30:.2f} kWh/day")
        display_bill(total_kwh, self.calculator)
        yearly = self.calculator.total_bill(total_kwh) * 12
        print(f"\nProjected yearly cost : RM {yearly:,.2f}")
        pause()

    # ------------------------------------------------------------------ #
    # Feature 3: analysis and results
    # ------------------------------------------------------------------ #
    def show_analysis(self):
        """Show usage rating, carbon footprint, top consumers and tips."""
        if not self._require_appliances():
            return
        print_header("ENERGY-SAVING ANALYSIS")
        total_kwh = self.household.total_monthly_kwh()

        print(f"Usage rating     : {self.analyzer.usage_rating(total_kwh)}")
        print(f"CO2 emissions    : {self.analyzer.carbon_kg(total_kwh):.1f} kg/month")
        print(f"Trees to offset  : {self.analyzer.trees_to_offset(total_kwh):.0f} trees "
              f"(one year of emissions)")

        print("\nShare of usage by appliance:")
        for appliance in self.household.sorted_by_usage():
            share = (appliance.monthly_kwh() / total_kwh * 100) if total_kwh > 0 else 0
            bar = "#" * int(share // 2)  # one '#' for every 2 %
            print(f"  {appliance.name[:18]:<18} {share:5.1f}% {bar}")

        print("\nTop 3 appliances and saving tips:")
        for rank, appliance in enumerate(self.household.sorted_by_usage()[:3], start=1):
            print(f"  {rank}. {appliance.name}: {self.analyzer.tip_for(appliance.name)}")
        pause()

    def what_if_simulator(self):
        """Estimate savings if an appliance is used fewer hours per day."""
        if not self._require_appliances():
            return
        print_header("'WHAT-IF' SAVING SIMULATOR")
        display_appliance_table(self.household)
        count = len(self.household.appliances)
        number = get_int(f"Choose an appliance (1-{count}): ", minimum=1, maximum=count)
        appliance = self.household.appliances[number - 1]
        hours = get_float(f"Reduce use by how many hours/day (max {appliance.hours_per_day:g}): ",
                          minimum=0, maximum=appliance.hours_per_day)

        before_kwh = self.household.total_monthly_kwh()
        saved_kwh = self.analyzer.what_if_reduce(appliance, hours)
        after_kwh = before_kwh - saved_kwh
        before_bill = self.calculator.total_bill(before_kwh)
        after_bill = self.calculator.total_bill(after_kwh)

        print(f"\n{'':<18}{'Current':>12}{'After change':>15}")
        print(f"{'Usage (kWh)':<18}{before_kwh:>12.1f}{after_kwh:>15.1f}")
        print(f"{'Bill (RM)':<18}{before_bill:>12.2f}{after_bill:>15.2f}")
        print(f"\nYou would save {saved_kwh:.1f} kWh and RM {before_bill - after_bill:.2f} per month")
        print(f"(RM {(before_bill - after_bill) * 12:.2f} per year) and avoid "
              f"{self.analyzer.carbon_kg(saved_kwh):.1f} kg of CO2 each month.")
        pause()

    # ------------------------------------------------------------------ #
    # Data helpers
    # ------------------------------------------------------------------ #
    def load_sample_data(self):
        """Replace the current list with a typical household for demos."""
        if not self.household.is_empty():
            if not get_yes_no("This replaces your current list. Continue? (y/n): "):
                return
        self.household.appliances = []
        for name, watts, qty, hours, days in SAMPLE_APPLIANCES:
            self.household.add_appliance(Appliance(name, watts, qty, hours, days))
        print(f"\n  [OK] Loaded {len(SAMPLE_APPLIANCES)} sample appliances.")
        pause()

    def file_menu(self):
        """Save the appliance list to CSV or load it back."""
        print_header("SAVE / LOAD")
        print("  1. Save appliances to file")
        print("  2. Load appliances from file")
        print("  0. Back")
        choice = get_int("Choice: ", minimum=0, maximum=2)
        if choice == 0:
            return
        filename = input(f"File name [{DEFAULT_FILE}]: ").strip() or DEFAULT_FILE
        try:
            if choice == 1:
                self.household.save_to_csv(filename)
                print(f"  [OK] Saved {len(self.household.appliances)} appliances to {filename}.")
            else:
                count = self.household.load_from_csv(filename)
                print(f"  [OK] Loaded {count} appliances from {filename}.")
        except FileNotFoundError:
            print(f"  [!] File '{filename}' was not found.")
        except (OSError, ValueError) as error:
            print(f"  [!] Could not use the file: {error}")
        pause()

    def exit_app(self):
        """Confirm and stop the menu loop."""
        if get_yes_no("Are you sure you want to exit? (y/n): "):
            print("\nThank you for saving energy! Every kWh counts for SDG 7. Goodbye.")
            self.running = False
