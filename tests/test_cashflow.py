import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from cashflow import forecast
class ForecastTests(unittest.TestCase):
    def setUp(self):self.d={'as_of':'2026-10-24','starting_balance':'100','minimum_buffer':'25','events':[]}
    def test_no_bills(self):self.assertEqual(forecast(self.d)['risk'],'ON_TRACK')
    def test_shortfall(self):
        self.d['events']=[{'date':'2026-10-25','amount':'-150','status':'confirmed'}]
        self.assertEqual(forecast(self.d)['first_negative_date'],'2026-10-25')
    def test_low_buffer(self):
        self.d['events']=[{'date':'2026-10-25','amount':'-80','status':'confirmed'}]
        self.assertEqual(forecast(self.d)['risk'],'LOW_BUFFER')
    def test_expected_paycheck_stress(self):
        self.d['events']=[{'date':'2026-10-25','amount':'200','status':'expected'},{'date':'2026-10-26','amount':'-150','status':'confirmed'}]
        self.assertIsNone(forecast(self.d)['first_negative_date'])
        self.assertEqual(forecast(self.d)['without_unconfirmed_income_scenario']['first_negative_date'],'2026-10-26')
    def test_past_event_ignored(self):
        self.d['events']=[{'date':'2026-10-23','amount':'-1000'}]
        self.assertEqual(forecast(self.d)['projected_end_balance'],'100.00')
    def test_nan_rejected(self):
        self.d['starting_balance']='NaN'
        with self.assertRaises(ValueError):forecast(self.d)
    def test_currency_rejected(self):
        self.d['currency']='EUR'
        with self.assertRaises(ValueError):forecast(self.d)
if __name__=='__main__':unittest.main()
