"""Compare sourced, same-spec price quotes collected by Cubbie or entered by students.

No web access, bank access or affiliate recommendations; never manufactures prices.
"""
import argparse
import datetime as dt
import json
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path

# Supported Arizona municipalities for CampusCash regional discovery.
SUPPORTED_CITIES = ('Tempe', 'Chandler', 'Mesa', 'Phoenix', 'Scottsdale', 'Gilbert')
CITY_NAMES = {name.casefold(): name for name in SUPPORTED_CITIES}


def normalize_city(value):
    return CITY_NAMES.get(str(value).strip().casefold())


def selected_cities(data):
    """Accept legacy single-city queries or an explicit selection of 1–6 cities."""
    if str(data.get('state', '')).strip().upper() != 'AZ':
        raise ValueError('Only Arizona locations in the six supported cities are allowed')
    if 'cities' in data:
        if 'city' in data:
            raise ValueError('Use either city or cities, not both')
        raw = data['cities']
        if not isinstance(raw, list) or not 1 <= len(raw) <= len(SUPPORTED_CITIES):
            raise ValueError('cities must list 1 to 6 supported Arizona cities')
    else:
        raw = [data.get('city') if 'city' in data else None]
    names = [normalize_city(name) for name in raw]
    if None in names or len(names) != len(set(names)):
        raise ValueError('Choose distinct cities from Tempe, Chandler, Mesa, Phoenix, Scottsdale, Gilbert (AZ)')
    return names


def dec(value, label, minimum=Decimal('0')):
    if isinstance(value, bool):
        raise ValueError(f'{label} must be a number')
    try:
        v = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f'{label} must be a number') from None
    if not v.is_finite() or v < minimum or v > 100000000:
        raise ValueError(f'{label} is outside the permitted range')
    return v


def dollars(value):
    return format(value.quantize(Decimal('.01')), '.2f')


