import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'scripts'))
from compare_offers import compare

class TempeOnlyTests(unittest.TestCase):
    def setUp(self):
        self.base = {'as_of':'2026-10-24','city':'Tempe','state':'AZ','category':'restaurant','item':'lunch',
            'comparison_key':'one-lunch-takeout','service_mode':'takeout','quantity_needed':1,'offers':[]}
    def offer(self, **kwargs):
        r={'seller':'Demo Tempe Restaurant','city':'Tempe','state':'AZ','address':'Fictional Road, Tempe AZ',
           'location_verified':True,'source_url':'https://example.org/fictional','checked_at':'2026-10-24',
           'comparison_key':'one-lunch-takeout','available':True,'cuisine':'Indian','dish':'Lunch entree',
           'service_mode':'takeout','price':'10.00','tax_estimate':'0.80','tip_estimate':'0.00',
           'service_fee':'0.00','delivery_fee':'0.00','travel_cost':'0.00'}
        r.update(kwargs)
        return r
    def test_restaurant_all_in_cost(self):
        self.base['offers']=[self.offer(price='9',tax_estimate='0.80',travel_cost='2.00',tip_estimate='1')]
        self.assertEqual(compare(self.base)['ranked_offers'][0]['estimated_checkout_total'],'12.80')
    def test_grouped_by_cuisine(self):
        self.base['offers']=[self.offer(seller='A'),self.offer(seller='B',cuisine='Mexican',price='8')]
        r=compare(self.base)
        self.assertEqual(set(r['ranked_by_cuisine']),{'Indian','Mexican'})
        self.assertIsNone(r['lowest_comparable_quote'])
    def test_filter_cuisine(self):
        self.base['cuisine']='Indian'
        self.base['offers']=[self.offer(seller='A'),self.offer(seller='B',cuisine='Mexican')]
        r=compare(self.base)
        self.assertEqual(len(r['ranked_offers']),1)
    def test_reject_mesa(self):
        self.base['offers']=[self.offer(city='Mesa')]
        self.assertEqual(len(compare(self.base)['ranked_offers']),0)
    def test_reject_unverified_tempe(self):
        self.base['offers']=[self.offer(location_verified=False)]
        self.assertEqual(len(compare(self.base)['ranked_offers']),0)
    def test_reject_no_address(self):
        self.base['offers']=[self.offer(address='')]
        self.assertEqual(len(compare(self.base)['ranked_offers']),0)
    def test_reject_different_meal(self):
        self.base['offers']=[self.offer(comparison_key='all-you-can-eat-dinner')]
        self.assertEqual(len(compare(self.base)['ranked_offers']),0)
    def test_reject_mismatched_service_mode(self):
        self.base['offers']=[self.offer(service_mode='delivery')]
        self.assertEqual(compare(self.base)['ranked_offers'],[])
    def test_reject_missing_tax(self):
        row=self.offer();del row['tax_estimate'];self.base['offers']=[row]
        self.assertEqual(len(compare(self.base)['ranked_offers']),0)
    def test_reject_stale_menu(self):
        self.base['offers']=[self.offer(checked_at='2026-10-01')]
        self.assertEqual(len(compare(self.base)['ranked_offers']),0)
    def test_all_modes_only_tempe(self):
        self.base.update(category='grocery',quantity_needed=12,comparison_key='eggs')
        self.base['offers']=[dict(self.offer(city='Phoenix',comparison_key='eggs',price='2.00'),pack_quantity=12)]
        self.assertEqual(compare(self.base)['ranked_offers'],[])
    def test_invalid_search_city(self):
        self.base['city']='Tucson'
        with self.assertRaisesRegex(ValueError,'Tempe'):
            compare(self.base)
    def test_no_globally_cheapest_between_cuisines(self):
        self.base['offers']=[self.offer(cuisine='Indian',price='20'),self.offer(cuisine='Thai',price='5')]
        r=compare(self.base)
        self.assertIsNone(r['lowest_comparable_quote'])
    def test_same_cuisine_rank(self):
        self.base['offers']=[self.offer(seller='A',price='20'),self.offer(seller='B',price='10')]
        self.assertEqual(compare(self.base)['lowest_comparable_quote'],'B')

if __name__=='__main__':unittest.main()
