"""Unit tests for the calculation logic.  Run:  python -m unittest"""

import unittest

from energy_saver.models import Appliance, Household
from energy_saver.services import EnergyAnalyzer, TariffCalculator


class TestAppliance(unittest.TestCase):
    def test_monthly_kwh(self):
        # 1000 W x 1 unit x 8 h x 30 days = 240 kWh
        ac = Appliance("Air Conditioner", 1000, 1, 8, 30)
        self.assertAlmostEqual(ac.monthly_kwh(), 240.0)

    def test_quantity_multiplies_usage(self):
        lights = Appliance("LED", 10, 8, 6, 30)  # 10 W x 8 x 6 h x 30 = 14.4 kWh
        self.assertAlmostEqual(lights.monthly_kwh(), 14.4)


class TestHousehold(unittest.TestCase):
    def test_total_and_sorting(self):
        home = Household()
        home.add_appliance(Appliance("Fan", 70, 1, 10, 30))      # 21 kWh
        home.add_appliance(Appliance("AC", 1000, 1, 8, 30))      # 240 kWh
        self.assertAlmostEqual(home.total_monthly_kwh(), 261.0)
        self.assertEqual(home.sorted_by_usage()[0].name, "AC")


class TestTariff(unittest.TestCase):
    def setUp(self):
        self.calc = TariffCalculator(service_tax_rate=0.08, tax_free_kwh=600)

    def test_first_block_only(self):
        self.assertEqual(self.calc.total_bill(100), 21.80)  # 100 x 0.218

    def test_two_blocks(self):
        # 200 x 0.218 + 50 x 0.334 = 43.60 + 16.70 = 60.30
        self.assertEqual(self.calc.total_bill(250), 60.30)

    def test_zero_usage(self):
        self.assertEqual(self.calc.total_bill(0), 0.0)

    def test_tax_above_limit(self):
        energy = self.calc.energy_charge(700)
        self.assertEqual(self.calc.total_bill(700), round(energy * 1.08, 2))


class TestAnalyzer(unittest.TestCase):
    def test_rating_boundaries(self):
        analyzer = EnergyAnalyzer()
        self.assertTrue(analyzer.usage_rating(200).startswith("LOW"))
        self.assertTrue(analyzer.usage_rating(201).startswith("MODERATE"))
        self.assertTrue(analyzer.usage_rating(601).startswith("VERY HIGH"))

    def test_what_if_cannot_exceed_hours(self):
        analyzer = EnergyAnalyzer()
        tv = Appliance("TV", 100, 1, 5, 30)
        # asking to cut 10 h when only 5 h are used saves the full 15 kWh
        self.assertAlmostEqual(analyzer.what_if_reduce(tv, 10), 15.0)

    def test_tip_matching(self):
        self.assertIn("LED", EnergyAnalyzer().tip_for("Bedroom Lights"))


if __name__ == "__main__":
    unittest.main()
