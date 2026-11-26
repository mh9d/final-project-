"""Tiered (block) electricity tariff calculator."""

# Tariff blocks: (block size in kWh, rate in RM per kWh).
# None as the size means "all remaining kWh".
# NOTE: These rates follow the older Malaysian domestic block tariff and are
# for teaching purposes only. Update them to the current official rates.
DEFAULT_TARIFF_BLOCKS = [
    (200, 0.218),   # first 200 kWh
    (100, 0.334),   # next 100 kWh (201 - 300)
    (300, 0.516),   # next 300 kWh (301 - 600)
    (300, 0.546),   # next 300 kWh (601 - 900)
    (None, 0.571),  # above 900 kWh
]


class TariffCalculator:
    """Calculates the electricity bill using block (tiered) pricing.

    Pattern recognition: every block is handled with the same steps
    (take the kWh that fall into the block, multiply by its rate), so a
    single loop works for any number of blocks.
    """

    def __init__(self, blocks=None, service_tax_rate=0.0, tax_free_kwh=600):
        self.blocks = blocks if blocks is not None else DEFAULT_TARIFF_BLOCKS
        self.service_tax_rate = service_tax_rate  # e.g. 0.08 for 8 %
        self.tax_free_kwh = tax_free_kwh          # tax applies only above this usage

    def breakdown(self, total_kwh):
        """Split total kWh into tariff blocks.

        Returns a list of tuples: (label, kwh_in_block, rate, cost).
        """
        rows = []
        remaining = total_kwh
        lower = 0
        for size, rate in self.blocks:
            if remaining <= 0:
                break
            # The last block has no size limit, so it takes everything left.
            used = remaining if size is None else min(remaining, size)
            upper = "above" if size is None else lower + size
            label = f"{lower + 1}-{upper} kWh" if size is not None else f"> {lower} kWh"
            rows.append((label, used, rate, used * rate))
            remaining -= used
            if size is not None:
                lower += size
        return rows

    def energy_charge(self, total_kwh):
        """Return the cost of energy before tax (RM)."""
        return sum(cost for _, _, _, cost in self.breakdown(total_kwh))

    def service_tax(self, total_kwh):
        """Return service tax, charged only when usage exceeds the tax-free limit."""
        if total_kwh > self.tax_free_kwh and self.service_tax_rate > 0:
            return self.energy_charge(total_kwh) * self.service_tax_rate
        return 0.0

    def total_bill(self, total_kwh):
        """Return the final bill amount (RM), rounded to 2 decimal places."""
        return round(self.energy_charge(total_kwh) + self.service_tax(total_kwh), 2)
