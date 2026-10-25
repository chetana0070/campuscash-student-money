import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from savings_coach import analyze_savings


class SavingsCoachTests(unittest.TestCase):
    def setUp(self):
        self.d = json.loads((ROOT / 'assets' / 'savings-demo.json').read_text(encoding='utf-8'))

    def test_surplus_after_essentials_and_buffer(self):
        r = analyze_savings(self.d)
        self.assertEqual(r['status'], 'ILLUSTRATIVE_EXTRA_CASH')
        self.assertEqual(r['illustrative_cash_available_to_earmark_today'], '250.00')
        self.assertEqual(r['forecast_lowest_balance'], '550.00')

    def test_unconfirmed_income_blocks_excess_money(self):
        self.d['events'][0]['status'] = 'expected'
        r = analyze_savings(self.d)
        self.assertEqual(r['status'], 'INCOME_UNCERTAINTY')
        self.assertEqual(r['illustrative_cash_available_to_earmark_today'], '0.00')
        self.assertEqual(r['without_unconfirmed_income_lowest_balance'], '150.00')

    def test_missing_essentials_review_blocks_excess_claim(self):
        self.d['essentials_reviewed'] = False
        r = analyze_savings(self.d)
        self.assertEqual(r['status'], 'NEEDS_OBLIGATION_REVIEW')
        self.assertIsNone(r['illustrative_cash_available_to_earmark_today'])

    def test_essential_categories_are_not_targets(self):
        r = analyze_savings(self.d)
        self.assertEqual(r['illustrative_monthly_reduction_total'], '29.00')
        self.assertEqual({a['category'] for a in r['hypothetical_optional_spending_reductions']},
                         {'Dining out', 'Clothing extras', 'Optional subscriptions'})

    def test_goal_is_pace_not_guarantee(self):
        r = analyze_savings(self.d)
        self.assertEqual(r['savings_goal']['remaining'], '380.00')
        self.assertTrue(r['savings_goal']['affordability_not_established'])

    def test_negative_forecast_blocks_excess(self):
        self.d['events'].append({'date':'2026-10-25','label':'Urgent fees','amount':'-1600','status':'confirmed'})
        r = analyze_savings(self.d)
        self.assertEqual(r['status'], 'ESSENTIAL_SHORTFALL')
        self.assertEqual(r['illustrative_cash_available_to_earmark_today'], '0.00')

    def test_reduction_outside_range_rejected(self):
        self.d['hypothetical_reduction_percent'] = '105'
        with self.assertRaises(ValueError):
            analyze_savings(self.d)

    def test_negative_monthly_spending_rejected(self):
        self.d['monthly_spending'][0]['amount'] = '-1'
        with self.assertRaises(ValueError):
            analyze_savings(self.d)

    def test_no_auto_invest_and_disclaimer(self):
        r = analyze_savings(self.d)
        self.assertIn('no obligation or compulsion', r['disclaimer'])
        self.assertIn('at your own risk', r['disclaimer'])
        self.assertIn('never moves or invests money', r['disclaimer'])

    def test_invalid_essentials_confirmation(self):
        self.d['essentials_reviewed'] = 'yes'
        with self.assertRaises(ValueError):
            analyze_savings(self.d)

    def test_expired_goal_rejected(self):
        self.d['savings_goal']['target_date'] = '2025-01-01'
        with self.assertRaises(ValueError):
            analyze_savings(self.d)

    def test_decimal_precision(self):
        self.d['monthly_spending'] = [{'category':'Snack', 'amount':'1.05','essential':False}]
        self.d['hypothetical_reduction_percent'] = '10'
        self.assertEqual(analyze_savings(self.d)['illustrative_monthly_reduction_total'], '0.11')


if __name__ == '__main__':
    unittest.main()
