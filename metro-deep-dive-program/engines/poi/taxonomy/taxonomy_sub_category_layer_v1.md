# POI Taxonomy: Sub Category Draft v0

Companion to `poi_category_spec_v1.md`, which defines the Category layer and the
governance rules. Read the source field rule below before implementing anything
here.

Grounded in the 258 distinct `basic_category` values in the source file
(61,513 places). Category layer as agreed: 21 categories plus Unclassified.

## Source field rule

The field names are actively misleading. `basic` sounds legacy and `primary`
sounds current. It is the other way around.

| Column in the extract | Overture property | Status |
|---|---|---|
| `source_category_basic` | `basic_category` (new, ~280 values) | **Current. Build on this.** |
| `source_category_primary` | `categories.primary` (legacy) | **Deprecated.** Removed in the September 2026 release |

**`source_category_primary` is NOT `taxonomy.primary`.** They are different
vocabularies from different taxonomy generations. Evidence from the extract
itself: one row carries `source_category_basic = food_and_drink` alongside
`source_category_primary = eat_and_drink`. `food_and_drink` is the new
taxonomy's top-level bucket; `eat_and_drink` is the old one.

`taxonomy.primary` and `taxonomy.hierarchy` are **not in the current extract**
and require a re-pull. Every `[T]` row below is blocked on that re-pull and
cannot be implemented against the `source_category_primary` column.

Notation:
- **[B]** derivable from `basic_category` alone. Implementable today
- **[T]** requires `taxonomy.primary` or a `taxonomy.hierarchy` traversal.
  Blocked on the re-pull. Do not substitute `source_category_primary`
- **[U]** unspecified bucket, holds source values that name a category but no sub-category

---

## Food & Drink (~5,700 places)

| Sub Category | Source | Notes |
|---|---|---|
| Restaurants | [B] `restaurant`, `casual_eatery` | Cuisine goes to Detailed |
| Quick Service | [B] `fast_food_restaurant`, `food_truck_stand`, `food_court` | |
| Cafes & Coffee | [B] `coffee_shop`, `cafe`, `smoothie_juice_bar` | |
| Bars & Lounges | [B] `bar`, `lounge`, `alcoholic_beverage_venue`, `non_alcoholic_beverage_venue` | |
| Breweries, Wineries & Distilleries | [B] `brewery`, `winery`, `distillery` | Production plus tasting room |
| Catering & Food Services | [B] `food_service` | Delivery services, caterers, consultants |
| Unspecified | [U] `food_and_drink` | |

`casual_eatery` sits under `restaurant` in the Overture hierarchy, so it rolls up
to Restaurants rather than Quick Service.

## Retail (~8,000 places)

| Sub Category | Source | Notes |
|---|---|---|
| Grocery & Food Retail | [B] `food_and_beverage_store`, `farmers_market`, `market` | Daily-needs basket input |
| Convenience Stores | [B] `convenience_store` | Kept separate from grocery for access analysis |
| Pharmacy & Drug Stores | [B] `pharmacy_and_drug_store` | Daily-needs basket input |
| General Merchandise | [B] `department_store`, `discount_store`, `superstore`, `warehouse_club_store`, `shopping_mall`, `kiosk` | |
| Apparel & Accessories | [B] `fashion_and_apparel_store` | |
| Home, Hardware & Garden | [B] `hardware_home_and_garden_store`, `office_supply_store` | |
| Electronics & Media | [B] `electronics_store`, `books_music_and_video_store`, `musical_instrument_and_pro_audio_store` | |
| Specialty Retail | [B] `specialty_store`, `arts_crafts_and_hobby_store`, `toys_and_games_store`, `flowers_and_gifts_store`, `animal_and_pet_store`, `personal_care_and_beauty_store`, `sporting_goods_store` | |
| Resale & Secondhand | [B] `second_hand_store` | |
| Unspecified | [U] `shopping` | |

## Healthcare (~7,900 places)

