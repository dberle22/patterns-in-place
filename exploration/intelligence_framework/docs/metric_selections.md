# Metric Selections

## Character Memo

This memo translates the latest Character notebook run into a cleaner selection document for Phase 1. It is based on `exploration/intelligence_framework/phase_variable_selection/character_variable_selection.qmd` and its rendered output `exploration/intelligence_framework/phase_variable_selection/character_variable_selection.html`.

### Frame Read

- Universe: `401` CBSAs with `pop_total >= 100000`
- Complete Character coverage: `382` CBSAs
- Subject read:
  - `Demographics` is a strong Character subject with average topic coverage of `99.8%`
  - `Social Fabric` is useful but uneven with average topic coverage of `98.4%`
- Topic dimensionality:
  - `Race & ethnicity`: `4` components to explain `80%` of within-topic variance
  - `Residential stability`: `4` components
  - `Social capital`: `3` components
  - `Educational attainment`, `Nativity & citizenship`, `Population density`, and `Nonprofits & civic organizations`: `1` dominant component each
- Overall Character dimensionality: `9` components explain at least `80%` of the variance in the surviving Character set
- Cross-topic leader check:
  - only `1` cross-topic pair exceeded the `|r| = 0.75` review threshold
  - `pct_hispanic` vs `pct_non_citizen`: `r = 0.79`
  - in the broader pairwise CBSA comparison, `pct_hispanic` is less correlated with `pct_foreign_born` (`r = 0.564`) than with `pct_non_citizen` (`r = 0.612`)

### Recommended Core Character Set

- `diversity_index`
- `pct_black_nh`
- `pct_asian_nh`
- `pct_hispanic`
- `pct_age_over_64`
- `pct_ba_plus`
- `pct_foreign_born`
- `pop_weighted_density_sqmi`
- `friending_bias`
- `civic_engagement_volunteering_rate`
- `civic_organizations_per_1000`
- `nonprofits_per_100k`
- `irs_net_migration_rate`
- `pct_moved_diff_st`
- `pct_moved_abroad`
- `social_associations_per_10k`
- `pct_struct_multifam`

### Subject Decisions

#### Demographics

**Subject decision:** Keep

**Why keep it**
- It is the strongest Character subject in the notebook on both coverage and stability.
- Average topic coverage is `99.8%`.
- Several topics inside Demographics remain active after screening rather than collapsing into one general “population profile” story.

**Contrarian take**
- Demographics can easily dominate clustering if we carry too many composition metrics at once.
- The real task is not deciding whether to keep Demographics, but keeping it from swallowing the rest of Character.

##### Race & ethnicity

**Topic decision:** Keep

**Why keep it**
- `7` race / ethnicity metrics survive the variance screen.
- The topic needs `4` components to explain `80%` of within-topic variance, so it is genuinely multi-dimensional.
- The main redundancy is concentrated in only part of the family:
  - `pct_hispanic` vs `pct_white_nh`: `r = -0.75`
  - `pct_hispanic` also overlaps with the sharper nativity alternative, but the broader pairwise read is cleaner for `pct_foreign_born` than for `pct_non_citizen`

**KPI read**
- Recommended core KPIs:
  - `diversity_index`
  - `pct_black_nh`
  - `pct_asian_nh`
  - `pct_hispanic`
- Sensitivity / optional KPIs:
  - `pct_aian_nh`
  - `pct_nhpi_nh`
- KPIs to avoid in default set:
  - `pct_white_nh`, because it is the most clearly redundant large-share counterpart once `pct_hispanic` and `diversity_index` are already present

**Contrarian take**
- The notebook’s raw CV ordering favors `pct_aian_nh` and `pct_nhpi_nh`, which means small-share groups may still be doing real differentiating work.
- A tighter core improves stability, but it may also smooth away smaller-population identities that actually matter for Character.
- Also, because `pct_hispanic` is the only race KPI that materially overlaps with another topic leader, there is a reasonable case for watching whether it is doing double duty as both composition and immigration signal.

##### Age structure

**Topic decision:** Keep, but as a one-KPI topic

**Why keep it**
- The topic still belongs conceptually in Character.
- `pct_age_over_64` survives the variance screen and acts as the only active age KPI at this grain.

**KPI read**
- Recommended core KPI:
  - `pct_age_over_64`
- KPIs to drop from default clustering:
  - `median_age`
  - `pct_age_under_18`
  - `pct_age_18_64`

**Data behind the call**
- Topic PCA shows only `1` surviving metric for age structure.
- The other three age metrics fall below the `CV = 0.2` threshold.

**Contrarian take**
- Low variance does not mean low importance. Age still affects household formation, labor force shape, and service demand.
- It may deserve to stay as a descriptive overlay even if it is not strong enough to justify multiple clustering slots.

##### Educational attainment

**Topic decision:** Keep, but consolidate hard

**Why keep it**
- All four education KPIs survive the variance screen.
- The topic clearly matters, but it behaves like one dominant underlying dimension rather than multiple independent stories.

**KPI read**
- Recommended core KPI:
  - `pct_ba_plus`
- Strong alternative:
  - `pct_grad_plus`
- KPIs to avoid carrying together in the default set:
  - `pct_grad_plus`
  - `pct_ba_plus`
  - `pct_ba`
  - `pct_hs_or_less`

**Data behind the call**
- Topic dimensionality is `1`.
- Correlations are extremely high:
  - `pct_grad_plus` vs `pct_ba_plus`: `r = 0.95`
  - `pct_ba_plus` vs `pct_ba`: `r = 0.95`
  - `pct_ba` vs `pct_hs_or_less`: `r = -0.90`

**Contrarian take**
- `pct_grad_plus` is still the statistically stronger differentiator in the notebook.
- We are choosing `pct_ba_plus` because it is easier to explain and more intuitively captures broad educational attainment, but that does trade away some statistical sharpness.

##### Nativity & citizenship

**Topic decision:** Keep, but consolidate to one lead KPI

**Why keep it**
- The topic survives cleanly and clearly differentiates metros.
- It is substantively distinct from race alone even though some overlap exists.

**KPI read**
- Recommended core KPI:
  - `pct_foreign_born`
- Strong alternative:
  - `pct_non_citizen`

**Data behind the call**
- Topic dimensionality is `1`.
- `pct_non_citizen` vs `pct_foreign_born`: `r = 0.96`
- In the cross-topic leader check, `pct_non_citizen` vs `pct_hispanic`: `r = 0.79`
- In the broader pairwise CBSA comparison:
  - `pct_hispanic` vs `pct_foreign_born`: `r = 0.564`
  - `pct_hispanic` vs `pct_non_citizen`: `r = 0.612`

**Contrarian take**
- `pct_non_citizen` is still the sharper differentiator and may better capture places shaped by more recent or institutionally unsettled immigration.
- We are choosing `pct_foreign_born` because it is cleaner relative to the Hispanic-composition signal and easier to defend as a distinct Character KPI.

##### Population density

**Topic decision:** Keep, but use one density KPI by default

**Why keep it**
- Density is a central Character signal and clearly differentiates metros.
- But the topic acts like one dominant dimension rather than two independent ones.

**KPI read**
- Recommended core KPI:
  - `pop_weighted_density_sqmi`
- Strong alternative:
  - `gross_density_sqmi`

**Data behind the call**
- Topic dimensionality is `1`.
- `gross_density_sqmi` vs `pop_weighted_density_sqmi`: `r = 0.77`
- The metric map already notes that `pop_weighted_density_sqmi` is the more lived-density interpretation.

**Contrarian take**
- `gross_density_sqmi` ranked more strongly on variance in the notebook.
- If the goal is to capture metro form rather than resident-experienced density, `gross_density_sqmi` may actually separate places more cleanly.

#### Social Fabric

**Subject decision:** Keep

**Why keep it**
- Social Fabric is not just filler around Demographics. Several topics remain active after screening.
- The strongest live topics are `Social capital`, `Residential stability`, and `Nonprofits & civic organizations`.

**Contrarian take**
- Social Fabric is less even than Demographics, and some parts of it are really thin at CBSA scale.
- That means we need to be more selective here and avoid treating every socially themed KPI as equally important.

##### Social capital

**Topic decision:** Keep

**Why keep it**
- This is one of the clearest non-demographic Character topics.
- It survives with enough breadth and enough structure to justify multiple KPIs rather than a single proxy.

**KPI read**
- Recommended core KPIs:
  - `friending_bias`
  - `civic_engagement_volunteering_rate`
  - `civic_organizations_per_1000`
- Strong sensitivity KPI:
  - `childhood_friending_bias`
- KPIs to drop from default clustering:
  - `economic_connectedness`
  - `childhood_economic_connectedness`
  - `cohesion_clustering`
  - `cohesion_support_ratio`

**Data behind the call**
- `390` complete rows for topic PCA
- `4` KPIs survive the variance screen
- Topic needs `3` components to explain `80%` of topic variance
- The dropped KPIs fall into the low-variance bucket at CBSA scale

**Contrarian take**
- `childhood_friending_bias` was the top KPI in the notebook scorecard.
- Excluding it from the default core may make the topic feel more present-tense and less structurally inherited than the data actually suggests.

##### Nonprofits & civic organizations

**Topic decision:** Keep, but collapse to one KPI

**Why keep it**
- The topic survives clearly, but the two KPIs are effectively the same signal at this grain.

**KPI read**
- Recommended core KPI:
  - `nonprofits_per_100k`
- Strong alternative:
  - `nonprofits_total_per_100k`

**Data behind the call**
- Topic dimensionality is `1`
- `nonprofits_per_100k` vs `nonprofits_total_per_100k`: `r = 0.99`

