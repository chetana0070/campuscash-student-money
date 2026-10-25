# CampusCash AI — Cubbie Hackathon Track 1

An iMessage-first student money copilot combining **30-day cash-flow forecasts** with **six-city Greater Phoenix Price Scout**. The Skill helps college students protect essentials, compare current public offers, and make budget-aware buying or rental choices. All bundled prices and vendors are **fictional**. Live prices and inventory are **not** embedded in this repository.

## Capabilities

- Cash-flow forecasting with dated income and expenses, minimum balance buffer, and missed-paycheck stress scenario.
- Price comparisons across Tempe, Chandler, Mesa, Phoenix, Scottsdale and Gilbert for groceries, electronics, rooms/housing, restaurants by cuisine and service mode.
- **Car rentals** across these six cities, comparing same dates, vehicle class, fees, age-related surcharges, protection options, mileage and fuel estimates; refundable card holds separate from costs.
- **Dress rentals** across these six cities, comparing rental periods, size availability, cleaning/return costs and refundable deposits.
- **Clothing and general shopping** across these six cities, accounting for item condition, size, applicable fees, travel and verified return policies.
- Optional 'Can I afford this?' step using the existing cash-flow script, never making purchases or bookings.
- **Savings Coach:** voluntary ways to reduce nonessential spending, account for campus obligations first, calculate cautious hypothetical leftover cash, and explore emergency savings or other optional uses without auto-transfers or product endorsements.

Every physical seller, restaurant, property, rental pickup and rental return must be in a **selected city among Tempe, Chandler, Mesa, Phoenix, Scottsdale and Gilbert (AZ)**. A search can target one city or all six, and cross-city rankings require estimated travel and tax inputs. The script does not independently geocode or search the web; Cubbie or the student supplies verified current public quotes with source links and dates.

## Windows local commands

From `campuscash-student-money` in Windows Command Prompt:

```cmd
py scripts\cashflow.py --sample
py scripts\compare_offers.py --sample
py scripts\compare_offers.py --restaurant-sample
py scripts\compare_offers.py --car-sample
py scripts\compare_offers.py --dress-sample
py scripts\compare_offers.py --shopping-sample
py scripts\savings_coach.py --sample
py -m unittest discover -s tests -v
```

To validate with the downloaded organizer kit:

```cmd
py "%USERPROFILE%\OneDrive\Documents\cubbie-hackathon-kit\skills\cubbie-skill-creator\scripts\validate_cubbie_skill.py" .
```

## Install or update in Cubbie

1. Publish the contents of this repository at https://github.com/chetana0070/campuscash-student-money .
2. Share the GitHub repository URL in the Cubbie conversation and explicitly ask Cubbie to **update** the installed Skill from the latest commit.
3. Wait for Cubbie to confirm which version was installed, then run a fictional comparison prompt. Validate the numerical output against the CLI demo.
4. Record the **real Cubbie response**, not fabricated screenshots, for any hackathon demo.

## Privacy and trust

No banking passwords, real account data, identity documents, card details, or sensitive receipts in public GitHub. No external finance server. No automatic purchases, rental reservations, lease agreements or deposits. Treat pricing, student discounts, driver eligibility and deposit/insurance policies as unverified until checked at the actual Tempe vendor.

Savings Coach always gives optional, no-compulsion, at-your-own-risk guidance. See `references/savings-coach.md`.

Detailed sourcing instructions: `references/price-scout.md`, `references/tempe-restaurants.md` and `references/tempe-shopping-rentals.md`.

## Regional Price Scout demo (six cities; fictional data)

Run `py scripts\compare_offers.py --metro-sample` on Windows, or `python3 scripts/compare_offers.py --metro-sample` on Linux. This compares fictional stores in all six cities using unit costs and entered transportation estimates; no real stores or prices are implied.

See `references/metro-coverage.md` for the `cities` JSON format, limitations, and regional search policy.