def compare(data):
    if not isinstance(data, dict):
        raise ValueError('Input must be a JSON object')
    mode = data.get('category')
    if mode not in ('grocery', 'electronics', 'housing', 'restaurant', 'car_rental', 'clothing', 'dress_rental', 'shopping'):
        raise ValueError('category must be grocery, electronics, housing, restaurant, car_rental, clothing, dress_rental or shopping')
    # A single Tempe request remains Tempe-only; 'cities' enables regional comparison.
    cities = selected_cities(data)
    allowed_cities = set(cities)
    date = dt.date.fromisoformat(data['as_of'])
    key = data['comparison_key']
    if not isinstance(key, str) or not key.strip():
        raise ValueError('comparison_key must describe equal specs or lease terms')
    offers = data.get('offers')
    if not isinstance(offers, list) or len(offers) > 50:
        raise ValueError('offers must be a list of up to 50 quotes')
    quantity = dec(data.get('quantity_needed', 1), 'quantity_needed', Decimal('0.00001'))
    found, excluded = [], []
    freshness = {'grocery': 7, 'electronics': 14, 'housing': 3, 'restaurant': 7,
                 'car_rental': 2, 'clothing': 7, 'dress_rental': 3, 'shopping': 7}[mode]
    wanted_cuisine = str(data.get('cuisine', '')).strip().casefold() if mode == 'restaurant' else ''
    requested_service = str(data.get('service_mode', '')).strip().lower() if mode == 'restaurant' else ''
    if mode == 'restaurant' and requested_service not in ('dine-in','takeout','delivery'):
        raise ValueError('restaurant comparisons require service_mode: dine-in, takeout or delivery')
    rental_days = None
    if mode in ('car_rental','dress_rental'):
        value = data.get('rental_days')
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 60:
            raise ValueError('rental_days must be a whole number between 1 and 60')
        rental_days = value
    coverage_key = data.get('coverage_key') if mode == 'car_rental' else None
    if mode == 'car_rental' and (not isinstance(coverage_key, str) or not coverage_key.strip()):
        raise ValueError('car rental requires a coverage_key to compare identical protection choices')
    for index, offer in enumerate(offers):
        if not isinstance(offer, dict):
            excluded.append({'offer': index + 1, 'reason': 'invalid quote'})
            continue
        name = str(offer.get('seller', f'Offer {index+1}'))[:80]
        reason = None
        try:
            url = offer['source_url']
            checked = dt.date.fromisoformat(offer['checked_at'])
            if not isinstance(url, str) or not url.startswith(('https://', 'http://')):
                reason = 'missing direct source URL'
            elif checked > date or (date - checked).days > freshness:
                reason = 'stale or future-dated quote'
            elif normalize_city(offer.get('city')) not in allowed_cities or str(offer.get('state', '')).strip().upper() != 'AZ':
                reason = 'location outside requested Arizona cities or unverified'
            elif offer.get('location_verified') is not True or not str(offer.get('address', '')).strip():
                reason = 'physical location/address not independently verified'
            elif offer.get('comparison_key') != key:
                reason = 'different product specification or lease terms'
            elif offer.get('available') is not True:
                reason = 'availability unconfirmed'
            elif mode == 'restaurant' and str(offer.get('service_mode', '')).strip().lower() != requested_service:
                reason = 'different service mode'
            elif mode == 'restaurant' and wanted_cuisine and str(offer.get('cuisine','')).strip().casefold() != wanted_cuisine:
                reason = 'outside requested cuisine'
            elif mode in ('car_rental', 'dress_rental') and (offer.get('rental_days') != rental_days):
                reason = 'different rental duration'
            elif mode in ('car_rental', 'dress_rental') and (
                offer.get('return_location_verified') is not True
                or normalize_city(offer.get('return_city')) not in allowed_cities
                or str(offer.get('return_state', '')).strip().upper() != 'AZ'
                or not str(offer.get('return_address', '')).strip()):
                reason = 'return location outside requested Arizona cities or unverified'
            elif mode == 'car_rental' and (offer.get('coverage_key') != coverage_key):
                reason = 'insurance/protection coverage not comparable'
            elif mode == 'car_rental' and offer.get('driver_eligible') is not True:
                reason = 'renter eligibility not verified for this branch and driver'
            elif mode == 'dress_rental' and offer.get('fit_available') is not True:
                reason = 'requested size/fit unavailable or unverified'
            elif mode == 'clothing' and (offer.get('size_available') is not True or offer.get('return_policy_checked') is not True):
                reason = 'clothing size/return policy unverified'
            elif mode == 'shopping' and offer.get('return_policy_checked') is not True:
                reason = 'return policy unverified'
            elif mode == 'car_rental':
                # Charges and refundable card holds are deliberately separated.
                cost = dec(offer['daily_rate'], 'daily_rate') * rental_days
                cost += dec(offer['young_driver_fee_per_day'], 'young_driver_fee_per_day') * rental_days
                fields = ('tax_estimate','mandatory_fees','insurance_or_coverage_total',
                          'fuel_estimate','mileage_fee_estimate','pickup_travel_cost','return_travel_cost')
                cost += sum((dec(offer[f], f) for f in fields), Decimal('0'))
                hold = dec(offer['refundable_deposit_hold'], 'refundable_deposit_hold')
                row = {'seller': name, 'source_url': url, 'checked_at': checked.isoformat(),
                       'rental_days': rental_days, 'coverage_key': coverage_key,
                       'pickup_address': str(offer['address']), 'return_address': str(offer['return_address']),
                       'mileage_policy': str(offer['mileage_policy'])[:90],
                       'estimated_checkout_total': dollars(cost),
                       'refundable_deposit_hold': dollars(hold),
                       'potential_funds_needed_including_hold': dollars(cost+hold),
                       'basis': 'same-class vehicle and rental period; entered price, mandatory fees, estimated fuel, mileage, protection and travel included; card hold kept separate'}
                if not row['mileage_policy'].strip():
                    raise ValueError('mileage_policy is required')
            elif mode == 'dress_rental':
                fields = ('rental_fee','tax_estimate','cleaning_fee','service_fee',
                          'travel_cost','return_fee','damage_waiver_total')
                cost = sum((dec(offer[f], f) for f in fields), Decimal('0'))
                deposit = dec(offer['refundable_deposit'], 'refundable_deposit')
                row = {'seller': name, 'source_url': url, 'checked_at': checked.isoformat(),
                       'rental_days': rental_days, 'dress_size': str(offer.get('size', ''))[:30],
                       'pickup_address': str(offer['address']), 'return_address': str(offer['return_address']),
                       'estimated_checkout_total': dollars(cost), 'refundable_deposit_hold': dollars(deposit),
                       'potential_funds_needed_including_hold': dollars(cost+deposit),
                       'basis': 'dress rental for equal duration/size/style, including cleaning, service, damage coverage, return and travel estimates'}
            elif mode == 'housing':
                monthly = sum((dec(offer[field], field) for field in
                    ('rent_monthly', 'utilities_monthly', 'fees_monthly', 'commute_monthly')), Decimal('0'))
                upfront = monthly + dec(offer['deposit'], 'deposit') + dec(offer['move_in_fees'], 'move_in_fees')
                row = {'seller': name, 'source_url': url, 'checked_at': checked.isoformat(),
                       'monthly_total': dollars(monthly), 'approx_move_in_cash': dollars(upfront),
                       'deposit_included_in_move_in_cash': dollars(dec(offer['deposit'], 'deposit')),
                       'basis': 'monthly cost including user-entered utility, fee and commute estimates'}
            elif mode == 'restaurant':
                cuisine = str(offer.get('cuisine','')).strip()[:40]
                dish = str(offer.get('dish','')).strip()[:100]
                service = str(offer.get('service_mode','')).strip().lower()
                if not cuisine or not dish or service not in ('dine-in','takeout','delivery'):
                    raise ValueError('cuisine, dish and service_mode (dine-in/takeout/delivery) required')
                if quantity != 1:
                    raise ValueError('restaurant quotes are priced per one comparable meal')
                required = ('price','tax_estimate','tip_estimate','service_fee','delivery_fee','travel_cost')
                cost = sum((dec(offer[f], f) for f in required), Decimal('0'))
                row = {'seller': name, 'cuisine': cuisine, 'dish': dish, 'service_mode': service,
                       'address': str(offer['address']), 'source_url': url, 'checked_at': checked.isoformat(),
                       'estimated_checkout_total': dollars(cost),
                       'basis': 'one comparable meal with entered tax, tip, service, delivery and travel estimates'}
            else:
                # Cross-city ranking must include a sourced/entered estimate for travel and tax.
                if len(cities) > 1 and ('travel_cost' not in offer or 'tax_estimate' not in offer):
                    raise ValueError('multi-city quotes require explicit travel_cost and tax_estimate (use 0 only when verified)')
                pack = dec(offer.get('pack_quantity', 1), 'pack_quantity', Decimal('0.00001'))
                if mode == 'electronics' and (pack != 1 or quantity != 1):
                    raise ValueError('electronics quotes require exactly one product')
                packs = int((quantity / pack).to_integral_value(rounding=ROUND_CEILING))
                cost = dec(offer['price'], 'price') * packs
                cost += sum((dec(offer.get(f, '0'), f) for f in
                    ('tax_estimate', 'delivery_fee', 'travel_cost', 'other_fees')), Decimal('0'))
                row = {'seller': name, 'source_url': url, 'checked_at': checked.isoformat(),
                       'estimated_checkout_total': dollars(cost), 'packs_to_buy': packs,
                       'basis': 'same-spec total for requested quantity including provided fees'}
            if reason:
                excluded.append({'seller': name, 'reason': reason})
            else:
                row['city'] = normalize_city(offer.get('city'))
                row['state'] = 'AZ'
                row['address'] = str(offer['address'])
                if mode in ('car_rental', 'dress_rental'):
                    row['return_city'] = normalize_city(offer.get('return_city'))
                found.append(row)
        except (KeyError, ValueError, TypeError) as error:
            excluded.append({'seller': name, 'reason': f'incomplete or invalid quote: {error}'})
    field = 'monthly_total' if mode == 'housing' else 'estimated_checkout_total'
    found.sort(key=lambda r: Decimal(r[field]))
    by_city = {city: [row for row in found if row['city'] == city] for city in cities}
    by_cuisine = {}
    if mode == 'restaurant':
        for r in found:
            by_cuisine.setdefault(r['cuisine'], []).append(r)
    return {'category': mode, 'city': cities[0] if len(cities) == 1 else None,
            'cities': cities, 'state': 'AZ', 'ranked_by_city': by_city,
            'ranked_by_cuisine': by_cuisine if mode == 'restaurant' else None, 'item': data.get('item', ''), 'as_of': date.isoformat(),
            'comparison_key': key, 'ranked_offers': found, 'excluded_offers': excluded,
            'lowest_comparable_quote': found[0]['seller'] if found and (mode != 'restaurant' or len(by_cuisine) == 1) else None,
            'note': 'Rankings use only provided quotes tagged as verified within the selected six-city Arizona coverage area. This calculator does not independently verify municipal boundaries, travel estimates, addresses, inventory, prices, rental eligibility, terms, or links. For cross-city comparisons include travel/commute costs. Rental deposits are temporary holds, not spending. Best means cheapest only among checked comparable offers. Dress rentals and purchases must be compared separately.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Rank sourced offers near a campus, no live scraping')
    p.add_argument('--input', type=Path)
    p.add_argument('--sample', action='store_true')
    p.add_argument('--restaurant-sample', action='store_true')
    p.add_argument('--car-sample', action='store_true')
    p.add_argument('--dress-sample', action='store_true')
    p.add_argument('--shopping-sample', action='store_true')
    p.add_argument('--metro-sample', action='store_true', help='Compare six-city fictional grocery quotes')
    args = p.parse_args()
    if not any((args.sample, args.restaurant_sample, args.car_sample, args.dress_sample, args.shopping_sample, args.metro_sample, args.input)):
        p.error('pass --input <private-json>, --sample, --restaurant-sample, --car-sample, --dress-sample, --shopping-sample or --metro-sample')
    demos = {'sample': 'price-demo.json', 'restaurant_sample': 'restaurant-demo.json',
             'car_sample': 'car-rental-demo.json', 'dress_sample': 'dress-rental-demo.json',
             'shopping_sample': 'shopping-demo.json', 'metro_sample': 'metro-demo.json'}
    selected = next((name for flag, name in demos.items() if getattr(args, flag)), None)
    path = (Path(__file__).resolve().parents[1] / 'assets' / selected) if selected else args.input
    try:
        print(json.dumps(compare(json.loads(path.read_text(encoding='utf-8'))), indent=2))
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        p.error(str(exc))