| Sub Category | Source | Notes |
|---|---|---|
| Primary & General Care | [B] `primary_care_or_general_clinic`, `walk_in_clinic` | |
| Hospitals & Emergency | [B] `hospital`, `specialty_hospital`, `emergency_department`, `emergency_or_urgent_care_facility`, `urgent_care_clinic` | |
| Specialty Care | [B] `specialized_health_care`, `specialized_medical_facility`, `surgery`, `pediatric_clinic`, `reproductive_perinatal_and_womens_care`, `outpatient_care_facility`, `physical_medicine_and_rehabilitation` | Specialism goes to Detailed |
| Dental | [B] `dental_clinic` | |
| Vision | [B] `vision_or_eye_care_clinic` | |
| Behavioral & Mental Health | [B] `behavioral_or_mental_health_clinic` | |
| Diagnostics & Labs | [B] `diagnostics_imaging_or_lab_service` | |
| Alternative & Complementary | [B] `complementary_and_alternative_medicine` | |
| Senior & Long-Term Care | [B] `senior_living_facility` | Check against Residential before locking |
| Veterinary | [T] `animal_or_pet_service` where primary is veterinary | Grooming and boarding go to Personal Care |
| Unspecified | [U] `health_care` (1,241), `medical_service` (321) | Largest unspecified bucket in the taxonomy |

## Education (~2,100 places)

| Sub Category | Source |
|---|---|
| Early Childhood | [B] `preschool`, `kindergarten` |
| K-12 | [B] `elementary_school`, `middle_school`, `high_school` |
| Higher Education | [B] `college_university`, `campus_building` |
| Specialty & Vocational | [B] `specialty_school` |
| Tutoring & Test Prep | [B] `tutoring_service`, `educational_service` |
| Libraries | [B] `library` |
| Research | [T] `research_institute` where non-medical |
| Administration | [B] `school_district_office` |
| Unspecified | [U] `place_of_learning` (287), `education`, `educational_facility` |

## Personal Care (~4,000 places)

Granularity problem: `personal_or_beauty_service` alone holds 2,730 places
spanning hair, nails, barber and beauty. Sub Category here must come from
`taxonomy.primary`.

| Sub Category | Source |
|---|---|
| Hair & Barber | [T] hair_salon, barber |
| Nail & Beauty | [T] nail_salon, beauty_salon, skin_care, waxing, tanning_salon |
| Spa & Massage | [B] `wellness_service` |
| Tattoo & Body Art | [T] tattoo_and_piercing |
| Laundry & Dry Cleaning | [B] `laundry_service` |
| Pet Grooming & Boarding | [T] `animal_or_pet_service` where non-veterinary |
| Other Personal Services | [B] `psychic_advising`, `astrological_advising` |

## Recreation & Fitness (~1,400 places)

| Sub Category | Source |
|---|---|
| Gyms & Fitness | [B] `gym`, `fitness_studio`, [T] `sport_or_fitness_facility` where gym-like |
| Sports Facilities | [B] `sport_court`, `sport_field`, `sports_complex`, `swimming_pool`, `skating_rink`, `golf_course`, `country_club` |
| Clubs, Leagues & Teams | [B] `sport_or_recreation_club`, `sport_league`, `sport_team` |
| Outdoor Recreation | [B] `marina`, `recreational_equipment_rental`, `skate_park` |
| Unspecified | [U] `sports_and_recreation` |

## Arts, Culture & Landmarks (~1,300 places)

| Sub Category | Source |
|---|---|
| Historic Sites & Monuments | [B] `historic_site` (923), `monument`, `fort`, `lighthouse`, `sculpture_statue` |
| Museums & Science | [B] `museum`, `planetarium`, `science_attraction` |
| Galleries | [B] `art_gallery` |
| Performing Arts | [B] `performing_arts_venue`, `theatre_venue` |
| Cultural & Creative Spaces | [B] `cultural_center`, `arts_and_crafts_space` |
| Unspecified | [U] `arts_and_entertainment` |

## Entertainment & Nightlife (~350 places)

