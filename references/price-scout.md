# Price Scout research and input format

This feature compares groceries, electronics, housing, restaurants, car rentals, dress rentals, clothing purchases and dorm shopping in the six selected Arizona municipalities: Tempe, Chandler, Mesa, Phoenix, Scottsdale and Gilbert. **It does not connect to a live product database.** Cubbie must research current offers using whatever browsing capability is available, or accept price links/screenshots provided by the student. The script ranks **supplied quotes** only, using Decimal arithmetic.

## Workflow

- Ask: 'What item or cuisine are you looking for across Tempe, Chandler, Mesa, Phoenix, Scottsdale, or Gilbert, and what is your budget? Any travel preference?' Exclude physical locations outside the selected allowed cities; prefer destinations with manageable travel expense.
- For groceries, normalize to the desired quantity. A 6-pack is not inherently cheaper than a 12-pack. Include travel, delivery, taxes and minimum order charges; don't overlook a free campus pantry as an alternative if genuinely applicable and verified.
- For electronics, require the **same** iPad model/generation, storage, Wi-Fi/cellular capability, device condition and warranty. Verify student discounts from the official education store; don't assume they stack with promotions. Compare actual final cost and return policy.
- For restaurants, filter to addresses within the selected allowed cities and group by cuisine. Compare the same meal type, portion and service mode; include menu price, tax, tip, service/delivery fees and transportation. Mark unverified discounts and prices; use direct recent menu links. For living space, distinguish per-bed/per-room rent from whole-unit rent, lease term, move-in date, deposit, application/administrative fees, utilities, internet, parking, renters insurance and commute. Record estimated costs explicitly and check the listing with the landlord; the ASU housing marketplace does not itself guarantee listings.
- Provide direct offer links, checked-on dates, approximate true cost and any uncertainty. Do not fabricate 'real-time' availability, taxes, or travel prices. Never auto-purchase or send deposits.
- Rank only offers whose `comparison_key` matches. For example, `large-eggs-dozen`, `ipad-air-model-storage-connectivity-condition`, and `private-bed-12months-fall2027`. If quotes are incomparable, report them as separate groups, not a false cheapest winner.

## JSON for the ranker

Common fields: `as_of` (student-local YYYY-MM-DD), either `city` (e.g. `Tempe`) or `cities` (a subset of six permitted names), `state` (`AZ`), `category` (`grocery`, `electronics`, `housing`, `restaurant`), `item`, `comparison_key`, `quantity_needed` (1 for electronics/housing), and `offers` (up to 50).

Every offer requires: `seller`, `city` (one of six supported cities), `state` (`AZ`), `address` (verified physical address), `location_verified` (true only after external boundary/address verification), `source_url` (direct public HTTP(S) link), `checked_at` (YYYY-MM-DD), `comparison_key`, `available` (true only if verified), and relevant numeric cost fields encoded as decimal strings. Quotes are excluded if stale, out-of-stock, mismatched, or incomplete. The script does not independently validate links or inventory.

For grocery/electronics offers use `price` (per pack/product), optional `pack_quantity` (default 1), `tax_estimate`, `delivery_fee`, `travel_cost`, and `other_fees` (defaults 0; never assume those estimates are official). `quantity_needed` normalizes groceries to the desired quantity. Electronics comparisons require a quantity and pack size of 1.

Housing offers require `rent_monthly`, `utilities_monthly`, `fees_monthly`, `commute_monthly`, `deposit`, and `move_in_fees`; **estimated values must be labeled** in the conversation. The output shows monthly cost and approximate move-in cash. Set unknown fees aside and do not rank until checked. The 'upfront cash' calculation assumes the first month's estimated costs plus deposit and other move-in fees; actual leasing schedules may differ.

### Run locally on Windows

```cmd
py scripts\compare_offers.py --sample
py -m unittest discover -s tests -v
```

`assets/price-demo.json` contains **fictional stores and amounts**; it is a sample of the JSON structure, not current pricing near ASU.

## Student reply example (not real prices)

'Among the two fictional egg quotes, Market B totals $4.50 for twelve eggs including estimated travel, versus $5.00 at Market A. These prices are DEMO ONLY. Want me to check live links or work with screenshots you've provided and then assess affordability after rent?'

## Restaurant JSON (single city or multi-city)
See `assets/restaurant-demo.json` for synthetic venues and synthetic prices. Set `category: "restaurant"`, `service_mode` to `dine-in`, `takeout`, or `delivery`, `comparison_key` to a comparable meal/portion/service type, and optional `cuisine: "Indian"` to limit the cuisine. Each restaurant offer requires `cuisine`, `dish`, `service_mode` (dine-in/takeout/delivery), `price`, `tax_estimate`, `tip_estimate`, `service_fee`, `delivery_fee`, `travel_cost`. **All costs required** so missing fees are not silently assumed zero. Known zero is explicit "0.00". The script groups ranking by cuisine and does not claim one overall cheapest restaurant across dissimilar cuisines. Mode is for one complete comparable meal (`quantity_needed: 1`). `location_verified` is evidence supplied by prior research, not geocoding the script itself.

Tempe boundary example (verify other cities independently): https://www.arcgis.com/home/item.html?id=660f9b04f0c044999e6bcd23e749ef1b. Tempe Tourism restaurants: https://www.tempetourism.com/things-to-do/food-and-drink/; Downtown Tempe dining: https://www.downtowntempe.com/dining. Discovery directories are *not* price verification.

## Car and dress rentals / apparel / other shopping
See `references/tempe-shopping-rentals.md`. Rental deposits or payment holds are NOT consumption. `--car-sample`, `--dress-sample`, and `--shopping-sample` are synthetic demos.

**Multi-city use:** Replace top-level `city: Tempe` with `cities: ["Tempe","Chandler","Mesa","Phoenix","Scottsdale","Gilbert"]`, leaving `state: AZ`. Do not include `city` and `cities` together. See `references/metro-coverage.md` for details.