**Contrarian take**
- `nonprofits_total_per_100k` may be the better measure if we want total associational density rather than a narrower nonreligious or more curated civic measure.

##### Residential stability

**Topic decision:** Keep

**Why keep it**
- This is one of the richest Character topics in the notebook.
- It captures migration churn and movement-origin structure rather than just one generic mobility story.

**KPI read**
- Recommended core KPIs:
  - `irs_net_migration_rate`
  - `pct_moved_diff_st`
  - `pct_moved_abroad`
- Strong sensitivity KPIs:
  - `pct_moved_same_cnty`
  - `mobility_rate`
- KPIs moved out of Character:
  - `irs_inflow_agi`
  - `irs_outflow_agi`
  - `irs_net_agi`
- KPIs to avoid carrying together indiscriminately inside Character:
  - `irs_net_migration`
  - `pct_moved_same_cnty`
  - `mobility_rate`

**Data behind the call**
- `10` metrics survive the variance screen
- `396` complete rows for topic PCA
- Topic needs `4` components to explain `80%` of topic variance
- Strong within-topic redundancies:
  - `irs_inflow_agi` vs `irs_outflow_agi`: `r = 0.89`
  - `irs_net_migration` vs `irs_net_agi`: `r = 0.87`
  - `pct_moved_same_cnty` vs `mobility_rate`: `r = 0.76`
- We are treating the AGI-flow variables as a better conceptual fit for `Opportunity` than for `Character`, even though they were active in the original notebook.

**Contrarian take**
- Even this trimmed core may be too compressed.
- The topic’s structure suggests a case for splitting it into migration-churn and migration-origin subtopics inside Character, while letting wealth-flow live elsewhere.

##### Household structure

**Topic decision:** Drop from default clustering set

**Why drop it**
- It is the only fully inactive topic in the current Character notebook.

**KPI read**
- KPIs to drop from default clustering:
  - `pct_hh_single_person`
  - `pct_family_single_parent`

**Data behind the call**
- `0` KPIs in this topic survive the variance screen
- Both variables have broad coverage but low cross-metro differentiation

**Contrarian take**
- Household structure can still matter culturally and socially even when it does not differentiate enough for clustering.
- It may be better handled as a narrative overlay than as a formal Character axis.

##### Social associations

**Topic decision:** Keep

**Why keep it**
- It survives cleanly and adds an institutional-density angle that is not identical to the social-network measures.

**KPI read**
- Recommended core KPI:
  - `social_associations_per_10k`

**Data behind the call**
- `396` complete rows for topic PCA
- Single-KPI topic that survives the variance screen

**Contrarian take**
- Because it is a singleton topic, it may behave more like a supplemental proxy for civic density than a distinct Character dimension once nonprofit density and civic organizations are already in the frame.

##### Safety proxy

**Topic decision:** Move out of Character

**Why move it**
- `homicide_rate` works as a live proxy, but it fits Livability more naturally than Character.
- Safety reads more like a lived-condition topic than a civic-identity topic in this framework.

**KPI read**
- Moved out of the Character cluster model:
  - `homicide_rate`
- Still acceptable as descriptive context if needed.

**Data behind the call**
- `387` complete rows for topic PCA
- Survives the variance screen
- The move is being made on conceptual grounds, not because the metric failed statistically

**Contrarian take**
- One could argue that extreme violence does shape metro character and social trust.
- We are moving it because conceptual fit matters more here than squeezing every surviving KPI into the Character frame.

##### Built form

**Topic decision:** Keep, but as a one-KPI topic

**Why keep it**
- Built form matters, but only one KPI is really active at CBSA scale in the current run.

**KPI read**
- Recommended core KPI:
  - `pct_struct_multifam`
- KPI to drop from default clustering:
  - `owner_occ_rate`

**Data behind the call**
- `pct_struct_multifam` survives the variance screen
- `owner_occ_rate` falls below `CV = 0.2`
- Topic PCA shows only `1` active metric

**Contrarian take**
- `owner_occ_rate` may still capture a real owner-dominant vs renter-heavy metro divide even if it is too low-variance to earn a core clustering slot.

### Working Interpretation

- Character is not just a demographic-composition frame. Social Fabric contributes real signal, especially through `Social capital`, `Residential stability`, and `Nonprofits & civic organizations`.
- The main modeling risk is overcounting within-topic redundancy, not under-populating the Character frame.
- We are explicitly moving `Safety` and IRS wealth-flow measures out of Character on conceptual grounds even though they show live signal in the notebook.
- The cross-topic leader pass came back relatively clean. Only one pair crossed the review threshold: `pct_hispanic` and `pct_non_citizen` (`r = 0.79`).
- That result pushes the default nativity choice toward `pct_foreign_born`, with `pct_non_citizen` retained as the sharper sensitivity-test alternative.
- The cleanest Phase 1 approach is:
  - keep most topics
  - collapse single-dimension topics to one lead KPI
  - allow multi-KPI treatment only where the notebook clearly shows real topic dimensionality
  - use the cross-topic check mainly as a guardrail around race / nativity overlap, not as a reason to keep pruning the whole frame

### Next Move

- Use the core set above as the default Character bundle for Phase 2 clustering.
- Run one sensitivity bundle with the strongest remaining contrarian alternatives:
  - `gross_density_sqmi` instead of `pop_weighted_density_sqmi`
  - `pct_non_citizen` instead of `pct_foreign_born`
  - `childhood_friending_bias` added to the Social Capital core
  - `nonprofits_total_per_100k` instead of `nonprofits_per_100k`

## Livability Memo

This memo translates `exploration/intelligence_framework/phase_variable_selection/livability_variable_selection.qmd` and its rendered HTML into a cleaner Phase 1 selection read for Livability.

### Frame Read

- Universe: `401` CBSAs with `pop_total >= 100000`
- Strong recurring source families:
  - `ACS affordability`, `ACS transport`, `ACS broadband`, `ACS housing`, and `BPS permits` all cover essentially the full CBSA universe
  - `CHR health` remains broad but not universal
- Partial or baseline-only families:
  - `RPP-adjusted income`: `352 / 401`
  - `EPA AQI`: `345 / 401`
  - `EPA EJScreen`: `329 / 401`
  - `FEMA NRI`: `333 / 401`
  - `EPA SLD`: `395 / 401`, but `2021` only
  - `USDA food access`: `390 / 401`, but `2019` only
- Subject decisions from the notebook:
  - `Affordability`: keep
  - `Health & Safety`: keep
  - `Access & Infrastructure`: keep
  - `Education access`: drop from the Phase 1 core
  - `Physical Environment`: keep in Livability, but with coverage caution
- Overall Livability dimensionality: `14` components explain `80%` of the variance in the surviving set, so the frame is still broad even after pruning.
- Cross-topic correlation read:
  - `value_to_income` vs `pct_rent_burden_30plus`: `r = 0.47`
  - `value_to_income` vs `pov_rate`: `r = -0.16`
  - `pct_rent_burden_30plus` vs `pov_rate`: `r = 0.12`
  - `pop_weighted_density_sqmi` vs `vacancy_rate`: `r = -0.30`
  - `pop_weighted_density_sqmi` vs `pct_struct_small_mf`: `r = 0.28`
  - `walkability_index` vs `pop_weighted_density_sqmi`: `r = 0.65`
  - `firearm_fatality_rate` vs `premature_death_rate`: `r = 0.74`
  - `motor_vehicle_crash_rate` vs `premature_death_rate`: `r = 0.79`

### KPI Count By Subject

- `Affordability`
  - `8` recurring core KPIs
- `Health & Safety`
  - `7` recurring core KPIs
- `Access & Infrastructure`
  - `5` recurring core KPIs
  - `4` supplemental baseline / proxy KPIs
- `Physical Environment`
  - `2` supplemental coverage-caution KPIs
- `Education access`
  - `0` KPIs in the initial model

### Recommended Phase 1 Livability Set

#### Recurring core

- `value_to_income`
- `pct_rent_burden_30plus`
- `pov_rate`
- `permits_per_1000_housing_units`
- `permits_share_units_5_plus`
- `pct_struct_mobile`
- `pct_struct_small_mf`
- `pct_struct_mid_mf`
- `premature_death_rate`
- `mental_health_provider_ratio`
- `drug_overdose_death_rate`
- `pct_uninsured_adults`
- `preventable_hospital_stay_rate`
- `firearm_fatality_rate`
- `motor_vehicle_crash_rate`
- `pct_commute_walk`
- `pct_commute_wfh`
- `vacancy_rate`
- `pct_hh_0_vehicles`
- `pct_no_internet_access`

#### Keep in frame, but baseline / coverage-caution / proxy

- `walkability_index`
- `jobs_access_45min_transit`
- `pct_population_low_income_low_access_1_10`
- `pop_weighted_density_sqmi`
- `unhealthy_days`
- `fema_risk_score`

### Weighting Design

The cleanest way to avoid overweighting a subject is hierarchical weighting:

1. Standardize each KPI to a z-score.
2. Average KPIs into a topic score.
3. Average topic scores into a subject score.
4. Average subject scores into the final Livability score or clustering input.

That means more KPIs inside a subject do not automatically give that subject more influence.

#### Subject weights

For the first Livability model, use four active subjects with equal top-line weight:

- `Affordability = 0.25`
- `Health & Safety = 0.25`
- `Access & Infrastructure = 0.25`
- `Physical Environment = 0.25`

`Education access` stays out of the initial model.

#### Topic weights within subject

Weight topics inside each subject by:

`raw_topic_weight = coverage_share * reliability_factor`

