-- A notebook-readable contract prevents visual labels from obscuring what each
-- measure answers, its source period, or the inference it cannot support.
select * from (values
    ('Renter burden at 30%+', 'pct_rent_burden_30plus', 'ACS B25070 renter households', '2024 level; five-year change where complete', 'Household burden; the 30% threshold is valid', 'Not a median-rent price level'),
    ('Median-rent-to-all-household-income price proxy', 'median_rent_to_all_hh_income_proxy', 'ACS median gross rent / ACS all-household median income', '2024 level; five-year change where complete', 'Prevailing rent relative to broad local income', 'Not a renter-household burden test; no 30% or 50% cutoff'),
    ('Value-to-income market-entry proxy', 'value_to_income', 'ACS median home value / ACS all-household median income', '2024 level; five-year change where complete', 'Asset-price access proxy', 'Not a monthly buyer payment or owner burden'),
    ('Existing-owner cost context', 'median_owner_costs_*', 'ACS selected monthly owner costs, split by mortgage status', '2024 level; five-year change where complete', 'Costs reported by existing owners', 'Not current-buyer affordability'),
    ('Home-price momentum', 'hpi_5yr_pct', 'FHFA HPI', 'Five years ending 2024', 'Canonical CBSA/county home-price momentum', 'Not demand by itself'),
    ('Rent momentum', 'rent_growth_5yr', 'ACS median gross rent', 'Five years ending 2024', 'Canonical parallel rent momentum', 'Not renter burden by itself'),
    ('Supply response', 'housing_unit_growth_5yr; permits_5yr_per_1000_start_units', 'ACS housing stock; Census BPS permits', 'Five years ending 2024', 'Realized stock growth and construction response', 'Not valid at tract/ZCTA grain'),
    ('Demand', 'pop_growth_5yr', 'ACS population', 'Five years ending 2024', 'Resident demand context', 'Not a causal explanation on its own')
) as contract(display_name, field_name, source, period, valid_interpretation, prohibited_inference);
