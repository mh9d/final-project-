"""Functions that format and print information to the console."""

LINE_WIDTH = 64


def print_header(title):
    """Print a boxed section title."""
    print("\n" + "=" * LINE_WIDTH)
    print(title.center(LINE_WIDTH))
    print("=" * LINE_WIDTH)


def display_main_menu():
    """Show the main menu options."""
    print_header("SDG 7 HOUSEHOLD ELECTRICITY BILL ESTIMATOR")
    print("  1. Add an appliance")
    print("  2. View appliance list")
    print("  3. Remove an appliance")
    print("  4. Calculate monthly usage and bill")
    print("  5. Energy-saving analysis")
    print("  6. 'What-if' saving simulator")
    print("  7. Load sample household (demo data)")
    print("  8. Save / load appliances (CSV file)")
    print("  0. Exit")
    print("-" * LINE_WIDTH)


def display_appliance_table(household):
    """Print every appliance in a formatted table with its monthly kWh."""
    print(f"\n{'No':<4}{'Appliance':<20}{'Watts':>7}{'Qty':>5}{'Hrs/day':>9}"
          f"{'Days':>6}{'kWh/mo':>10}")
    print("-" * LINE_WIDTH)
    for number, appliance in enumerate(household.appliances, start=1):
        print(f"{number:<4}{appliance.name[:19]:<20}{appliance.power_watts:>7.0f}"
              f"{appliance.quantity:>5}{appliance.hours_per_day:>9.1f}"
              f"{appliance.days_per_month:>6}{appliance.monthly_kwh():>10.1f}")
    print("-" * LINE_WIDTH)
    print(f"{'TOTAL':<51}{household.total_monthly_kwh():>10.1f} kWh")


def display_bill(total_kwh, calculator):
    """Print the tariff block breakdown and the final bill."""
    print(f"\n{'Tariff block':<20}{'kWh':>10}{'Rate (RM)':>12}{'Cost (RM)':>12}")
    print("-" * 54)
    for label, kwh, rate, cost in calculator.breakdown(total_kwh):
        print(f"{label:<20}{kwh:>10.1f}{rate:>12.3f}{cost:>12.2f}")
    print("-" * 54)
    print(f"{'Energy charge':<42}{calculator.energy_charge(total_kwh):>12.2f}")
    tax = calculator.service_tax(total_kwh)
    if tax > 0:
        print(f"{'Service tax':<42}{tax:>12.2f}")
    else:
        print(f"{'Service tax (usage below limit)':<42}{0:>12.2f}")
    print(f"{'ESTIMATED MONTHLY BILL (RM)':<42}{calculator.total_bill(total_kwh):>12.2f}")


def pause():
    """Wait for the user before returning to the menu."""
    input("\nPress Enter to return to the menu...")
