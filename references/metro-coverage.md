# CampusCash Greater Phoenix six-city coverage

## Allowed cities
Tempe, Chandler, Mesa, Phoenix, Scottsdale, and Gilbert, Arizona only. They are eligible **municipalities**, not an unrestricted radius around campus. Never silently include Glendale, Guadalupe, Tucson, Apache Junction, unincorporated locations or other cities. Place-name labels and ZIP codes are insufficient to verify municipal boundaries. Confirm street address/branch against trusted sources before setting `location_verified: true`; the local calculation script does **not** geocode.

## How to search
- For non-emergency local place and shopping queries, ask the student to specify a supported city unless one was already given; do not default to all six. Search another supported city only with permission. An immediate emergency bypasses this clarification. Offer optional filters: one city, maximum travel budget, transport method, cuisine, price ceiling, ratings, dietary needs, timeframe and availability. Avoid asking for a personal residential address; use 'ASU Tempe campus' or a general starting area if needed.
- Only use sources tied to an actual branch, menu, item or listing, with `source_url`, `checked_at`, availability and address verified. A chain having a branch in Phoenix does not imply an identical offer in Tempe. Live pricing and availability require real current research; the Python engine only compares supplied offers.
- Compare **final costs** (tax/fees + travel) rather than sticker price. For multi-city groceries/electronics/clothing/shopping, enter explicit `travel_cost` and `tax_estimate`; neither can be silently assumed zero. For restaurants, use priced meals plus tax/tip/service/delivery/travel. For housing, include approximate monthly commute. For car/dress rentals, include eligible pickup AND return cities, dates, deposits/holds and relevant travel/return fees. Never invent mileage, drive times, rates, inventory or discounts.
- Show the strongest 2–3 *comparable* offers with city, source URL, checked date, true estimated cost and tradeoffs. If no verified offers exist, say so and provide a research checklist, not a fabricated cheapest result. Respect any student-selected maximum travel time or cost using checked routes when available.
- Run the optional savings/affordability check **only after reviewing essentials**, preserving an emergency buffer and emphasizing that all action is voluntary.

## JSON request schema

Single-city (backward compatible): `{"as_of":"2026-10-24","city":"Tempe","state":"AZ", ...}`.

Multi-city: `{"as_of":"2026-10-24","cities":["Tempe","Chandler","Mesa","Phoenix","Scottsdale","Gilbert"],"state":"AZ",...}`.

Use either `city` or `cities`, never both. Offer rows still require `city`, `state`, `address`, `location_verified`, `checked_at`, `source_url`, `comparison_key`, and category-specific fields. Rental return cities must also be included in the selected city list and independently verified. Output contains `ranked_offers`, `ranked_by_city`, and, for restaurants, `ranked_by_cuisine`. Excluded quotes include a reason.

## Run a synthetic multi-city test

Windows: `py scripts\compare_offers.py --metro-sample`
Linux/macOS: `python3 scripts/compare_offers.py --metro-sample`

`assets/metro-demo.json` contains **fictional stores, addresses, prices and URLs**; it does not prove live local availability.

## Communication guideline

If two comparable offers have different sticker prices but the cheaper one requires a costly cross-city trip, explain the difference and recommend based on *total estimated cost*, not just shelf price. For housing, emphasize commute reliability and upfront deposits. For dining, separate cuisine groupings and service modes. A current quote from Tempe does not establish prices for Mesa, Phoenix, or the other four cities.
