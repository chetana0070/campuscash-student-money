import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from compare_offers import compare

class CompareTests(unittest.TestCase):
    def setUp(self):
        self.base = {'as_of': '2026-10-24', 'category': 'grocery', 'city':'Tempe', 'state':'AZ', 'item': '12 eggs', 'comparison_key': 'eggs', 'quantity_needed': 12, 'offers': []}
    def quote(self, **kwargs):
        x = {'seller': 'Store', 'city':'Tempe', 'state':'AZ', 'address':'100 Fictional Street, Tempe, AZ', 'location_verified':True, 'source_url': 'https://example.com/a', 'checked_at': '2026-10-24', 'comparison_key': 'eggs', 'available': True, 'price': '3.00', 'pack_quantity': 12}
        x.update(kwargs)
        return x
    def test_no_offers(self):
        self.assertIsNone(compare(self.base)['lowest_comparable_quote'])
    def test_cheapest_with_transport(self):
        self.base['offers'] = [self.quote(seller='Cheap sticker', price='2.50', travel_cost='3'), self.quote(seller='Lowest total', price='3.00', travel_cost='0')]
        self.assertEqual(compare(self.base)['lowest_comparable_quote'], 'Lowest total')
    def test_pack_sizes(self):
        self.base['offers'] = [self.quote(pack_quantity=6, price='2.00')]
        self.assertEqual(compare(self.base)['ranked_offers'][0]['estimated_checkout_total'], '4.00')
        self.assertEqual(compare(self.base)['ranked_offers'][0]['packs_to_buy'], 2)
    def test_old_quote_excluded(self):
        self.base['offers'] = [self.quote(checked_at='2026-10-10')]
        self.assertFalse(compare(self.base)['ranked_offers'])
    def test_unavailable_excluded(self):
        self.base['offers'] = [self.quote(available=False)]
        self.assertFalse(compare(self.base)['ranked_offers'])
    def test_different_model_excluded(self):
        self.base['offers'] = [self.quote(comparison_key='another')]
        self.assertFalse(compare(self.base)['ranked_offers'])
    def test_reject_nan(self):
        self.base['offers'] = [self.quote(price='NaN')]
        self.assertFalse(compare(self.base)['ranked_offers'])
    def test_electronics_comparable_model(self):
        self.base.update(category='electronics', comparison_key='ipad-air-wifi-128-new', quantity_needed=1)
        self.base['offers'] = [self.quote(comparison_key='ipad-air-wifi-128-new', price='499', pack_quantity=1, tax_estimate='39', delivery_fee='0')]
        self.assertEqual(compare(self.base)['ranked_offers'][0]['estimated_checkout_total'], '538.00')
    def test_housing_all_in_rent_and_deposit(self):
        self.base.update(category='housing', comparison_key='private-room-12month', quantity_needed=1)
        self.base['offers'] = [self.quote(comparison_key='private-room-12month', rent_monthly='750', utilities_monthly='75', fees_monthly='25', commute_monthly='30', deposit='500', move_in_fees='80')]
        r = compare(self.base)['ranked_offers'][0]
        self.assertEqual(r['monthly_total'], '880.00')
        self.assertEqual(r['approx_move_in_cash'], '1460.00')
    def test_housing_requires_utilities(self):
        self.base.update(category='housing', comparison_key='private-room-12month')
        self.base['offers'] = [self.quote(comparison_key='private-room-12month', rent_monthly='800')]
        self.assertFalse(compare(self.base)['ranked_offers'])

if __name__ == '__main__': unittest.main()
