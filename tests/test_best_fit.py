import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from compare_offers import compare

class BestFitTests(unittest.TestCase):
    def setUp(self):
        self.data = {'as_of':'2026-10-24','category':'grocery','city':'Tempe','state':'AZ',
                     'item':'a dozen eggs','comparison_key':'large-eggs','quantity_needed':12,'offers':[]}

    def offer(self, name, price, rating=None, rating_source=True, **kw):
        o = {'seller':name,'city':'Tempe','state':'AZ','address':'Fictional Address, Tempe, AZ',
             'location_verified':True,'source_url':'https://example.com/offer',
             'checked_at':'2026-10-24','comparison_key':'large-eggs','available':True,
             'price':price,'pack_quantity':12}
        if rating is not None:
            o['quality_rating_5']=str(rating)
            if rating_source:
                o['rating_source_url']='https://example.com/reviews'
                o['rating_checked_at']='2026-10-24'
        o.update(kw)
        return o

    def test_no_exact_match_proposes_search_not_false_offer(self):
        x = compare(self.data)['decision_support']
        self.assertFalse(x['exact_match_found'])
        self.assertIsNone(x['recommended_option'])
        self.assertTrue(x['next_best_search_steps_if_unavailable'])

    def test_best_value_not_automatically_cheapest(self):
        self.data['offers']=[self.offer('Cheapest', '2.00', rating='1.0'),
                             self.offer('Better', '3.00', rating='4.8')]
        x = compare(self.data)['decision_support']
        self.assertEqual(x['lowest_total_cost_option'], 'Cheapest')
        self.assertEqual(x['highest_sourced_rating_option'], 'Better')
        self.assertEqual(x['recommended_option'], 'Better')

    def test_missing_quality_evidence_blocks_best_value_claim(self):
        self.data['offers']=[self.offer('Unrated','2.00'), self.offer('Rated','3.00',rating='5')]
        x=compare(self.data)['decision_support']
        self.assertIsNone(x['recommended_option'])
        self.assertFalse(x['ratings_documented_for_all_eligible_quotes'])
        self.assertEqual(x['lowest_total_cost_option'],'Unrated')

    def test_rating_without_evidence_is_not_quality(self):
        self.data['offers']=[self.offer('Unverified','2.00',rating='5',rating_source=False)]
        x=compare(self.data)['decision_support']
        self.assertIsNone(x['highest_sourced_rating_option'])

    def test_budget_limit_not_relaxed_implicitly(self):
        self.data['decision']={'max_total_cost':'2.50', 'priority':'highest_quality'}
        self.data['offers']=[self.offer('Over cap','3.00',rating='5.0'),
                             self.offer('Within cap','2.00',rating='4.0')]
        x=compare(self.data)['decision_support']
        self.assertEqual(x['recommended_option'],'Within cap')
        self.assertEqual(x['within_budget_verified_offer_count'],1)

    def test_all_over_budget_no_recommendation(self):
        self.data['decision']={'max_total_cost':'1.00'}
        self.data['offers']=[self.offer('Expensive','2.00',rating='5')]
        x=compare(self.data)['decision_support']
        self.assertIsNone(x['recommended_option'])
        self.assertTrue(x['next_best_search_steps_if_unavailable'])

    def test_invalid_priority_rejected(self):
        self.data['decision']={'priority':'fake'}
        with self.assertRaises(ValueError): compare(self.data)

    def test_outside_city_not_substituted(self):
        self.data['offers']=[self.offer('Outside','1.00',city='Phoenix')]
        x=compare(self.data)
        self.assertFalse(x['decision_support']['exact_match_found'])
        self.assertIsNone(x['decision_support']['recommended_option'])

    def test_expired_rating_ignored(self):
        self.data['offers']=[self.offer('Old reviews','2.00',rating='5', rating_checked_at='2026-01-01')]
        x=compare(self.data)
        self.assertIsNone(x['decision_support']['recommended_option'])

    def test_rental_hold_budget(self):
        sample={'as_of':'2026-10-24','category':'car_rental','city':'Tempe','state':'AZ',
                'item':'car','comparison_key':'economy-car','quantity_needed':1,
                'rental_days':1,'coverage_key':'base','decision':{'priority':'lowest_cost','max_upfront_cash':'90'},
                'offers':[{'seller':'Hold too high','city':'Tempe','state':'AZ',
                           'address':'100 Fictional Ave, Tempe, AZ','location_verified':True,
                           'source_url':'https://example.com/car','checked_at':'2026-10-24',
                           'comparison_key':'economy-car','available':True,'rental_days':1,
                           'return_location_verified':True,'return_city':'Tempe','return_state':'AZ',
                           'return_address':'100 Fictional Ave, Tempe, AZ','coverage_key':'base',
                           'driver_eligible':True,'daily_rate':'20','young_driver_fee_per_day':'0',
                           'tax_estimate':'0','mandatory_fees':'0','insurance_or_coverage_total':'0',
                           'fuel_estimate':'0','mileage_fee_estimate':'0','pickup_travel_cost':'0',
                           'return_travel_cost':'0','refundable_deposit_hold':'100','mileage_policy':'unlimited'}]}
        d=compare(sample)['decision_support']
        self.assertFalse(d['exact_match_found'])
        self.assertIsNone(d['recommended_option'])

if __name__=='__main__':unittest.main()