Use these reliability factors:

- recurring core topics: `1.00`
- supplemental baseline topics: `0.75`
- supplemental coverage-caution topics: `0.60`

Then normalize within each subject:

`topic_weight_within_subject = raw_topic_weight / sum(raw_topic_weight within subject)`

And apply the equal subject weight:

`final_topic_weight = subject_weight_equal * topic_weight_within_subject`

#### KPI weights within topic

Use simple within-topic weights:

- one-KPI topics: the lead KPI gets all topic weight
- multi-KPI recurring topics: split topic weight equally across the selected core KPIs
- supplemental baseline / caution topics: split equally across the selected supplemental KPIs

So the concrete KPI formula is:

`final_kpi_weight = final_topic_weight / number_of_selected_kpis_in_topic`

#### Why this is the right default

- It prevents `Affordability` from dominating just because it has the deepest KPI bench.
- It lets us keep `Health & Safety` consolidated as one subject while still preserving distinct topics inside it.
- It keeps the supplemental baseline KPIs in frame without letting one-time sources overpower recurring series.
- It is simple enough to explain and audit before we get fancier with calibration.

### Subject Decisions

#### Affordability

**Subject decision:** Keep

**Why keep it**
- This is still the deepest recurring Livability subject.
- Average topic coverage is `99.0%`.
- The cross-topic correlation pass shows that the main affordability topics are related but not redundant enough to collapse automatically.

**Contrarian take**
- Affordability is still the subject most likely to overwhelm the rest of Livability if we treat every housing KPI like a separate concept.
- The subject belongs, but it has to be deliberately compressed.

##### Price pressure

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage is `95.9%`.
- It is a clean lead topic and the strongest price-pressure KPI is still the ownership-side measure.

**KPI read**
- Recommended core KPI:
  - `value_to_income`
- Descriptive / sensitivity KPIs:
  - `rent_to_income`
  - `rpp_real_pc_income`

**Data behind the call**
- `value_to_income` vs `pct_rent_burden_30plus` is only `r = 0.47`, so Price Pressure and Housing Burden are related but not the same topic.
- `rpp_real_pc_income` is useful context, but only covers `352 / 401` CBSAs.

**Contrarian take**
- `rent_to_income` may still be the better lived-experience metric if we want a renter-first read of Livability.
- The notebook keeps it descriptive because home values are the stronger differentiator in the current pass.

##### Housing burden

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage is `99.1%`.
- This is the clean renter-stress companion to Price Pressure and deserves its own slot.

**KPI read**
- Recommended core KPI:
  - `pct_rent_burden_30plus`
- Descriptive / baseline KPIs:
  - `pct_cost_burdened`
  - `pct_severely_cost_burdened`
  - `pct_renter_severely_cost_burdened`
- KPI to drop from the default set:
  - `pct_rent_burden_50plus`

**Data behind the call**
- Topic PCA still says this is mostly one dominant KPI story.
- The recurring rent-burden line is the right default anchor, while CHAS remains contextual.

**Contrarian take**
- CHAS severe-burden fields may tell the sharper distress story.
- They stay in the descriptive bundle even if they do not lead the model.

##### Poverty context

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage is `100.0%`.
- Poverty adds real household-stress context without collapsing into the housing-price topics.

**KPI read**
- Recommended core KPI:
  - `pov_rate`

**Data behind the call**
- `pov_rate` is only weakly correlated with `value_to_income` and `pct_rent_burden_30plus`, so it is not obviously duplicating the rest of Affordability.

**Contrarian take**
- Poverty can read like a distress or opportunity topic as much as a Livability topic.
- It stays because Affordability needs a basic stress-context field.

##### Housing supply

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `100.0%`.
- The permit family still needs `2` components to explain most of its variance, so the topic is not fake even if the KPIs overlap.

**KPI read**
- Recommended core KPIs:
  - `permits_per_1000_housing_units`
  - `permits_share_units_5_plus`
- Descriptive / sensitivity KPI:
  - `permits_avg_units_per_bldg`
- Redundant KPIs:
  - `permits_per_1000_population`
  - `permits_share_multifam_units`

**Data behind the call**
- `permits_per_1000_housing_units` vs `permits_share_units_5_plus` is only `r = 0.10`, so the topic naturally splits between scale-of-supply and density-of-supply.
- `permits_per_1000_housing_units` vs `pct_struct_small_mf` is only `r = -0.27`, which supports keeping Housing Supply separate from Housing Structure Mix.

**Contrarian take**
- The whole permit family is easy to over-interpret as a solved “future supply” story.
- Keeping just two core KPIs is the safest version of the topic.

##### Housing structure mix

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `100.0%`.
- The topic remains genuinely multi-dimensional after screening.

**KPI read**
- Recommended core KPIs:
  - `pct_struct_mobile`
  - `pct_struct_small_mf`
  - `pct_struct_mid_mf`
- Descriptive KPIs:
  - `pct_struct_large_mf`
  - `pct_struct_multifam`
- KPI to drop from the default set:
  - `pct_struct_sf_det`

**Data behind the call**
- This topic survives because the notebook goes deeper than the basic single-family vs. multifamily split.
- The built-form proxy correlations are only moderate, so this topic is not just duplicating density.

**Contrarian take**
- `pct_struct_multifam` is still the simplest version and may be enough if we later need a lighter-weight model.
- The richer structure mix is more defensible analytically, but less simple to explain.

#### Health & Safety

**Subject decision:** Keep

**Why keep it**
- Health and Safety work better as one consolidated Livability subject than as two separate subject votes.
- Average topic coverage is `98.0%`.
- The cross-topic correlation pass shows the injury and violence KPIs sitting close to the main health-outcome line, but still distinct enough to justify their own topic family inside the subject.

**Contrarian take**
- This subject can drift toward a generalized distress frame if we only keep downside metrics.
- The subject belongs, but we should keep some descriptive non-core metrics visible so the frame does not collapse into mortality-plus-hardship.

##### Health outcomes

**Topic decision:** Collapse to one lead KPI

**Why keep it**
- Topic coverage is `97.6%`.
- The topic behaves like one dominant dimension in the PCA read.

**KPI read**
- Recommended core KPI:
  - `premature_death_rate`
- Descriptive / sensitivity KPIs:
  - `child_mortality_rate`
  - `life_expectancy`
- KPI to drop from the default set:
  - `infant_mortality_rate`

**Data behind the call**
- `premature_death_rate` is the main outcome KPI for the model.
- `child_mortality_rate` and `life_expectancy` are better kept descriptive than treated as additional equal-weight model inputs.

**Contrarian take**
- `life_expectancy` is still the most intuitive public-facing health KPI.
- It may be the right narrative lead even if it is not the best model KPI.

##### Health behavior and access

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `98.3%`.
- Many KPIs still clear the variance screen and the topic remains genuinely multi-dimensional.

**KPI read**
- Recommended core KPIs:
  - `mental_health_provider_ratio`
  - `drug_overdose_death_rate`
  - `pct_uninsured_adults`
  - `preventable_hospital_stay_rate`
- Descriptive / sensitivity KPIs:
  - `primary_care_ratio`
  - `child_care_cost_burden_rate`
  - `physical_inactivity`
  - `adult_obesity`
  - `poor_mental_health_days`
  - `food_insecurity_rate`

**Data behind the call**
- The strongest surviving model KPIs are access, acute harm, and system-strain metrics.
- The lifestyle metrics remain useful, but they fit better as descriptive context than as core model inputs in this pass.

**Contrarian take**
- Lifestyle metrics may matter more for “can you live well here?” than some of the narrower system-failure measures.
- If we later want a more positive-health read, this is the first topic to rebalance.

##### Violence and injury

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- The topic still needs `2` components to explain most of its variance.
- It is not just a one-metric safety placeholder anymore.

**KPI read**
- Recommended core KPIs:
  - `firearm_fatality_rate`
  - `motor_vehicle_crash_rate`
- Sensitivity KPI:
  - `homicide_rate`

**Data behind the call**
- `firearm_fatality_rate` vs `premature_death_rate`: `r = 0.74`
- `motor_vehicle_crash_rate` vs `premature_death_rate`: `r = 0.79`
- `homicide_rate` stays useful, but it is the narrowest of the three.

**Contrarian take**
- `homicide_rate` is still the clearest public violence KPI.
- If the product wants a sharper crime-adjacent read, homicide may deserve more narrative weight than model weight.

#### Access & Infrastructure

**Subject decision:** Keep

**Why keep it**
- Average topic coverage is `99.2%`.
- This subject now has a cleaner internal structure: recurring daily-life topics, baseline access topics, and one explicit built-form proxy.

**Contrarian take**
- This is still the messiest subject in the frame.
- The right answer is not to shrink it away, but to separate the recurring topics from the baseline topics clearly.

##### Commute and mode access

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `100.0%`.
- The topic remains multi-dimensional in the notebook.

**KPI read**
- Recommended core KPIs:
  - `pct_commute_walk`
  - `pct_commute_wfh`
- Sensitivity KPI:
  - `pct_commute_transit`
- Descriptive KPI:
  - `mean_travel_time`

**Data behind the call**
- The surviving model read is more about mode structure than simple commute burden.
- Transit is better treated as an alternate sensitivity metric than as a guaranteed core KPI everywhere.

**Contrarian take**
- `mean_travel_time` is still the easiest daily-friction metric for general readers to understand.
- It may deserve narrative use even if it stays out of the model core.

##### Vehicle access

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage is `100.0%`.
- Splitting this from vacancy makes the topic structure cleaner.

