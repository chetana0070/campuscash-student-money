# Shopping and Rentals in Tempe, Chandler, Mesa, Phoenix, Scottsdale and Gilbert

## Finding reliable local offers

All physical pickup, shopping and return addresses must be verified within one of the **six selected Arizona municipalities**, not just a Tempe ZIP code. Use the municipal boundary data or authoritative map; the offline script trusts (but cannot independently validate) supplied `location_verified` and `return_location_verified` flags. Include direct verified listing or branch URLs with date checked. If Cubbie cannot browse, ask for links/screenshots and compare those rather than claiming current quotes.

Sources to **start research**, not preapproved offers:
- Tempe Tourism Shopping: https://www.tempetourism.com/things-to-do/shopping/ (centers, outlet shopping, secondhand clothing)
- Tempe Tourism vintage/resale guide: https://www.tempetourism.com/blog/fun-unique-vintage-stores-tempe/ (recheck businesses and address)
- Tempe Tourism student shopping guide: https://www.tempetourism.com/blog/tempe-101-a-prep-course-asu/
- Individual car rental agencies' official Tempe branch pages and exact quote/terms pages, e.g. https://www.enterprise.com/en/car-rental-locations/us/az/tempe-s-priest-dr-5096.html . The quoted age surcharge and requirements can change; verify branch-specific rates and eligibility. Use other local agencies only with verified pickup and return addresses in selected cities.
- Official municipal boundary layer: https://www.arcgis.com/home/item.html?id=660f9b04f0c044999e6bcd23e749ef1b

## Four request types

1. **Car rental** `category: car_rental`: compare one vehicle class, exact dates/duration, age requirements, driver eligibility, comparable coverage plan and eligible-city pickup/return. Request `rental_days` (1..60), `coverage_key` (same in offers), and `comparison_key` including car class/date window. Every valid offer must have `daily_rate`, `young_driver_fee_per_day`, `tax_estimate`, `mandatory_fees`, `insurance_or_coverage_total`, `fuel_estimate`, `mileage_fee_estimate`, `pickup_travel_cost`, `return_travel_cost`, `refundable_deposit_hold`, `mileage_policy`, `driver_eligible: true`, and validated return location (`return_address`, `return_city` in selected cities, `return_state: AZ`, `return_location_verified: true`). A $0 field must explicitly be `"0.00"`. Rental quotes get stale after 2 days. Upfront card funds may be cost PLUS a hold, subject to actual branch rules. **Do not treat refundable holds as expenditure**. Do not advise using unauthorized credit cards or insurance.
2. **Dress rental** `category: dress_rental`: separate from clothing purchases. Set `rental_days`, `comparison_key` including garment type, size, occasion and dates; every quote must have `rental_fee`, `tax_estimate`, `cleaning_fee`, `service_fee`, `travel_cost`, `return_fee`, `damage_waiver_total`, `refundable_deposit`, `fit_available: true`, and verified return location in the selected coverage area. Confirm policy for late return, stains/damage, alterations, try-on, exchanges and sanitation. Quotes older than 3 days excluded.
3. **Buy clothing/outfits** `category: clothing`: compare similar items, exact size, new/used condition, return policies and taxes. Offers require `price`, `tax_estimate`, `delivery_fee`, `travel_cost`, `other_fees`, `size_available: true`, `return_policy_checked: true`. Compare sale or discount only if eligibility verified. Quotes older than 7 days excluded.
4. **Shopping/dorm supplies** `category: shopping`: compare purchase price with tax, transport, delivery and other costs; require verified returns, exact items/specs. Quotes older than 7 days excluded. If user requests thrift, prioritize reliable selected-city resale sources where the actual product/condition can be verified.

Every offer includes: `seller`, `city`, `state`, `address`, `location_verified`, `source_url`, `checked_at`, `comparison_key`, `available`. The top-level JSON must include `as_of`, `category`, either `city` or `cities`, `state: AZ`, `item`, `comparison_key`, `quantity_needed` (typically 1), and `offers` (up to 50). All cash figures strings.

## Decisions and guardrails

- Ranking is lowest **estimated checkout total among supplied comparable quotes**, not blanket 'best in Greater Phoenix'. Split decisions by priorities: lowest cost, flexible return, shortest travel, warranty, style/fit, or risk.
- A missing quote, taxes, terms or availability means no false comparison. Discount codes, student status and promo exclusions must be checked.
- For rentals, use a signed contract only from legitimate provider after verifying total, deposits/holds, minimum age and insurance. Never say car rentals are possible for a driver based solely on their age, and never collect identifying documents via chat.
- Run a 'can I afford it?' scenario only after the student agrees; essential bills and the minimum buffer remain the gate. Card holds must be checked against accessible payment method limits separately from cash forecasts.
- Show 2-3 verified in-scope sources with city labels and cite checked quote pages; if no comparable live data, say 'I could not verify pricing in the selected cities right now' and offer useful next steps rather than inventing prices.

**Regional change:** Any of the six covered cities is eligible if included in the request. Pickup and return may be in different selected cities only when current branch terms permit it and one-way fees are included. `--metro-sample` is a fictional cross-city example for groceries; apply the same `cities` list to rental quotes. See `references/metro-coverage.md`.
