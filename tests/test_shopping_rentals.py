import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from compare_offers import compare


class TempeRentalShoppingTests(unittest.TestCase):
    @staticmethod
    def sample(name):
        return json.loads((ROOT / 'assets' / name).read_text(encoding='utf-8'))

    def test_car_rental_true_total_and_hold_separate(self):
        data = self.sample('car-rental-demo.json')
        result = compare(data)
        self.assertEqual(result['lowest_comparable_quote'], 'Demo Car Rental B')
        self.assertEqual(result['ranked_offers'][0]['estimated_checkout_total'], '115.00')
        self.assertEqual(result['ranked_offers'][0]['refundable_deposit_hold'], '100.00')
        self.assertEqual(result['ranked_offers'][0]['potential_funds_needed_including_hold'], '215.00')

    def test_age_surcharge_included_for_each_day(self):
        data = self.sample('car-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        self.assertEqual(compare(data)['ranked_offers'][0]['estimated_checkout_total'], '149.00')

    def test_renter_not_eligible_excluded(self):
        data = self.sample('car-rental-demo.json')
        data['offers'][0]['driver_eligible'] = False
        data['offers'][1]['driver_eligible'] = False
        self.assertFalse(compare(data)['ranked_offers'])

    def test_uncertain_driver_eligibility_excluded(self):
        data = self.sample('car-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        del data['offers'][0]['driver_eligible']
        self.assertFalse(compare(data)['ranked_offers'])

    def test_out_of_city_return_excluded(self):
        data = self.sample('car-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['return_city'] = 'Phoenix'
        self.assertFalse(compare(data)['ranked_offers'])

    def test_missing_return_verification_excluded(self):
        data = self.sample('car-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['return_location_verified'] = False
        self.assertFalse(compare(data)['ranked_offers'])

    def test_mismatched_rental_duration_excluded(self):
        data = self.sample('car-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['rental_days'] = 4
        self.assertFalse(compare(data)['ranked_offers'])

    def test_mismatched_coverage_excluded(self):
        data = self.sample('car-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['coverage_key'] = 'comprehensive-cover'
        self.assertFalse(compare(data)['ranked_offers'])

    def test_rental_requires_known_fees(self):
        data = self.sample('car-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        del data['offers'][0]['tax_estimate']
        self.assertFalse(compare(data)['ranked_offers'])

    def test_rental_freshness_two_days(self):
        data = self.sample('car-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['checked_at'] = '2026-10-20'
        self.assertFalse(compare(data)['ranked_offers'])

    def test_rental_duration_max_60(self):
        data = self.sample('car-rental-demo.json')
        data['rental_days'] = 61
        with self.assertRaisesRegex(ValueError, 'rental_days'):
            compare(data)

    def test_dress_rental_cost_and_deposit(self):
        result = compare(self.sample('dress-rental-demo.json'))
        row = result['ranked_offers'][0]
        self.assertEqual(row['seller'], 'Demo Dress Rental B')
        self.assertEqual(row['estimated_checkout_total'], '44.00')
        self.assertEqual(row['refundable_deposit_hold'], '75.00')
        self.assertEqual(row['potential_funds_needed_including_hold'], '119.00')

    def test_dress_fit_unavailable(self):
        data = self.sample('dress-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['fit_available'] = False
        self.assertFalse(compare(data)['ranked_offers'])

    def test_dress_return_outside_tempe(self):
        data = self.sample('dress-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['return_city'] = 'Mesa'
        self.assertFalse(compare(data)['ranked_offers'])

    def test_dress_missing_cleaning_fee_excluded(self):
        data = self.sample('dress-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        del data['offers'][0]['cleaning_fee']
        self.assertFalse(compare(data)['ranked_offers'])

    def test_dress_old_quote_excluded(self):
        data = self.sample('dress-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['checked_at'] = '2026-10-20'
        self.assertFalse(compare(data)['ranked_offers'])

    def test_clothing_true_cost_and_comparison(self):
        result = compare(self.sample('shopping-demo.json'))
        self.assertEqual(result['ranked_offers'][0]['seller'], 'Demo Fashion Shop B')
        self.assertEqual(result['ranked_offers'][0]['estimated_checkout_total'], '37.30')
        self.assertEqual(result['ranked_offers'][1]['estimated_checkout_total'], '39.75')

    def test_clothing_size_unavailable_excluded(self):
        data = self.sample('shopping-demo.json')
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['size_available'] = False
        self.assertFalse(compare(data)['ranked_offers'])

    def test_clothing_return_policy_unknown_excluded(self):
        data = self.sample('shopping-demo.json')
        data['offers'] = [data['offers'][0]]
        del data['offers'][0]['return_policy_checked']
        self.assertFalse(compare(data)['ranked_offers'])

    def test_general_shopping_requires_return_policy(self):
        data = self.sample('shopping-demo.json')
        data['category'] = 'shopping'
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['return_policy_checked'] = False
        self.assertFalse(compare(data)['ranked_offers'])

    def test_general_shopping_does_not_require_size(self):
        data = self.sample('shopping-demo.json')
        data['category'] = 'shopping'
        data['offers'] = [data['offers'][0]]
        del data['offers'][0]['size_available']
        self.assertEqual(len(compare(data)['ranked_offers']), 1)

    def test_invalid_search_city_always_rejected(self):
        data = self.sample('shopping-demo.json')
        data['city'] = 'Tucson'
        with self.assertRaisesRegex(ValueError, 'Tempe'):
            compare(data)

    def test_negative_card_hold_rejected(self):
        data = self.sample('car-rental-demo.json')
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['refundable_deposit_hold'] = '-100'
        self.assertFalse(compare(data)['ranked_offers'])


if __name__ == '__main__':
    unittest.main()