**KPI read**
- Recommended core KPI:
  - `pct_hh_0_vehicles`

**Data behind the call**
- This is now a single clean access dependency topic rather than a mixed access/housing bucket.

**Contrarian take**
- Zero-vehicle households can read as either a transit-positive or transit-need signal depending on the metro.
- It is analytically useful, but narratively ambiguous.

##### Housing slack

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage is `100.0%`.
- Splitting it out makes the Access section cleaner and avoids forcing it into the vehicle story.

**KPI read**
- Recommended core KPI:
  - `vacancy_rate`

**Data behind the call**
- Built form is only moderately related to vacancy: `r = -0.30`.
- That supports keeping vacancy as its own topic rather than absorbing it into density or structure mix.

**Contrarian take**
- `vacancy_rate` could also live under Affordability or Housing.
- It stays here because market slack affects day-to-day access and optionality directly.

##### Digital access

**Topic decision:** Collapse to one lead KPI

**Why keep it**
- Topic coverage is `100.0%`.
- The mirror pair still behaves like one basic exclusion story.

**KPI read**
- Recommended core KPI:
  - `pct_no_internet_access`
- Descriptive KPI:
  - `pct_broadband_subscription`

**Data behind the call**
- The no-access version remains the sharper differentiator.

**Contrarian take**
- The broadband-subscription framing may communicate better to external readers even if it is weaker analytically.

##### Walkability and transit baseline

**Topic decision:** Keep as a baseline topic

**Why keep it**
- Topic coverage is `98.5%`.
- Even as a one-time `2021` baseline, this is too conceptually central to Livability to defer.

**KPI read**
- Recommended baseline KPIs:
  - `walkability_index`
  - `jobs_access_45min_transit`
- Descriptive KPIs:
  - `transit_service_density`
  - `jobs_access_45min_auto`

**Data behind the call**
- `walkability_index` vs `pop_weighted_density_sqmi` is `r = 0.65`, so Walkability overlaps with Built Form but is not redundant with it.
- That supports keeping the topic visible as its own baseline access lens.

**Contrarian take**
- Because the source is one-time, it may still prove too sticky or lagged for some modeling uses.
- But conceptually it belongs in the frame.

##### Food access baseline

**Topic decision:** Keep as a baseline topic

**Why keep it**
- Topic coverage is `97.3%`.
- Food access is a direct daily-life topic and the 2019 baseline is still useful enough to keep.

**KPI read**
- Recommended baseline KPI:
  - `pct_population_low_income_low_access_1_10`
- Descriptive KPI:
  - `pct_population_low_access_1_10`

**Data behind the call**
- `pct_population_low_income_low_access_1_10` vs `pct_no_internet_access` is only `r = 0.35`, so this topic is not just rephrasing digital exclusion or poverty.

**Contrarian take**
- The source vintage is still a real limitation.
- If USDA updates the Atlas, this topic should be revisited quickly.

##### Built-form proxy

**Topic decision:** Keep as a proxy topic

**Why keep it**
- Topic coverage is `98.8%`.
- This is still a useful access-intensity proxy even if it is not a first-class Livability family.

**KPI read**
- Recommended proxy KPI:
  - `pop_weighted_density_sqmi`
- Descriptive proxy:
  - `gross_density_sqmi`

**Data behind the call**
- Density is only moderately related to vacancy and structure mix, so it is not obviously duplicating those topics.

**Contrarian take**
- Density may matter more for Livability than the “proxy” label implies.
- It stays labeled as a proxy because its primary conceptual home is still Character / Built Form.

#### Education access

**Subject decision:** Drop from the Phase 1 core

**Why drop it**
- The live CHR education set still produces `0` high-variance KPIs in this pass.
- The broader K-12 quality topic remains deferred until better data lands.

**Contrarian take**
- Education is clearly important substantively.
- The current result says the live proxy set is weak, not that the subject is unimportant.

##### School performance

**Topic decision:** Drop

**Why drop it**
- Coverage is acceptable but the topic does not survive the variance screen.

**KPI read**
- Best descriptive KPI:
  - `math_score_index`
- Other current-topic KPIs to avoid in the default set:
  - `reading_score_index`
  - `hs_graduation_rate`

**Data behind the call**
- Topic coverage: `90.9%`
- High-variance metrics: `0`

**Contrarian take**
- If we need one public-facing education metric while SEDA is still deferred, `hs_graduation_rate` is probably the cleanest narrative fallback.

#### Physical Environment

**Subject decision:** Keep in Livability, but with coverage caution

**Why keep it**
- This is too interesting a line of thinking to drop just because coverage is weaker.
- The notebook still shows real structure inside Air Pollution and Climate Hazard Risk.

**Contrarian take**
- Coverage is still the main risk here, so these topics should be weighted carefully until the environment family thickens.

##### Air pollution

**Topic decision:** Keep with coverage caution

**Why keep it**
- Topic coverage is `86.0%`.
- The topic is genuinely multi-dimensional and not just a weak placeholder.

**KPI read**
- Recommended coverage-caution KPI:
  - `unhealthy_days`
- Strong sensitivity KPIs:
  - `ejs_diesel_pm`
  - `air_pollution_pm25`
- Descriptive / redundant KPIs:
  - `aqi_median`
  - `aqi_p90`
  - `ejs_pm25`
- KPI to drop first:
  - `ejs_ozone`

**Data behind the call**
- This topic survives because it adds a distinct environmental-exposure read, not because it has perfect coverage.

**Contrarian take**
- We may still be underweighting Air Pollution by treating it as a caution topic instead of a default core family.
- It is one of the strongest candidates for promotion once coverage improves.

##### Climate hazard risk

**Topic decision:** Keep with coverage caution

**Why keep it**
- Topic coverage is `88.0%`.
- Even with thinner coverage, it is a distinct and important Livability topic.

**KPI read**
- Recommended coverage-caution KPI:
  - `fema_risk_score`
- Descriptive / proxy KPI:
  - `adverse_climate_events`

**Data behind the call**
- The notebook keeps the topic because the concept matters and the direct-source family is now live enough to stay visible.

**Contrarian take**
- The CHR proxy may be easier to interpret right now than the FEMA composite.
- But the long-run aim should still be to move toward the direct hazard-risk family.

##### Hazard exposure

**Topic decision:** Sensitivity-only topic

**Why keep it as sensitivity**
- Topic coverage is `83.0%`.
- The topic is promising, but still too partial to treat as a default part of the Phase 1 set.

**KPI read**
- Best sensitivity KPI:
  - `ejs_wastewater_discharge`
- Other useful sensitivity KPIs:
  - `ejs_superfund_proximity`
  - `ejs_drinking_water_noncompliance`

**Data behind the call**
- `5` KPIs clear the variance threshold, but the family is still coverage-constrained.

**Contrarian take**
- Hazard exposure may matter most at neighborhood scale, which means the CBSA pass could be understating its importance.

### Working Interpretation

- Affordability is still the biggest Livability subject, but the cross-topic correlation pass says it is not obviously overcounting if we keep:
  - one Price Pressure KPI
  - one Housing Burden KPI
  - one Poverty KPI
  - a compressed Housing Supply bundle
- The strongest case for consolidation is not inside Affordability. It is inside `Health & Safety`, where the injury and violence KPIs sit close to the main health-outcome line while still earning their own topic.
- `Access & Infrastructure` got stronger in this pass because the topic structure is cleaner:
  - recurring daily-life topics
  - explicit baseline topics
  - one named proxy topic
- `Education access` is weak enough to defer from the initial model.
- `Physical Environment` should stay in frame even if its coverage forces caution for now.

### Next Move

- Use the cross-topic matrix before any clustering or calibration so topic weights do not accidentally let Affordability dominate.
- Use `Health outcomes`, `Health behavior and access`, and `Violence and injury` as separate visible topics inside one broader `Health & Safety` weighting bundle.
- Run one sensitivity bundle that adds the baseline and coverage-caution topics:
  - `walkability_index`
  - `jobs_access_45min_transit`
  - `pct_population_low_income_low_access_1_10`
  - `pop_weighted_density_sqmi`
  - `unhealthy_days`
  - `fema_risk_score`
- Keep the descriptive alternates live in the notebook output even when they stay outside the default model:
  - `rent_to_income`
  - `rpp_real_pc_income`
  - `life_expectancy`
  - `child_mortality_rate`
  - `homicide_rate`
  - `mean_travel_time`
  - `permits_avg_units_per_bldg`

### Recommended Core Livability Set

- `value_to_income`
- `pct_rent_burden_30plus`
- `pov_rate`
- `permits_per_1000_housing_units`
- `permits_share_units_5_plus`
- `pct_struct_mobile`
- `pct_struct_small_mf`
- `pct_struct_mid_mf`
- `premature_death_rate`
- `mental_health_provider_ratio`
- `drug_overdose_death_rate`
- `pct_uninsured_adults`
- `preventable_hospital_stay_rate`
- `firearm_fatality_rate`
- `motor_vehicle_crash_rate`
- `pct_commute_walk`
- `pct_commute_wfh`
- `vacancy_rate`
- `pct_hh_0_vehicles`
- `pct_no_internet_access`

### Recommended Supplemental Baseline And Coverage-Caution Set

- `walkability_index`
- `jobs_access_45min_transit`
- `pct_population_low_income_low_access_1_10`
- `pop_weighted_density_sqmi`
- `unhealthy_days`
- `fema_risk_score`

### Subject Decisions

#### Affordability

**Subject decision:** Keep

**Why keep it**
- This is the deepest recurring Livability subject and one of the cleanest in coverage.
- Average topic coverage is `99.0%`.
- The notebook shows that the real challenge is de-duplicating within the subject, not deciding whether the subject belongs.

