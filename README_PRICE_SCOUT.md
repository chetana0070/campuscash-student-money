# CampusCash Price Scout — optional update

Adds a source-linked cost comparison workflow for groceries, electronics, housing, **restaurants by cuisine**, car rentals, dress rentals, clothing and general shopping, inside a selectable six-city Arizona area: Tempe, Chandler, Mesa, Phoenix, Scottsdale and Gilbert. **Live discovery is performed by Cubbie if available, or supplied by users—not by the Python script.** The bundled quotes are fictional.

**After copying these update files into the root of your existing CampusCash repository**, from Windows Command Prompt:

```cmd
cd /d "%USERPROFILE%\OneDrive\Documents\campuscash-student-money"
py scripts\compare_offers.py --sample
py scripts\compare_offers.py --restaurant-sample
py scripts\compare_offers.py --car-sample
py scripts\compare_offers.py --dress-sample
py scripts\compare_offers.py --shopping-sample
py -m unittest discover -s tests -v
py "%USERPROFILE%\OneDrive\Documents\cubbie-hackathon-kit\skills\cubbie-skill-creator\scripts\validate_cubbie_skill.py" .
git status
git add SKILL.md README_PRICE_SCOUT.md scripts\compare_offers.py tests\test_compare_offers.py tests\test_tempe_restaurants.py tests\test_shopping_rentals.py assets\price-demo.json assets\restaurant-demo.json assets\car-rental-demo.json assets\dress-rental-demo.json assets\shopping-demo.json references\price-scout.md references\tempe-restaurants.md references\tempe-shopping-rentals.md
git commit -m "Add six-city prices, restaurant cuisines, car and dress rentals, shopping"
git push origin main
```

After push, ask Cubbie to **refresh/reinstall the Skill** from https://github.com/chetana0070/campuscash-student-money and verify the new capability. It must not claim to have live prices if browsing/availability is unverified.

Example prompts:
- 'Find the lowest true cost for 12 eggs near ASU Tempe. Show direct retailer links, when checked, travel cost, and compare with my grocery budget.'
- 'Find the best verified student price for an iPad Air with these exact specs. Include sales tax and transport or shipping.'
- 'Compare private rooms near ASU Tempe for a 12-month lease. Include utilities, fees, commute and move-in cash, not just the advertised rent.'

Privacy: no private student balances or receipts in public repos. No passwords, banking connections, purchases or lease commitments.

New restaurant test prompt:

> "Use CampusCash to find vegetarian Indian lunch in **Tempe, Chandler, Mesa, Phoenix, Scottsdale and Gilbert, AZ**, and compare current menu prices for similar takeout meals. Include taxes/fees/transport, menu links, last checked dates, and affordability after my upcoming bills. Compare equivalent meals, travel costs and city labels."

**Disclosure:** `location_verified: true` is provided by the research step; the offline script does not itself verify GIS coordinates or real-world restaurant menus. The example venues and prices are fictional.

### Rental-specific cautions

Car quotes require eligibility confirmation and comparable coverage; refundable deposits are separate from costs. Dress rental quotes require fit, return location and all fee estimates. All examples are fictional. Do not claim to have live real-world quotes or confirmed renter eligibility until official sources are checked.

To compare all six cities use `--metro-sample` and see `references/metro-coverage.md`; legacy `city: Tempe` queries still search only Tempe.
