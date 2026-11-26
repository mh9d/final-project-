"""Energy analysis: carbon footprint, usage rating and saving tips."""

# Approximate grid emission factor for Peninsular Malaysia (kg CO2 per kWh).
# Assumption for teaching purposes; replace with the latest official figure.
GRID_EMISSION_FACTOR = 0.585

# kg of CO2 one mature tree absorbs per year (commonly quoted estimate).
CO2_ABSORBED_PER_TREE_YEAR = 21.0

# Keyword -> saving tip. Used to match appliance names (pattern recognition).
SAVING_TIPS = {
    "air": "Set the air conditioner to 24-25 C and clean its filter monthly.",
    "fridge": "Keep the fridge door closed and leave space behind it for airflow.",
    "refrigerator": "Keep the fridge door closed and leave space behind it for airflow.",
    "heater": "Use the water heater only shortly before bathing or add a timer.",
    "light": "Switch to LED bulbs; they use about 80% less energy than incandescent.",
    "lamp": "Switch to LED bulbs; they use about 80% less energy than incandescent.",
    "tv": "Turn the TV off at the plug instead of leaving it on standby.",
    "television": "Turn the TV off at the plug instead of leaving it on standby.",
    "computer": "Enable sleep mode and shut the computer down at night.",
    "washing": "Wash full loads with cold water when possible.",
    "iron": "Iron clothes in batches to avoid reheating the iron many times.",
    "fan": "Fans are efficient; use them instead of air conditioning when you can.",
}


class EnergyAnalyzer:
    """Analyses a household's consumption and suggests improvements."""

    def __init__(self, emission_factor=GRID_EMISSION_FACTOR):
        self.emission_factor = emission_factor

    def carbon_kg(self, monthly_kwh):
        """Return monthly CO2 emissions in kg."""
        return monthly_kwh * self.emission_factor

    def trees_to_offset(self, monthly_kwh):
        """Return how many trees are needed to absorb one year of emissions."""
        yearly_co2 = self.carbon_kg(monthly_kwh) * 12
        return yearly_co2 / CO2_ABSORBED_PER_TREE_YEAR

    def usage_rating(self, monthly_kwh):
        """Classify monthly usage into a simple rating using if/elif/else."""
        if monthly_kwh <= 200:
            return "LOW - Excellent, very efficient household."
        elif monthly_kwh <= 400:
            return "MODERATE - Good, but there is room to save."
        elif monthly_kwh <= 600:
            return "HIGH - Consider reducing heavy appliance use."
        else:
            return "VERY HIGH - Urgent: review your largest appliances."

    def tip_for(self, appliance_name):
        """Return a saving tip that matches the appliance name, or a general tip."""
        lowered = appliance_name.lower()
        for keyword, tip in SAVING_TIPS.items():
            if keyword in lowered:
                return tip
        return "Unplug this appliance when not in use to avoid standby power."

    def what_if_reduce(self, appliance, hours_saved_per_day):
        """Return kWh saved per month if daily usage drops by the given hours."""
        hours_saved = min(hours_saved_per_day, appliance.hours_per_day)
        return (appliance.power_watts * appliance.quantity * hours_saved
                * appliance.days_per_month) / 1000