**Contrarian take**
- Affordability can swallow the rest of Livability if we carry too many near-duplicate housing-cost and permit metrics.
- The subject should stay, but it has to be compressed aggressively.

##### Price pressure

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage is `95.9%`.
- It has only `1` high-variance KPI in the notebook and behaves like a thin but important recurring affordability lens.

**KPI read**
- Recommended core KPI:
  - `value_to_income`
- Sensitivity KPIs:
  - `rent_to_income`
  - `rpp_real_pc_income`

**Data behind the call**
- The notebook keeps `value_to_income` as the lead recurring price-pressure metric.
- `rpp_real_pc_income` is useful context, but only covers `352 / 401` CBSAs.
- The topic PCA still suggests more than one conceptual story, but only one KPI really survives cleanly for default use.

**Contrarian take**
- `rent_to_income` may be the more day-to-day Livability measure even if `value_to_income` differentiates more strongly.
- If the product leans renter-first, this topic could justifiably flip to `rent_to_income`.

##### Housing burden

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage is `99.1%`.
- The notebook now preserves the recurring rent-burden field instead of letting the single-vintage CHAS series take over the topic.

**KPI read**
- Recommended core KPI:
  - `pct_rent_burden_30plus`
- Optional baseline / context KPIs:
  - `pct_cost_burdened`
  - `pct_severely_cost_burdened`
  - `pct_renter_severely_cost_burdened`
- KPI to drop from the default set:
  - `pct_rent_burden_50plus`

**Data behind the call**
- Topic PCA read: “Mostly one dominant KPI story.”
- The recurring burden read should come from the canonical ACS/Housing Core burden line, not from CHAS-only fields.
- CHAS remains valuable as context, but not as the default Phase 1 burden metric.

**Contrarian take**
- The CHAS severe-burden fields may be more analytically interesting for distress stories than the broader `30%+` threshold.
- They should stay in the sensitivity bundle even if they do not anchor the default topic.

##### Poverty context

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage is `100.0%`.
- It is a clean context topic and does not need more than one KPI.

**KPI read**
- Recommended core KPI:
  - `pov_rate`

**Data behind the call**
- Single-KPI topic in the notebook.
- It survives the topic screen as a useful affordability context field rather than a housing-price field.

**Contrarian take**
- Poverty belongs just as naturally in Opportunity or distress analysis as in Livability.
- It stays here because affordability without household stress context is too thin.

##### Housing supply

**Topic decision:** Keep, but collapse the recurring set hard

**Why keep it**
- Topic coverage is `100.0%`.
- `5` KPIs clear the variance threshold and the topic needs `2` components to explain `80%` of its variance, so there is real signal here.

**KPI read**
- Recommended core KPI:
  - `permits_per_1000_housing_units`
- Strong companion / sensitivity KPI:
  - `permits_share_units_5_plus`
- Redundant KPIs:
  - `permits_per_1000_population`
  - `permits_share_multifam_units`
  - `permits_avg_units_per_bldg`

**Data behind the call**
- The top variance read is concentrated in density-of-supply and permit-intensity measures.
- But the notebook’s correlation pass shows the whole permit family moving tightly enough that we should not carry every version at full weight.

**Contrarian take**
- `permits_avg_units_per_bldg` may be the more interpretable “what kind of supply is being built?” lens than a simple permit rate.
- If narrative clarity matters more than recurrence, it is a strong alternate lead KPI.

##### Housing structure mix

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `100.0%`.
- The topic remains genuinely multi-dimensional after screening.

**KPI read**
- Recommended core KPIs:
  - `pct_struct_mobile`
  - `pct_struct_small_mf`
- Optional third KPI:
  - `pct_struct_mid_mf`
- Redundant KPIs:
  - `pct_struct_large_mf`
  - `pct_struct_multifam`
- KPI to drop from the default set:
  - `pct_struct_sf_det`

**Data behind the call**
- `5` high-variance KPIs survive.
- Topic PCA read: “Multi-dimensional topic.”
- The signal is strongest when the topic is read as structural housing form, not as a generic single-family vs. multifamily split.

**Contrarian take**
- `pct_struct_multifam` is the simplest version and may be enough for a lighter model.
- The richer structure mix is defensible, but it does make the subject more technical.

#### Health & Safety

**Subject decision:** Keep

**Why keep it**
- Health and Safety should now be treated as one consolidated subject in the model rather than two separate subject votes.
- Average topic coverage is `98.0%`.
- The three live topics behave differently enough to keep all three visible inside the subject.

**Contrarian take**
- This subject can drift into a broad distress frame rather than daily-life livability if too many mortality and deprivation measures stay in the core.
- The subject belongs, but it needs sharper pruning than a generic “health dashboard.”

##### Health outcomes

**Topic decision:** Collapse to one lead KPI

**Why keep it**
- Topic coverage is `97.6%`.
- `3` KPIs clear the variance screen, but topic PCA says they mostly reflect one dominant underlying story.

**KPI read**
- Recommended core KPI:
  - `premature_death_rate`
- Optional sensitivity KPI:
  - `child_mortality_rate`
- KPIs to drop from the default set:
  - `life_expectancy`
  - `infant_mortality_rate`

**Data behind the call**
- The notebook flags this topic as one dominant dimension.
- `premature_death_rate` is the strongest lead signal among the outcome metrics.
- `infant_mortality_rate` is too coverage-constrained to anchor the default set.

**Contrarian take**
- `life_expectancy` is still the most intuitive public-facing health KPI.
- If presentation clarity matters more than statistical spread, it could still be the narrative lead even if it does not win the screening pass.

##### Health behavior and access

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `98.3%`.
- `6` KPIs clear the variance threshold and the topic remains genuinely multi-dimensional.

**KPI read**
- Recommended core KPIs:
  - `mental_health_provider_ratio`
  - `drug_overdose_death_rate`
  - `pct_uninsured_adults`
  - `preventable_hospital_stay_rate`
- Strong sensitivity KPIs:
  - `primary_care_ratio`
  - `child_care_cost_burden_rate`
- KPIs to drop from the default set:
  - `food_insecurity_rate`
  - `physical_inactivity`
  - `adult_obesity`
  - `poor_mental_health_days`

**Data behind the call**
- The lead variance metrics are access and acute-risk signals, not lifestyle prevalence measures.
- The notebook’s default core concentrates on access, system strain, and severe downside risk.

**Contrarian take**
- Lifestyle metrics like obesity and inactivity may matter more for long-run place health than for near-term distress.
- Dropping them from the core improves focus, but it also narrows the topic toward system failure and acute harm.

##### Violence and injury

**Topic decision:** Keep, but consolidate

**Why keep it**
- `3` KPIs clear the variance screen and the topic needs `2` components to explain `80%` of its variance.
- This is not a fake topic, but it is also not broad enough to carry a long KPI list.

**KPI read**
- Recommended core KPIs:
  - `firearm_fatality_rate`
  - `motor_vehicle_crash_rate`
- Strong sensitivity KPI:
  - `homicide_rate`

**Data behind the call**
- The notebook treats all three as meaningful but overlapping.
- `homicide_rate` is the narrowest and most tail-driven of the three.

**Contrarian take**
- `homicide_rate` is still the cleanest public violence signal.
- If the product wants a sharper urban-safety story, homicide could remain the lead despite being narrower.

#### Access & Infrastructure

**Subject decision:** Keep

**Why keep it**
- Average topic coverage is `99.1%`.
- The subject has a strong recurring ACS core plus several useful baseline-only extensions.

**Contrarian take**
- This subject is the messiest definitional area in Livability.
- It works best when we separate recurring daily-life access from one-time walkability and food-access baselines.

##### Commute and mode access

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `100.0%`.
- `3` KPIs clear the variance threshold and topic PCA says the topic is multi-dimensional.

**KPI read**
- Recommended core KPIs:
  - `pct_commute_walk`
  - `pct_commute_wfh`
- Strong sensitivity KPI:
  - `pct_commute_transit`
- KPI to drop from the default set:
  - `mean_travel_time`

**Data behind the call**
- The notebook keeps the mode shares and drops travel time.
- The surviving signal is less about congestion and more about metro mobility form.

**Contrarian take**
- `mean_travel_time` may still be the most legible “daily friction” measure for general readers.
- It loses the screening pass, but it may still deserve narrative use even if it leaves the model core.

##### Vehicle and housing access

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `100.0%`.
- Both KPIs survive cleanly and the topic has `2` meaningful sub-dimensions.

**KPI read**
- Recommended core KPIs:
  - `vacancy_rate`
  - `pct_hh_0_vehicles`

**Data behind the call**
- This is one of the cleanest two-KPI topics in the notebook.
- The pair separates market slack from transportation dependence.

**Contrarian take**
- `vacancy_rate` is partly a housing-market signal rather than a pure access KPI.
- It stays because metro access and housing slack are deeply intertwined in lived experience.

##### Digital access

**Topic decision:** Collapse to one lead KPI

**Why keep it**
- Topic coverage is `100.0%`.
- The two KPIs are effectively mirror images of the same story.

**KPI read**
- Recommended core KPI:
  - `pct_no_internet_access`
- KPI to drop from the default set:
  - `pct_broadband_subscription`

**Data behind the call**
- Topic PCA read: “Mostly one dominant KPI story.”
- The exclusion-oriented version is the sharper differentiator in the notebook.

**Contrarian take**
- `pct_broadband_subscription` is the more positive and policy-friendly framing.
- The no-access version is analytically sharper, but the subscription version may communicate better.