| Sub Category | Source |
|---|---|
| Cinema | [B] `movie_theater` |
| Live Music & Comedy | [B] `music_venue`, `comedy_club` |
| Nightlife | [B] `nightlife_venue`, `dance_club`, `adult_entertainment_venue` |
| Gaming & Gambling | [B] `casino`, `gaming_venue`, `arcade` |
| Attractions & Amusement | [B] `amusement_park`, `amusement_attraction`, `zoo`, `aquarium`, `animal_attraction`, `rodeo` |
| Event & Spectator Venues | [B] `event_venue`, `festival_venue`, `fairgrounds`, `stadium_arena` |

## Parks & Nature (~600 places)

| Sub Category | Source |
|---|---|
| Parks & Public Space | [B] `park`, `public_plaza`, `public_fountain` |
| Playgrounds & Dog Parks | [B] `playground`, `dog_park` |
| Trails & Greenways | [B] `recreational_trail_or_path` |
| Gardens | [B] `garden` |
| Protected Land | [B] `national_park`, `nature_reserve` |
| Natural Features | [B] `river`, `lake`, `mountain`, `island`, `beach`, `forest`, `land_feature`, `geographic_entities` |

## Lodging (~750 places)

| Sub Category | Source |
|---|---|
| Hotels & Motels | [B] `hotel` |
| Inns & B&Bs | [B] `inn`, `bed_and_breakfast` |
| Resorts | [B] `resort` |
| Short-Term Rental | [B] `private_lodging` |
| Campgrounds & RV Parks | [B] `campground`, `rv_park` |
| Unspecified | [U] `lodging` |

## Services (~12,500 places)

Largest category. Eight sub-categories rather than the two originally discussed,
because the basic values cluster cleanly and Real Estate in particular is too
analytically central to bury.

| Sub Category | Source | Places |
|---|---|---|
| Real Estate Services | [B] `real_estate_service`, `housing_or_property_service` | ~2,220 |
| Home & Trade Services | [B] `home_service`, `building_or_construction_service` | ~3,460 |
| Business & Professional | [B] `professional_service`, `corporate_or_business_office`, `b2b_service`, `b2b_office_and_professional_service`, `b2b_science_and_technology_service`, `b2b_energy_and_utility_service`, `technical_service`, `design_service`, `printing_service`, `security_service`, `environmental_or_ecological_service`, `shopping_service` | ~2,500 |
| Legal Services | [B] `attorney_or_law_firm`, `legal_service` | ~645 |
| Financial & Insurance Services | [T] `financial_service` excluding money transfer and check cashing | ~2,000 |
| Media & Communications | [B] `media_service`, `radio_station`, `television_station`, `telecommunications_service` | ~380 |
| Rental & Event Services | [B] `rental_service`, `event_or_party_service` | ~920 |
| Travel Services | [B] `travel_service` | ~211 |

## Automotive (~3,850 places)

| Sub Category | Source |
|---|---|
| Dealers | [B] `auto_dealer`, `vehicle_dealer` |
| Repair & Maintenance | [B] `automotive_service`, `vehicle_service` |
| Parts & Accessories | [B] `vehicle_parts_store` |
| Fuel & Charging | [B] `gas_station`, `fueling_station`, `ev_charging_station` |

## Industrial & Logistics (~1,150 places)

| Sub Category | Source |
|---|---|
| Manufacturing | [B] `manufacturer`, `industrial_facility_or_service`, `b2b_industrial_and_machine_service` |
| Wholesale & Distribution | [B] `supplier_or_distributor`, `wholesaler` |
| Warehousing & Storage | [B] `storage_facility`, `b2b_transportation_and_storage_service` |
| Shipping & Delivery | [T] `shipping_or_delivery_service` excluding postal |

## Transportation (~450 places)

| Sub Category | Source |
|---|---|
| Air | [B] `airport`, `air_transport_facility_or_service` |
| Rail & Transit | [B] `train_station`, `rail_facility_or_service`, `public_transit_facility_or_service`, `park_and_ride` |
| Parking | [B] `parking`, `parking_garage`, `parking_lot` |
| Ground Transport Services | [B] `taxi_or_ride_share_service` |
| Road Infrastructure | [B] `bridge`, `toll_station` |
| Unspecified | [U] `travel_and_transportation` |

