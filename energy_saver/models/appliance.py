"""Appliance model: one electrical device used in a household."""


class Appliance:
    """Represents a single household appliance and its usage pattern.

    Abstraction: we ignore brand, colour, etc. and keep only the data
    needed to calculate energy use (power, quantity, hours, days).
    """

    def __init__(self, name, power_watts, quantity, hours_per_day, days_per_month=30):
        self.name = name                      # str, e.g. "Air Conditioner"
        self.power_watts = power_watts        # float, rated power in watts
        self.quantity = quantity              # int, number of identical units
        self.hours_per_day = hours_per_day    # float, average daily usage
        self.days_per_month = days_per_month  # int, days used per month

    def daily_kwh(self):
        """Return energy used per day in kilowatt-hours (kWh).

        Formula: kWh = (watts x quantity x hours) / 1000
        """
        return (self.power_watts * self.quantity * self.hours_per_day) / 1000

    def monthly_kwh(self):
        """Return energy used per month in kWh."""
        return self.daily_kwh() * self.days_per_month

    def to_csv_row(self):
        """Convert the appliance to a list of strings for saving to CSV."""
        return [self.name, str(self.power_watts), str(self.quantity),
                str(self.hours_per_day), str(self.days_per_month)]

    @classmethod
    def from_csv_row(cls, row):
        """Create an Appliance from a CSV row (list of strings)."""
        name, watts, qty, hours, days = row
        return cls(name, float(watts), int(qty), float(hours), int(days))

    def __str__(self):
        return (f"{self.name} ({self.quantity} x {self.power_watts:.0f} W, "
                f"{self.hours_per_day:g} h/day, {self.days_per_month} days)")