##### Walkability and transit baseline

**Topic decision:** Sensitivity-only topic

**Why keep it**
- Topic coverage is `98.5%`, so the baseline is wide enough to test.
- But the whole topic is still a `2021` one-time SLD baseline rather than a recurring annual panel.

**KPI read**
- Best sensitivity KPIs:
  - `walkability_index`
  - `jobs_access_45min_transit`
- Redundant baseline KPIs:
  - `transit_service_density`
  - `jobs_access_45min_auto`

**Data behind the call**
- `4` KPIs clear the variance screen and topic PCA suggests `2` sub-dimensions.
- The topic is analytically interesting, but not stable enough yet for the default recurring Livability core.

**Contrarian take**
- This is one of the most intuitively “Livability” topics in the whole frame.
- If we overweight theory and underweight recency, we risk underusing a very valuable baseline.

##### Food access baseline

**Topic decision:** Sensitivity-only topic

**Why keep it**
- Topic coverage is `97.3%`.
- It behaves like one tight baseline story rather than a recurring multi-KPI theme.

**KPI read**
- Best sensitivity KPI:
  - `pct_population_low_income_low_access_1_10`
- Alternate baseline KPI:
  - `pct_population_low_access_1_10`

**Data behind the call**
- `2` KPIs clear the variance threshold, but topic PCA says they collapse into one dominant dimension.
- The 2019-only USDA vintage is the main reason this stays out of the default core.

**Contrarian take**
- Food access is a very direct quality-of-life topic and may matter more than some of the weaker recurring commute signals.
- It is being held back by source vintage, not by concept.

##### Built-form proxy

**Topic decision:** Sensitivity-only topic

**Why keep it**
- Topic coverage is `98.8%`.
- Density is clearly live and differentiating, but it belongs first to Character and only secondarily to Livability.

**KPI read**
- Best sensitivity KPI:
  - `pop_weighted_density_sqmi`
- Alternate sensitivity KPI:
  - `gross_density_sqmi`

**Data behind the call**
- Both density KPIs survive, but topic PCA says this is mostly one dominant story.
- The notebook treats the topic explicitly as a proxy, not a default Livability axis.

**Contrarian take**
- Density may matter more for daily life than for Character in many metros.
- The proxy label is defensible, but not inevitable.

#### Education access

**Subject decision:** Drop from the Phase 1 core

**Why drop it**
- Average topic coverage is `90.9%`, but the live CHR education trio produces `0` high-variance KPIs in the notebook.
- The broader K-12 learning-quality topic is still deferred because SEDA is not in Gold.

**Contrarian take**
- Education feels too substantively important to leave out forever.
- The right read is not that education does not matter, but that the current live proxy set is too weak for the Phase 1 core.

##### School performance

**Topic decision:** Drop

**Why drop it**
- Coverage is acceptable, but the topic does not survive the variance screen.
- The current live CHR education metrics do not separate CBSAs strongly enough.

**KPI read**
- Best sensitivity KPI:
  - `math_score_index`
- Other current-topic KPIs to avoid in the default set:
  - `reading_score_index`
  - `hs_graduation_rate`

**Data behind the call**
- Topic coverage: `90.9%`
- High-variance metrics: `0`
- Topic PCA still finds more than one dimension, but the screen says those dimensions are too weak at CBSA scale.

**Contrarian take**
- `hs_graduation_rate` is still a credible public-facing education signal.
- Once better school-quality data lands, this subject could come back quickly.

#### Physical Environment

**Subject decision:** Drop from the Phase 1 core and keep only as sensitivity

**Why drop it from the core**
- Average topic coverage is only `85.7%`.
- The subject is analytically promising, but the direct-source families are still partial and the fallback CHR fields are only proxies.

**Contrarian take**
- This is the strongest “not ready yet but clearly important” subject in the Livability frame.
- It should stay close to the surface even if it is not yet part of the default core.

##### Air pollution

**Topic decision:** Sensitivity-only topic

**Why keep it as sensitivity**
- Topic coverage is `86.0%`.
- `6` KPIs clear the variance threshold and the topic is genuinely multi-dimensional.

**KPI read**
- Best sensitivity KPIs:
  - `unhealthy_days`
  - `ejs_diesel_pm`
  - `air_pollution_pm25`
- Redundant KPIs:
  - `aqi_median`
  - `aqi_p90`
  - `ejs_pm25`
- KPI to drop first:
  - `ejs_ozone`

**Data behind the call**
- This is a real topic with real spread, but it sits below the notebook’s preferred coverage floor.
- The notebook keeps both direct and proxy variants visible so we can see what is source-driven versus concept-driven.

**Contrarian take**
- Air quality is important enough that we may be underweighting it by waiting for cleaner coverage.
- A partial but substantive topic can still be better than a fully covered but weaker topic.

##### Climate hazard risk

**Topic decision:** Sensitivity-only topic

**Why keep it as sensitivity**
- Topic coverage is `88.0%`.
- Only `1` KPI clears the variance screen cleanly in the current run.

**KPI read**
- Best sensitivity KPI:
  - `adverse_climate_events`
- Future direct-source KPI to watch:
  - `fema_risk_score`

**Data behind the call**
- The notebook keeps the CHR climate proxy, but the direct FEMA fields do not yet justify a default slot in the current coverage profile.

**Contrarian take**
- This is exactly the kind of topic where source partiality may be hiding the most important long-run Livability divide.
- Once FEMA coverage stabilizes, this topic may deserve quick promotion.

##### Hazard exposure

**Topic decision:** Sensitivity-only topic

**Why keep it as sensitivity**
- Topic coverage is `83.0%`.
- The topic has real variation, but it is still too partial to fold into the default Phase 1 core.

**KPI read**
- Best sensitivity KPI:
  - `ejs_wastewater_discharge`
- Other useful sensitivity KPIs:
  - `ejs_superfund_proximity`
  - `ejs_drinking_water_noncompliance`

**Data behind the call**
- `5` KPIs clear the variance threshold.
- Topic PCA read: “Multi-dimensional topic.”
- This is a promising future subject area, but not yet a default-metric family.

**Contrarian take**
- Environmental burden often matters precisely because it is uneven and localized.
- The CBSA screen may be underestimating the topic by smoothing away the neighborhood-level story.

### Working Interpretation

- The recommended Phase 1 Livability frame is strongest when it centers four subjects:
  - `Affordability`
  - `Health`
  - `Safety`
  - `Access & Infrastructure`
- The biggest redundancy problems are:
  - the permit family
  - the housing structure family
  - the health-outcomes family
  - digital access mirrors
  - the AQI / EJ pollution family
- The weakest current topics are:
  - `Education access / School performance`
  - `Physical Environment / Climate hazard risk`
  - the baseline-only `Food access` and `Walkability` topics if we require recurring annual comparability
- The best sensitivity-test alternatives are:
  - `rent_to_income` and `rpp_real_pc_income` inside price pressure
  - `permits_avg_units_per_bldg` and `permits_share_units_5_plus` inside housing supply
  - `child_mortality_rate` inside health outcomes
  - `homicide_rate` inside safety
  - `walkability_index` and `jobs_access_45min_transit` from SLD
  - `pct_population_low_income_low_access_1_10` from USDA food access
  - `unhealthy_days`, `ejs_diesel_pm`, and `fema_risk_score` from the environment families

## Opportunity Memo

This memo translates `exploration/intelligence_framework/phase_variable_selection/opportunity_variable_selection.qmd` and its rendered HTML into a cleaner Phase 1 selection read for Opportunity.

### Frame Read

- Universe: `401` CBSAs with `pop_total >= 100000`
- Strong live families:
  - `ACS labor`, `ACS population`, `BPS permits`, and the core `FHFA HPI` fields are effectively full-coverage for the CBSA universe
  - `IRS migration` is broad enough to keep in the default frame
  - `QCEW` employment shares, location quotients, and wage fields are strong enough to evaluate at full scale
- Mixed or vintage-sensitive families:
  - `BEA CAINC` growth fields require the latest non-null growth row rather than the latest table row
  - `BEA GDP growth`, `industry_concentration_hhi`, `BFS establishment-backed rates`, and `CBP density` all require the same latest-non-null treatment
  - `ZORI` is useful, but the topic-level average coverage falls to `48.1%` once the level fields are included
  - `economic_connectedness` is a live proxy, not a direct Opportunity Atlas mobility metric
- Subject decisions from the notebook:
  - `Resident Opportunity`: keep
  - `Market / Investor Opportunity`: keep
  - `Business & Industry Opportunity`: keep
- Overall Opportunity dimensionality: `17` components explain `80%` of the variance in the surviving set, so the frame is still broad even after pruning

### Recommended Core Opportunity Set

- `income_pc_growth_5yr`
- `pct_unemployment_rate`
- `lfpr`
- `pov_rate_change_5yr`
- `qcew_private_avg_wkly_wage`
- `hpi_5yr_pct`
- `hpi_yoy_pct`
- `zori_annual_avg_yoy_pct`
- `pop_growth_5yr`
- `irs_net_migration_rate`
- `irs_net_agi`
- `permits_per_1000_housing_units`
- `permits_share_units_5_plus`
- `productivity_growth_5yr`
- `industry_concentration_hhi`
- `bfs_business_application_rate_per_1000_establishments`
- `cbp_estabs_per_1000_residents`
- `pct_ba_plus_change_5yr`
- `lq_professional`
- `lq_information`
- `lq_manufacturing`

### Subject Decisions

#### Resident Opportunity

**Subject decision:** Keep

