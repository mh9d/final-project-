"""Household model: a collection of appliances belonging to one home."""

import csv

from energy_saver.models.appliance import Appliance


class Household:
    """Stores and manages the list of appliances for one household."""

    def __init__(self, owner_name="My Home"):
        self.owner_name = owner_name
        self.appliances = []  # list of Appliance objects

    def add_appliance(self, appliance):
        """Add an Appliance object to the household."""
        self.appliances.append(appliance)

    def remove_appliance(self, index):
        """Remove and return the appliance at the given list index."""
        return self.appliances.pop(index)

    def is_empty(self):
        """Return True when no appliances have been recorded."""
        return len(self.appliances) == 0

    def total_monthly_kwh(self):
        """Sum the monthly kWh of every appliance (accumulator pattern)."""
        total = 0.0
        for appliance in self.appliances:
            total += appliance.monthly_kwh()
        return total

    def sorted_by_usage(self):
        """Return appliances ordered from highest to lowest monthly kWh."""
        return sorted(self.appliances, key=lambda a: a.monthly_kwh(), reverse=True)

    def save_to_csv(self, filename):
        """Save all appliances to a CSV file."""
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["name", "power_watts", "quantity", "hours_per_day", "days_per_month"])
            for appliance in self.appliances:
                writer.writerow(appliance.to_csv_row())

    def load_from_csv(self, filename):
        """Replace the appliance list with the contents of a CSV file.

        Returns the number of appliances loaded. Raises OSError or
        ValueError if the file is missing or badly formatted.
        """
        loaded = []
        with open(filename, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # skip the header row
            for row in reader:
                if row:  # ignore blank lines
                    loaded.append(Appliance.from_csv_row(row))
        self.appliances = loaded
        return len(loaded)
