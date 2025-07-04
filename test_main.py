import unittest
import json
import os
from main import CreditCard, Wallet

class TestCreditCardOptimizer(unittest.TestCase):
    """
    Unit tests for the credit card optimization logic.
    """

    def setUp(self):
        """
        Set up a temporary data file for testing.
        This method runs before each test function.
        """
        self.test_data = [
            {
                "card_name": "Test Card A",
                "point_value": 1.5,
                "multipliers": {
                    "dining": 5,
                    "travel": 3,
                    "pharmacies": 1.25
                },
                "default_multiplier": 1
            },
            {
                "card_name": "Test Card B",
                "point_value": 1.0,
                "multipliers": {
                    "groceries": 4,
                    "dining": 4
                },
                "default_multiplier": 2
            }
        ]
        self.test_file = 'data/test_cards.json'
        with open(self.test_file, 'w') as f:
            json.dump(self.test_data, f)

        # Initialize the optimizer with the test file
        self.optimizer = Wallet(self.test_file)

    def tearDown(self):
        """
        Clean up the temporary data file after testing.
        This method runs after each test function.
        """
        os.remove(self.test_file)

    def test_credit_card_value_calculation(self):
        """
        Test the calculate_value method of the CreditCard class.
        """
        card_a_data = self.test_data[0]
        card_a = CreditCard(card_a_data)

        # Test a specific category multiplier (5 * 1.5c) / 100 = $0.075
        self.assertAlmostEqual(card_a.calculate_value("dining"), 0.075)
        # Test the default multiplier (1 * 1.5c) / 100 = $0.015
        self.assertAlmostEqual(card_a.calculate_value("shopping"), 0.015)

    def test_get_all_categories(self):
        """
        Test that all unique categories are correctly identified.
        """
        expected_categories = {"dining", "travel", "groceries", "pharmacies"}
        self.assertEqual(self.optimizer.get_all_categories(), expected_categories)

    def test_get_best_card_for_category(self):
        """
        Test finding the best card for a single category.
        """
        # Test dining: Card A (7.5%) vs Card B (4.0%)
        best_card_dining, value_dining = self.optimizer.get_best_card_for_category("dining")
        self.assertEqual(best_card_dining.name, "Test Card A")
        self.assertAlmostEqual(value_dining, 0.075)

        # Test groceries: Card B (4.0%)
        best_card_groceries, value_groceries = self.optimizer.get_best_card_for_category("groceries")
        self.assertEqual(best_card_groceries.name, "Test Card B")
        self.assertAlmostEqual(value_groceries, 0.04)

        # Test travel: Card A (4.5%)
        best_card_travel, value_travel = self.optimizer.get_best_card_for_category("travel")
        self.assertEqual(best_card_travel.name, "Test Card A")
        self.assertAlmostEqual(value_travel, 0.045)

        # Test default category: Card A (1.5%) vs Card B (2.0%)
        best_card_default, value_default = self.optimizer.get_best_card_for_category("default")
        self.assertEqual(best_card_default.name, "Test Card B")
        self.assertAlmostEqual(value_default, 0.02)

        # Test one card's default vs another bonus: Card A (1.875%) vs Card B (2.0%)
        best_card_pharmacy, value_pharmacy = self.optimizer.get_best_card_for_category("pharmacies")
        self.assertEqual(best_card_pharmacy.name, "Test Card B")
        self.assertAlmostEqual(value_pharmacy, 0.02)

    def test_get_best_cards_for_all_categories(self):
        """
        Test the generation of the full best-card-per-category report.
        """
        best_cards = self.optimizer.get_best_cards_for_all_categories()

        # Expected results based on the test data
        expected = {
            'default': {'best_card': 'Test Card B', 'value': 0.02},
            'dining': {'best_card': 'Test Card A', 'value': 0.075},
            'groceries': {'best_card': 'Test Card B', 'value': 0.04},
            'travel': {'best_card': 'Test Card A', 'value': 0.045},
            'pharmacies': {'best_card': 'Test Card B', 'value': 0.02}
        }

        self.assertEqual(len(best_cards), len(expected))
        for category, result in expected.items():
            self.assertIn(category, best_cards)
            self.assertEqual(best_cards[category]['best_card'], result['best_card'])
            self.assertAlmostEqual(best_cards[category]['value'], result['value'])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