**Why keep it**
- The subject is well-covered and analytically real.
- Average topic coverage is `98.6%`.
- The notebook shows that Resident Opportunity is not just one generic growth story; income growth, labor tightness, wages, and poverty change do not collapse fully into one axis.

**Contrarian take**
- Resident Opportunity can drift toward a generalized distress frame if we overweight poverty and labor metrics while underweighting actual mobility.
- The subject belongs, but it is still missing a true intergenerational mobility metric.

##### Income growth

**Topic decision:** Keep, but make it a one-KPI topic with a short-run sensitivity test

**Why keep it**
- Topic coverage is `96.3%`.
- The notebook technically collapses the topic to one active screened KPI, which is a sign that the family should be compressed rather than multiplied.

**KPI read**
- Recommended core KPI:
  - `income_pc_growth_5yr`
- Best sensitivity KPI:
  - `income_pc_growth_1yr`
- KPI to drop from the default set:
  - `income_pc_cagr_5yr`

**Data behind the call**
- The current Gold surface requires a latest-non-null growth pull; otherwise the `2024` row hides the growth series.
- The notebook’s topic read is effectively a one-dimension income-momentum story even though the raw variance ranking puts the 1-year field first.

**Contrarian take**
- The notebook’s variance screen likes `income_pc_growth_1yr` more than the 5-year field.
- We are still choosing `income_pc_growth_5yr` as the default because Opportunity should lean structural first and use the 1-year move as a momentum stress test.

##### Wage levels

**Topic decision:** Collapse to one lead KPI

**Why keep it**
- Topic coverage is `100.0%`.
- The two wage fields are essentially the same story at CBSA scale, so the decision is not whether to keep wages but which single wage lens to carry.

**KPI read**
- Recommended core KPI:
  - `qcew_private_avg_wkly_wage`
- Redundant KPI:
  - `qcew_total_covered_avg_wkly_wage`

**Data behind the call**
- Topic PCA read: “Mostly one dominant KPI story.”
- The notebook explicitly collapses the topic rather than treating covered and private wages as separate dimensions.

**Contrarian take**
- The broader covered-wage field may better capture the whole local labor market, especially in government-heavy metros.
- We are choosing the private wage field because it reads more directly as market-side opportunity.

##### Labor market tightness

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `99.6%`.
- The notebook reads the topic as multi-dimensional rather than a single unemployment proxy.

**KPI read**
- Recommended core KPIs:
  - `pct_unemployment_rate`
  - `lfpr`
- Best sensitivity KPIs:
  - `unemployment_rate_change_1yr`
  - `lfpr_growth_5yr`

**Data behind the call**
- `3` KPIs clear the variance screen.
- Topic PCA read: “Multi-dimensional topic.”
- The strongest live spread is in the change fields, but the level pair is still the cleaner default read for resident opportunity.

**Contrarian take**
- The short-run change fields may actually be the more newsworthy opportunity signal.
- A momentum-first interpretation would elevate `unemployment_rate_change_1yr` over the level fields.

##### Poverty and inclusion

**Topic decision:** Keep, but treat it as a one-KPI topic with inclusion sensitivity checks

**Why keep it**
- Topic coverage is `99.6%`.
- The topic has real internal structure, but it does not need a long default KPI list.

**KPI read**
- Recommended core KPI:
  - `pov_rate_change_5yr`
- Best sensitivity KPIs:
  - `pov_rate_change_1yr`
  - `gini_index`
- Baseline context KPI:
  - `pov_rate`

**Data behind the call**
- The notebook shows `3` high-variance metrics and a two-dimension topic read.
- The cleanest default story is whether resident poverty is improving over time, with inequality and short-run change held back as pressure tests.

**Contrarian take**
- `gini_index` may be the most conceptually important resident-opportunity KPI in the topic because it tests whether growth is broadly shared.
- We are not making it default because its cross-metro spread is weaker than the poverty-change family.

##### Intergenerational mobility proxy

**Topic decision:** Sensitivity-only proxy topic

**Why keep it as a proxy**
- Topic coverage is `97.3%`.
- The topic should stay in the audit because Opportunity Atlas is explicitly missing and `economic_connectedness` is the live stand-in.

**KPI read**
- Best proxy KPI:
  - `economic_connectedness`

**Data behind the call**
- The notebook shows `0` screened high-variance metrics here, so this is not a default core topic in the current CBSA run.
- The weak statistical read is exactly why it should be treated as a proxy rather than silently elevated into the main Resident bundle.

**Contrarian take**
- Even if it is low-variance at CBSA scale, `economic_connectedness` may be the most structurally important long-run resident-opportunity signal we have.
- It could still be worth carrying as a shadow KPI in later scoring calibration.

#### Market / Investor Opportunity

**Subject decision:** Keep

**Why keep it**
- This is still one of the clearest Opportunity subjects conceptually and empirically.
- Even with the rent topic dragging average topic coverage down, the subject keeps several strong live topics.

**Contrarian take**
- Market Opportunity can dominate the frame if we let housing-market heat stand in for all opportunity.
- It belongs, but it should stay separate from resident improvement rather than becoming the whole story.

##### Home price appreciation

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `97.3%`.
- The notebook shows that short-run and longer-run HPI measures are not identical.

**KPI read**
- Recommended core KPIs:
  - `hpi_5yr_pct`
  - `hpi_yoy_pct`
- Best sensitivity KPI:
  - `hpi_10yr_pct`

**Data behind the call**
- `3` HPI metrics clear the variance screen.
- Topic PCA read: “Has two meaningful sub-dimensions.”
- That is the right signal for a structural-vs-momentum housing topic.

**Contrarian take**
- The 5-year and YoY fields may still be too housing-cycle specific to generalize as a broader market-opportunity read.
- A more cautious version of the frame would cap HPI at one KPI and let permits and migration do the rest.

##### Rent growth

**Topic decision:** Keep as a one-KPI topic with strong coverage caution

**Why keep it**
- Rent momentum is too conceptually central to drop entirely.
- The annual YoY growth field is still useful even though the topic-level average coverage falls to `48.1%` once level fields are included.

**KPI read**
- Recommended core KPI:
  - `zori_annual_avg_yoy_pct`
- Best sensitivity KPI:
  - `zori_december_yoy_pct`
- Baseline context KPI:
  - `zori_annual_avg`
- KPI to drop from the default set:
  - `zori_december`

**Data behind the call**
- The notebook keeps the topic alive but clearly marks the coverage problem.
- The level fields are what pull the topic average down; the default momentum field is still the usable part of the family.

**Contrarian take**
- If we require the same coverage cleanliness as the rest of the core frame, rent growth should probably drop to sensitivity-only.
- We are keeping it because omitting rent entirely would understate investor-side market heat.

##### Population growth

**Topic decision:** Collapse to one lead KPI

**Why keep it**
- Topic coverage is `99.0%`.
- The family is clearly real, but it behaves like one dominant underlying story.

**KPI read**
- Recommended core KPI:
  - `pop_growth_5yr`
- Best sensitivity KPI:
  - `pop_growth_1yr`
- Redundant KPI:
  - `pop_cagr_5yr`

**Data behind the call**
- All `3` metrics clear the variance screen.
- Topic PCA read: “Mostly one dominant KPI story.”

**Contrarian take**
- A short-run migration boom can matter more than the 5-year average for investors trying to catch a turn.
- We are still making `pop_growth_5yr` the default because it is the cleaner structural market read.

##### Migration and wealth flows

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `98.8%`.
- The notebook shows a genuine two-part story: people movement and wealth movement are related but not identical.

**KPI read**
- Recommended core KPIs:
  - `irs_net_migration_rate`
  - `irs_net_agi`
- Redundant KPIs:
  - `irs_inflow_agi`
  - `irs_outflow_agi`

**Data behind the call**
- `4` metrics clear the variance screen.
- Topic PCA read: “Has two meaningful sub-dimensions.”
- The net fields preserve the core signal without double-counting gross flows.

**Contrarian take**
- Gross inflow and gross outflow may matter more than the net if we care about churn intensity rather than direction.
- We are trimming them because the default Phase 1 set should privilege interpretable net signals.

##### Permit activity

**Topic decision:** Keep as a multi-KPI topic

**Why keep it**
- Topic coverage is `100.0%`.
- This is one of the strongest market-side recurring topics and clearly survives with more than one signal.

**KPI read**
- Recommended core KPIs:
  - `permits_per_1000_housing_units`
  - `permits_share_units_5_plus`
- Best sensitivity KPIs:
  - `permits_share_multifam_units`
  - `permits_avg_units_per_bldg`
- Redundant KPI:
  - `permits_per_1000_population`

**Data behind the call**
- `5` metrics clear the variance screen.
- Topic PCA read: “Has two meaningful sub-dimensions.”
- The clean default split is permit intensity plus density-of-supply composition.

**Contrarian take**
- `permits_avg_units_per_bldg` may be the most interpretable “what kind of supply is actually coming?” measure in the whole topic.
- We are holding it as sensitivity because the rate-plus-5+-share pair is cleaner for default comparison.

#### Business & Industry Opportunity

**Subject decision:** Keep

**Why keep it**
- This is the richest Opportunity subject, and it is where the frame gets genuinely forward-looking rather than just reactive.
- Average topic coverage is `98.2%` after fixing the mixed-vintage pulls.

**Contrarian take**
- It is also the easiest subject to overbuild.
- The notebook shows real structure here, but the memo should compress aggressively or the business subject will overwhelm the whole frame.

##### GDP growth

**Topic decision:** Collapse to one lead KPI

**Why keep it**
- Topic coverage is `96.3%`.
- The growth family is real, but it is still one dominant economic-momentum story.