## Government & Public Safety (~1,200 places)

| Sub Category | Source |
|---|---|
| Government Offices | [B] `government_office`, `government_department`, `embassy` |
| Public Safety | [B] `police_station`, `fire_station`, `public_safety_service` |
| Courts & Corrections | [B] `courthouse`, `jail_or_prison` |
| Military | [B] `military_base`, `military_site` |
| Postal | [T] `shipping_or_delivery_service` where postal |
| Unspecified | [U] `community_and_government` |

## Community & Civic (~1,800 places)

| Sub Category | Source |
|---|---|
| Civic & Nonprofit Organizations | [B] `civic_organization`, `social_or_community_service` |
| Community Centers | [B] `community_center` |
| Youth & Family Services | [B] `youth_organization`, [T] `family_service` where non-clinical |
| Food Assistance | [B] `food_bank` |
| Labor & Political | [B] `labor_union`, `political_organization` |
| Social Clubs | [B] `social_club` |
| Cemeteries | [B] `cemetery` |

## Religious Institutions (~2,460 places)

Sub Category maps one-to-one onto basic values. Denomination (Baptist, Catholic,
Methodist) belongs at Detailed Category.

| Sub Category | Source |
|---|---|
| Christian | [B] `christian_place_of_worship` |
| Jewish | [B] `jewish_place_of_worship` |
| Muslim | [B] `muslim_place_of_worship` |
| Buddhist | [B] `buddhist_place_of_worship` |
| Hindu | [B] `hindu_place_of_worship` |
| Other & Unspecified | [U] `place_of_worship`, `religious_organization` |

## Financial Institutions (~1,700 places)

| Sub Category | Source |
|---|---|
| Banks & Credit Unions | [B] `bank_or_credit_union` |
| ATMs | [B] `atm` |
| Money Services | [T] `financial_service` where money transfer or check cashing |

## Utilities (~175 places)

| Sub Category | Source |
|---|---|
| Electric | [B] `electric_utility_provider` |
| Water | [B] `water_utility_provider` |
| Natural Gas | [B] `natural_gas_utility_provider` |
| Unspecified | [U] `public_utility` |

## Residential (~175 places)

| Sub Category | Source |
|---|---|
| Apartments | [B] `apartment` |
| Condominiums | [B] `condominium` |

## Agriculture (~360 places)

| Sub Category | Source |
|---|---|
| Farms | [B] `farm` |
| Agricultural Services | [B] `agricultural_service` |

## Unclassified (~2,100 places)

Null source values plus anything that fails both basic and taxonomy lookup.
Currently 2,054 places on a null/null pair. Re-profile after the September
Overture release, since null legacy `categories` does not imply null
`basic_category`.

---

## Cross-cutting rules

1. Every Category gets an **Unspecified** sub-category where the source has a
   category-level value with no finer detail. Do not force these into a real
   sub-category, and do not drop them. They are a coverage metric.
2. Sub Category is where the daily-needs basket is defined (Grocery, Convenience,
   Pharmacy, Primary & General Care, K-12, Parks & Public Space, Banks & Credit
   Unions). Any change to these names is a breaking change for Q4.
3. Cuisine, denomination, medical specialism, and trade type all belong at
   Detailed Category, never at Sub Category.
4. Sub Category names must be unique across the whole taxonomy so a
   fully-qualified path is not required to disambiguate.

## Open questions

- **Galleries**: currently split in spirit between commercial (Retail) and
  institutional (Arts). Basic cannot distinguish. Draft puts all in Arts.
- **Stadium & arena**: Entertainment (spectator) or Recreation (participation)?
  Draft says Entertainment.
- **Senior living**: Healthcare or Residential?
- **Cemeteries**: Community & Civic or Parks & Nature? Draft says Community.
- **Social clubs**: Community & Civic or Recreation? Draft says Community.
- **Services depth**: eight sub-categories may be too many if Detailed Category
  ends up thin under Legal, Media, and Travel.