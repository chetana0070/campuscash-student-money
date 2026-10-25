import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from compare_offers import compare, SUPPORTED_CITIES


class MetroCoverageTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'assets' / 'metro-demo.json').read_text(encoding='utf8'))

    def test_six_cities_and_ranking(self):
        r = compare(self.data)
        self.assertEqual(len(r['cities']), 6)
        self.assertEqual(set(r['ranked_by_city']), set(SUPPORTED_CITIES))
        self.assertEqual(len(r['ranked_offers']), 6)
        self.assertEqual(r['lowest_comparable_quote'], 'FICTIONAL Tempe store')

    def test_city_labels_retained(self):
        r = compare(self.data)
        self.assertEqual(r['ranked_by_city']['Chandler'][0]['city'], 'Chandler')
        self.assertEqual(r['ranked_by_city']['Gilbert'][0]['city'], 'Gilbert')

    def test_each_city_supported_individually(self):
        for city in SUPPORTED_CITIES:
            with self.subTest(city=city):
                data = copy.deepcopy(self.data)
                data.pop('cities')
                data['city'] = city
                self.assertEqual(len(compare(data)['ranked_offers']), 1)

    def test_outside_municipality_excluded(self):
        self.data['offers'].append(dict(self.data['offers'][0], seller='Fictional Tucson', city='Tucson'))
        r = compare(self.data)
        self.assertEqual(len(r['ranked_offers']), 6)
        self.assertTrue(any('outside' in x['reason'] for x in r['excluded_offers']))

    def test_unverified_city_rejected(self):
        self.data['offers'][0]['location_verified'] = False
        self.assertEqual(len(compare(self.data)['ranked_offers']), 5)

    def test_multicity_requires_travel_cost(self):
        self.data['offers'] = [self.data['offers'][0]]
        del self.data['offers'][0]['travel_cost']
        r = compare(self.data)
        self.assertEqual(r['ranked_offers'], [])
        self.assertIn('travel_cost', r['excluded_offers'][0]['reason'])

    def test_multicity_requires_tax_estimate(self):
        self.data['offers'] = [self.data['offers'][0]]
        del self.data['offers'][0]['tax_estimate']
        self.assertFalse(compare(self.data)['ranked_offers'])

    def test_top_level_city_and_cities_conflict(self):
        self.data['city'] = 'Tempe'
        with self.assertRaisesRegex(ValueError, 'either city or cities'):
            compare(self.data)

    def test_duplicate_cities_rejected(self):
        self.data['cities'] = ['Tempe', 'tempe']
        with self.assertRaisesRegex(ValueError, 'distinct cities'):
            compare(self.data)

    def test_unsupported_selected_city_rejected(self):
        self.data['cities'] = ['Tempe', 'Glendale']
        with self.assertRaisesRegex(ValueError, 'distinct cities'):
            compare(self.data)

    def test_wrong_state_rejected(self):
        self.data['state'] = 'CA'
        with self.assertRaisesRegex(ValueError, 'Arizona'):
            compare(self.data)

    def test_only_requested_city_ranked(self):
        self.data['cities'] = ['Mesa', 'Gilbert']
        r = compare(self.data)
        self.assertEqual(len(r['ranked_offers']), 2)
        self.assertEqual(set(r['ranked_by_city']), {'Mesa', 'Gilbert'})

    def test_restaurants_by_city_and_cuisine(self):
        data = json.loads((ROOT / 'assets' / 'metro-restaurant-demo.json').read_text(encoding='utf8'))
        r = compare(data)
        self.assertEqual(len(r['ranked_offers']), 6)
        self.assertEqual(set(r['ranked_by_cuisine']), {'Indian', 'Mexican'})
        self.assertEqual(set(r['ranked_by_city']), set(SUPPORTED_CITIES))
        self.assertIsNone(r['lowest_comparable_quote'])

    def test_cross_city_rental_return_allowed_if_selected(self):
        data = json.loads((ROOT / 'assets' / 'car-rental-demo.json').read_text(encoding='utf8'))
        data.pop('city')
        data['cities'] = ['Tempe', 'Mesa']
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['return_city'] = 'Mesa'
        data['offers'][0]['return_address'] = 'FICTIONAL return office, Mesa AZ'
        r = compare(data)
        self.assertEqual(len(r['ranked_offers']), 1)
        self.assertEqual(r['ranked_offers'][0]['return_city'], 'Mesa')

    def test_cross_city_rental_return_unselected_rejected(self):
        data = json.loads((ROOT / 'assets' / 'car-rental-demo.json').read_text(encoding='utf8'))
        data.pop('city')
        data['cities'] = ['Tempe', 'Chandler']
        data['offers'] = [data['offers'][0]]
        data['offers'][0]['return_city'] = 'Mesa'
        self.assertFalse(compare(data)['ranked_offers'])

    def test_housing_commute_cost_keeps_rank_honest(self):
        data = {'as_of': '2026-10-24', 'category': 'housing', 'cities':['Tempe','Mesa'],
                'state':'AZ','comparison_key':'private-room-12months', 'offers': []}
        for city, rent, commute in [('Tempe','850','10'),('Mesa','750','150')]:
            data['offers'].append({'seller': 'FICTIONAL housing in '+city,'city': city,'state':'AZ',
                 'address':'Fictional '+city+' AZ','location_verified':True, 'source_url':'https://example.com/fictional',
                 'checked_at':'2026-10-24','comparison_key':'private-room-12months','available':True,
                 'rent_monthly':rent,'utilities_monthly':'60','fees_monthly':'10','commute_monthly':commute,
                 'deposit':'300','move_in_fees':'50'})
        r = compare(data)
        self.assertEqual(r['ranked_offers'][0]['city'], 'Tempe')
        self.assertEqual(r['ranked_offers'][0]['monthly_total'], '930.00')


if __name__ == '__main__':
    unittest.main()
