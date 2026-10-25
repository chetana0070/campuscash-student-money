#!/usr/bin/env python3
"""Optional, deterministic budgeting suggestions based on user-entered numbers.

Never requests account credentials, sends money or recommends a specific investment.
"""
import argparse
import datetime as dt
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# Reuse existing CampusCash cashflow model, shipped in the user's main project.
from cashflow import forecast, amount

CENT = Decimal('0.01')
DISCLAIMER = (
    'These are optional educational suggestions, not personalized financial or '
    'investment advice. There is no obligation or compulsion to act. Any decision '
    'is yours and at your own risk. Verify current terms, fees, eligibility and '
    'potential losses independently. CampusCash never moves or invests money for you.'
)



def positive_money(value, name):
    val = amount(value)
    if val < 0:
        raise ValueError(f'{name} cannot be negative')
    return val


def formatted(value):
    return format(value.quantize(CENT, rounding=ROUND_HALF_UP), '.2f')


def analyze_savings(data, days=30):
    if not isinstance(data, dict):
        raise ValueError('Input must be a JSON object')
    if data.get('essentials_reviewed') not in (True, False, None):
        raise ValueError('essentials_reviewed must be true or false')
    base = forecast(data, days=days)
    minimum = Decimal(base['minimum_buffer'])
    base_low = Decimal(base['lowest_projected_balance'])
    delayed_low = Decimal(base['without_unconfirmed_income_scenario']['lowest_balance'])
    stress_limit = min(base_low, delayed_low) - minimum
    reviewed = data.get('essentials_reviewed') is True

    # This is an illustrative transfer/earmark maximum, not an investment recommendation.
    # An explicit confirmation of all essential obligations is required before displaying it.
    conservative = max(Decimal('0.00'), stress_limit).quantize(CENT)
    capacity = formatted(conservative) if reviewed else None
    if base['risk'] == 'SHORTFALL':
        status = 'ESSENTIAL_SHORTFALL'
        next_action = 'Prioritize essential bills and verify payment dates before setting money aside.'
    elif delayed_low < minimum:
        status = 'INCOME_UNCERTAINTY'
        next_action = 'Verify expected income and protect your safety buffer before considering extra savings.'
    elif base_low < minimum:
        status = 'LOW_BUFFER'
        next_action = 'Protect your minimum cash buffer and review optional expenses first.'
    elif not reviewed:
        status = 'NEEDS_OBLIGATION_REVIEW'
        next_action = 'List tuition, housing, food, transport, debt minimums and other upcoming essential bills before estimating surplus.'
    elif conservative == 0:
        status = 'NO_EXTRA_CAPACITY'
        next_action = 'Keep accessible cash for planned essentials and your safety buffer.'
    else:
        status = 'ILLUSTRATIVE_EXTRA_CASH'
        next_action = 'Optional: consider keeping part of the modeled amount in an accessible, appropriately insured savings account after verifying terms.'

    reduction_pct = Decimal(str(data.get('hypothetical_reduction_percent', '10')))
    if not reduction_pct.is_finite() or not Decimal('0') <= reduction_pct <= Decimal('100'):
        raise ValueError('hypothetical_reduction_percent must be 0 through 100')
    categories = data.get('monthly_spending', [])
    if not isinstance(categories, list) or len(categories) > 100:
        raise ValueError('monthly_spending must be a list of up to 100 entries')
    examples = []
    total = Decimal('0.00')
    for i, row in enumerate(categories):
        if not isinstance(row, dict) or not isinstance(row.get('essential'), bool):
            raise ValueError(f'monthly_spending[{i}] requires essential true/false')
        name = str(row.get('category', '')).strip()[:60]
        if not name:
            raise ValueError(f'monthly_spending[{i}] requires a category')
        value = positive_money(row.get('amount'), f'monthly_spending[{i}].amount')
        # Do not frame cuts to tuition, basic groceries, medicine or rent as savings advice.
        if row['essential']:
            continue
        delta = (value * reduction_pct / Decimal('100')).quantize(CENT, rounding=ROUND_HALF_UP)
        total += delta
        if delta:
            examples.append({'category': name, 'monthly_amount': formatted(value),
                             'hypothetical_reduction_percent': str(reduction_pct),
                             'illustrative_monthly_reduction': formatted(delta)})
    examples.sort(key=lambda x: (-Decimal(x['illustrative_monthly_reduction']), x['category'].lower()))

    goal_info = None
    if data.get('savings_goal') is not None:
        goal = data['savings_goal']
        if not isinstance(goal, dict):
            raise ValueError('savings_goal must be an object')
        name = str(goal.get('name', 'Savings goal')).strip()[:60] or 'Savings goal'
        target = positive_money(goal.get('target_amount'), 'savings_goal.target_amount')
        saved = positive_money(goal.get('already_saved', '0'), 'savings_goal.already_saved')
        date = dt.date.fromisoformat(goal['target_date'])
        today = dt.date.fromisoformat(data['as_of'])
        if date <= today:
            raise ValueError('savings_goal.target_date must be in the future')
        remaining = max(Decimal('0.00'), target - saved)
        rate = remaining * Decimal(7) / Decimal((date - today).days)
        goal_info = {'name': name, 'remaining': formatted(remaining),
                     'target_date': date.isoformat(),
                     'illustrative_weekly_pace': formatted(rate),
                     'affordability_not_established': True}

    general_tips = [
        'Compare grocery unit prices within your selected six-city area and plan meals before shopping; verify actual prices.',
        'Check student discounts and secondhand or borrowed textbooks and electronics; verify eligibility.',
        'Review optional subscriptions, delivery fees and dining-out frequency before reducing essentials.',
        'Compare transit, cycling and car rental total costs across selected cities where relevant; consider safety and access needs.',
        'Compare total housing costs in Tempe, Chandler, Mesa, Phoenix, Scottsdale and Gilbert, including utilities, fees, deposits and commute, before switching.',
    ]
    cash_suggestions = (
        ['Protect upcoming essentials and buffer; no extra-money allocation is advised from this scenario.']
        if status != 'ILLUSTRATIVE_EXTRA_CASH'
        else [
            'Optional: increase an accessible emergency fund for unexpected bills.',
            'Optional: earmark funds for known tuition, dorm, rent or other near-term fees.',
            'Optional: review high-interest debt and minimum payment obligations before choosing to save more.',
            'Optional: explore insured savings products and verify accessibility, fees and current rates; no product endorsement.',
            'Long-term investing is a separate decision involving risk of loss, time horizon and suitability; no trade is recommended.',
        ]
    )
    return {
        'status': status,
        'forecast_risk': base['risk'],
        'forecast_lowest_balance': base['lowest_projected_balance'],
        'without_unconfirmed_income_lowest_balance': base['without_unconfirmed_income_scenario']['lowest_balance'],
        'minimum_buffer': base['minimum_buffer'],
        'essentials_reviewed': reviewed,
        'illustrative_cash_available_to_earmark_today': capacity if status == 'ILLUSTRATIVE_EXTRA_CASH' else '0.00' if reviewed else None,
        'surplus_caveat': 'Based only on listed obligations over the forecast window. Not bank-verified; future fees, obligations outside this window and emergencies may change it.',
        'hypothetical_optional_spending_reductions': examples,
        'illustrative_monthly_reduction_total': formatted(total),
        'reduction_caveat': 'What-if reductions, not actual or guaranteed savings. Never reduce required essentials automatically.',
        'savings_goal': goal_info,
        'ways_to_save': general_tips,
        'optional_extra_cash_ideas': cash_suggestions,
        'recommended_next_step': next_action,
        'disclaimer': DISCLAIMER,
    }


def main():
    parser = argparse.ArgumentParser(description='Optional student savings coach (fictional samples only by default)')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--input', help='Private local JSON input')
    group.add_argument('--sample', action='store_true', help='Run the fictional demo')
    parser.add_argument('--days', type=int, default=30)
    args = parser.parse_args()
    filename = (Path(__file__).resolve().parents[1] / 'assets' / 'savings-demo.json') if args.sample else Path(args.input)
    try:
        print(json.dumps(analyze_savings(json.loads(filename.read_text(encoding='utf-8')), days=args.days), indent=2))
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