**KPI read**
- Recommended core KPI:
  - `productivity_growth_5yr`
- Best sensitivity KPI:
  - `real_gdp_growth_5yr`
- Redundant KPI:
  - `real_gdp_pc_growth_5yr`
- KPI to drop from the default set:
  - `real_gdp_cagr_5yr`

**Data behind the call**
- `4` metrics clear the variance screen.
- Topic PCA read: “Mostly one dominant KPI story.”
- The productivity version is the cleanest “better economy, not just bigger economy” read.

**Contrarian take**
- `real_gdp_growth_5yr` is simpler and may be easier to explain publicly than productivity growth.
- If presentation clarity matters more than nuance, the GDP-growth headline could still win.

##### Industry concentration

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage is `96.3%`.
- This is one of the cleanest structural Opportunity topics in the notebook.

**KPI read**
- Recommended core KPI:
  - `industry_concentration_hhi`

**Data behind the call**
- The topic survives with `1` screened KPI.
- The family is already conceptually compressed: concentration vs diversification.

**Contrarian take**
- HHI can punish specialized metros that are specialized in exactly the right future-facing sector.
- It is a useful resilience check, not a full industrial-opportunity verdict.

##### Human capital momentum

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage is `99.3%`.
- It adds a leading-indicator read that is distinct from both current wage levels and current industry mix.

**KPI read**
- Recommended core KPI:
  - `pct_ba_plus_change_5yr`
- Baseline context KPI:
  - `pct_ba_plus`

**Data behind the call**
- The notebook keeps the topic but compresses it.
- The change field is the Opportunity home for the human-capital story; the level field remains more naturally Character context.

**Contrarian take**
- Current BA+ level may matter more than recent change for already-established knowledge hubs.
- We are privileging change because Opportunity is about direction, not just status.

##### Business formation

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage rises back to `98.8%` once the mixed-vintage pull is fixed.
- The topic clearly belongs, but it should not carry four overlapping entrepreneurial-flow metrics by default.

**KPI read**
- Recommended core KPI:
  - `bfs_business_application_rate_per_1000_establishments`
- Best sensitivity KPIs:
  - `bfs_business_applications_yoy_pct`
  - `bfs_business_applications_per_1000_residents`
- Baseline context KPI:
  - `bfs_business_applications`

**Data behind the call**
- The notebook’s original automatic pass only stabilizes after we explicitly separate the `2024` BFS flow fields from the `2023` establishment-backed rate.
- With that fix, the rate field becomes the cleanest default signal.

**Contrarian take**
- The per-establishment rate inherits CBP’s vintage lag and can feel less current than the raw flow fields.
- A momentum-first product could reasonably flip to `bfs_business_applications_yoy_pct`.

##### Establishment density

**Topic decision:** Keep as a one-KPI topic

**Why keep it**
- Topic coverage is `98.8%`.
- This is a useful business-base depth check, but it does not need a large KPI family.

**KPI read**
- Recommended core KPI:
  - `cbp_estabs_per_1000_residents`
- Baseline context KPI:
  - `cbp_total_estabs`

**Data behind the call**
- The notebook treats the size-scaled density field as the real analytic signal and leaves the raw count as context.

**Contrarian take**
- Total establishment count may matter more for very large-market operator opportunity than a per-resident normalization.
- We are defaulting to density because it compares metros more cleanly.

##### Location quotient specialization

**Topic decision:** Keep as the default business-structure topic

**Why keep it**
- Topic coverage is `100.0%`.
- This is the cleanest way to express sector specialization without carrying every parallel structure family at full weight.

**KPI read**
- Recommended core KPIs:
  - `lq_professional`
  - `lq_information`
  - `lq_manufacturing`
- Best sensitivity KPI:
  - `lq_educ_health`

**Data behind the call**
- All `12` LQ fields clear the variance screen.
- Topic PCA read: “Multi-dimensional topic.”
- The memo chooses a small future-facing specialization bundle rather than carrying the whole LQ wall.

**Contrarian take**
- The notebook’s raw variance ordering puts some smaller or more cyclical sectors near the top.
- We are choosing interpretable strategic sectors over a purely variance-ranked selection.

##### Establishment mix

**Topic decision:** Sensitivity-only topic

**Why keep it as sensitivity**
- Topic coverage is `98.8%`.
- The notebook shows real signal here, but it overlaps heavily with location quotients and sector employment mix.

**KPI read**
- Best sensitivity KPIs:
  - `pct_cbp_estabs_professional`
  - `pct_cbp_estabs_information`
  - `pct_cbp_estabs_manufacturing`

**Data behind the call**
- `7` establishment-share metrics clear the variance screen.
- Topic PCA read: “Multi-dimensional topic.”
- The problem is not lack of signal; it is duplicate structure signal.

**Contrarian take**
- Establishment mix may be more stable and less noisy than employment-based sector shares.
- A business-base-first interpretation could justify promoting this topic later.

##### Sector GDP mix

**Topic decision:** Sensitivity-only topic

**Why keep it as sensitivity**
- Topic coverage is `96.3%`.
- The topic is informative, but it overlaps materially with HHI and LQ specialization.

**KPI read**
- Best sensitivity KPIs:
  - `pct_real_gdp_professional`
  - `pct_real_gdp_information`
  - `pct_real_gdp_manufacturing`
- Additional sensitivity KPI:
  - `pct_real_gdp_edu_health`

**Data behind the call**
- `11` GDP-share metrics clear the variance screen.
- Topic PCA read: “Multi-dimensional topic.”
- The notebook keeps it alive, but the memo does not want both GDP shares and LQs doing full default duty.

**Contrarian take**
- Output mix can matter more than employment mix when we care about value creation rather than job counts.
- A more productivity-focused version of Opportunity could promote this topic.

##### Sector employment mix

**Topic decision:** Sensitivity-only topic

**Why keep it as sensitivity**
- Topic coverage is `100.0%`.
- The topic is fully live, but it duplicates much of the specialization story already captured by LQ.

**KPI read**
- Best sensitivity KPIs:
  - `pct_qcew_private_emp_professional`
  - `pct_qcew_private_emp_information`
  - `pct_qcew_private_emp_manufacturing`
- Additional sensitivity KPI:
  - `pct_qcew_private_emp_educ_health`

**Data behind the call**
- All `12` employment-share metrics clear the variance screen.
- Topic PCA read: “Multi-dimensional topic.”
- The memo is intentionally not carrying both employment-share and LQ families as equal-default structure blocks.

**Contrarian take**
- Employment shares are more intuitive than location quotients for most readers.
- If communication simplicity matters more than benchmark sophistication, this topic could win instead.

##### Sector wage mix

**Topic decision:** Sensitivity-only topic

**Why keep it as sensitivity**
- Topic coverage is `97.2%`.
- The sector wage family is useful for the Autor-style job-quality read, but it is too large and too overlapping to keep in the default core.

**KPI read**
- Best sensitivity KPIs:
  - `qcew_private_avg_wkly_wage_professional`
  - `qcew_private_avg_wkly_wage_information`
  - `qcew_private_avg_wkly_wage_manufacturing`
- Additional sensitivity KPI:
  - `qcew_private_avg_wkly_wage_finance_real`

**Data behind the call**
- `8` sector wage metrics clear the variance screen.
- Topic PCA read: “Multi-dimensional topic.”
- The cleaner default move is to keep one overall wage-level topic in Resident Opportunity and reserve sector wages for pressure tests.

**Contrarian take**
- Sector wage quality may be exactly what separates a healthy labor market from a hollow one.
- Once we get deeper into scoring calibration, this topic could prove more important than the default memo gives it credit for.

### Working Interpretation

- The recommended Phase 1 Opportunity frame is strongest when it centers three subjects:
  - `Resident Opportunity`
  - `Market / Investor Opportunity`
  - `Business & Industry Opportunity`
- The recommended default business-structure family is `Location quotient specialization`; the other sector-share and sector-wage families should stay as sensitivity bundles rather than all entering the core at once.
- The biggest redundancy problems are:
  - `1yr` vs `5yr` vs `CAGR` variants inside income, population, and GDP growth
  - gross IRS AGI flow fields vs `irs_net_agi`
  - permit denominator and composition variants
  - covered wage vs private wage
  - the overlap among `LQ`, `QCEW sector shares`, `BEA GDP shares`, `CBP establishment shares`, and `QCEW sector wage` families
- The weakest current topics are:
  - `Intergenerational mobility proxy`, because it is still only a proxy and shows low variance at CBSA scale
  - `Rent growth`, because the topic-level coverage profile is still weak once the level fields are included
  - `Establishment mix`, `Sector GDP mix`, `Sector employment mix`, and `Sector wage mix` as default topics, because they are all individually real but collectively too redundant
- The best sensitivity-test alternatives are:
  - `income_pc_growth_1yr`, `unemployment_rate_change_1yr`, and `gini_index` inside Resident Opportunity
  - `hpi_10yr_pct`, `pop_growth_1yr`, and `zori_december_yoy_pct` inside Market Opportunity
  - `permits_avg_units_per_bldg` and `permits_share_multifam_units` inside permit activity
  - `real_gdp_growth_5yr` instead of `productivity_growth_5yr`
  - `bfs_business_applications_yoy_pct` and `bfs_business_applications_per_1000_residents` inside business formation
  - `pct_qcew_private_emp_*`, `pct_real_gdp_*`, `pct_cbp_estabs_*`, and `qcew_private_avg_wkly_wage_*` as alternate business-structure bundles
  - `economic_connectedness` as the explicit Opportunity proxy until Opportunity Atlas lands
