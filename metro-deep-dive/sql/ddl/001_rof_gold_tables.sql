-- Bootstrap the rof_gold schema and all app-facing tables.
-- Run once on a fresh rof_app.duckdb, or re-run safely (CREATE IF NOT EXISTS).
-- Export pipeline populates these tables; this file only defines structure.

CREATE SCHEMA IF NOT EXISTS rof_gold;

-- ── Market reference ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS rof_gold.market_profiles (
    market_key          VARCHAR PRIMARY KEY,
    cbsa_code           VARCHAR,
    state_scope         VARCHAR,
    cbsa_name           VARCHAR,
    cbsa_name_full      VARCHAR,
    market_name         VARCHAR,
    target_flag         VARCHAR,
    build_source        VARCHAR,
    run_timestamp       VARCHAR
);

-- ── Geography / geometry ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS rof_gold.cbsa_geometry (
    cbsa_code   VARCHAR PRIMARY KEY,
    geom_wkt    VARCHAR
);

CREATE TABLE IF NOT EXISTS rof_gold.county_geometry (
    cbsa_code       VARCHAR,
    county_geoid    VARCHAR,
    geom_wkt        VARCHAR,
    PRIMARY KEY (cbsa_code, county_geoid)
);

CREATE TABLE IF NOT EXISTS rof_gold.tract_geometry (
    cbsa_code       VARCHAR,
    tract_geoid     VARCHAR,
    geom_wkt        VARCHAR,
    PRIMARY KEY (cbsa_code, tract_geoid)
);

-- ── Tract features and scores ───────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS rof_gold.tract_features (
    cbsa_code               VARCHAR,
    county_geoid            VARCHAR,
    tract_geoid             VARCHAR,
    year                    INTEGER,
    pop_total               DOUBLE,
    pop_growth_3yr          DOUBLE,
    pop_growth_pctl         DOUBLE,
    pop_growth_5yr          DOUBLE,
    median_hh_income        DOUBLE,
    per_capita_income       DOUBLE,
    pov_rate                DOUBLE,
    income_pctl             DOUBLE,
    median_gross_rent       DOUBLE,
    median_home_value       DOUBLE,
    rent_pctl               DOUBLE,
    value_pctl              DOUBLE,
    price_proxy_pctl        DOUBLE,
    pct_commute_wfh         DOUBLE,
    mean_travel_time        DOUBLE,
    commute_intensity_b     DOUBLE,
    total_units_3yr_avg     DOUBLE,
    units_per_1k_3yr        DOUBLE,
    pop_density             DOUBLE,
    land_area_sqmi          DOUBLE,
    density_pctl            DOUBLE,
    gate_pop                INTEGER,
    gate_price              INTEGER,
    gate_density            INTEGER,
    eligible_v1             INTEGER,
    PRIMARY KEY (cbsa_code, tract_geoid, year)
);

CREATE TABLE IF NOT EXISTS rof_gold.tract_scores (
    market_key          VARCHAR,
    cbsa_code           VARCHAR,
    county_geoid        VARCHAR,
    tract_geoid         VARCHAR,
    year                INTEGER,
    eligible_v1         INTEGER,
    gate_pop            INTEGER,
    gate_price          INTEGER,
    gate_density        INTEGER,
    tract_score         DOUBLE,
    tract_rank          INTEGER,
    is_scored           BOOLEAN,
    why_tags            VARCHAR,
    -- raw z-score components (useful for detail panel)
    z_growth            DOUBLE,
    z_units             DOUBLE,
    z_headroom          DOUBLE,
    z_price             DOUBLE,
    z_commute           DOUBLE,
    z_income            DOUBLE,
    PRIMARY KEY (cbsa_code, tract_geoid)
);

-- ── Zone tables ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS rof_gold.cluster_assignments (
    market_key      VARCHAR,
    cbsa_code       VARCHAR,
    tract_geoid     VARCHAR,
    cluster_id      VARCHAR,
    cluster_label   VARCHAR,
    cluster_order   INTEGER,
    tract_score     DOUBLE,
    zone_method     VARCHAR,
    PRIMARY KEY (market_key, tract_geoid)
);

CREATE TABLE IF NOT EXISTS rof_gold.cluster_zone_summary (
    market_key              VARCHAR,
    cbsa_code               VARCHAR,
    cluster_id              VARCHAR,
    cluster_label           VARCHAR,
    cluster_order           INTEGER,
    tracts                  INTEGER,
    total_population        DOUBLE,
    pop_growth_3yr_wtd      DOUBLE,
    pop_density_median      DOUBLE,
    units_per_1k_3yr_wtd    DOUBLE,
    price_proxy_pctl_median DOUBLE,
    mean_tract_score        DOUBLE,
    zone_area_sq_mi         DOUBLE,
    zone_method             VARCHAR,
    PRIMARY KEY (market_key, cluster_id)
);

CREATE TABLE IF NOT EXISTS rof_gold.cluster_zone_geometries (
    market_key      VARCHAR,
    cbsa_code       VARCHAR,
    cluster_id      VARCHAR,
    cluster_label   VARCHAR,
    cluster_order   INTEGER,
    zone_area_sq_mi DOUBLE,
    label_lon       DOUBLE,
    label_lat       DOUBLE,
    geom_wkt        VARCHAR,
    zone_method     VARCHAR,
    PRIMARY KEY (market_key, cluster_id)
);

CREATE TABLE IF NOT EXISTS rof_gold.contiguity_zone_summary (
    market_key              VARCHAR,
    cbsa_code               VARCHAR,
    zone_id                 VARCHAR,
    zone_label              VARCHAR,
    zone_order              INTEGER,
    tracts                  INTEGER,
    total_population        DOUBLE,
    pop_growth_3yr_wtd      DOUBLE,
    pop_density_median      DOUBLE,
    units_per_1k_3yr_wtd    DOUBLE,
    price_proxy_pctl_median DOUBLE,
    mean_tract_score        DOUBLE,
    zone_area_sq_mi         DOUBLE,
    zone_method             VARCHAR,
    PRIMARY KEY (market_key, zone_id)
);

CREATE TABLE IF NOT EXISTS rof_gold.contiguity_zone_geometries (
    market_key      VARCHAR,
    cbsa_code       VARCHAR,
    zone_id         VARCHAR,
    zone_label      VARCHAR,
    zone_order      INTEGER,
    zone_area_sq_mi DOUBLE,
    label_lon       DOUBLE,
    label_lat       DOUBLE,
    geom_wkt        VARCHAR,
    zone_method     VARCHAR,
    PRIMARY KEY (market_key, zone_id)
);

-- ── Parcel tables ───────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS rof_gold.retail_parcels (
    market_key              VARCHAR,
    cbsa_code               VARCHAR,
    county_geoid            VARCHAR,
    county_name             VARCHAR,
    parcel_uid              VARCHAR PRIMARY KEY,
    join_key                VARCHAR,
    land_use_code           VARCHAR,
    land_use_category       VARCHAR,
    land_use_description    VARCHAR,
    retail_flag             BOOLEAN,
    retail_subtype          VARCHAR,
    owner_name              VARCHAR,
    site_addr               VARCHAR,
    living_area_sqft        DOUBLE,
    just_value              DOUBLE,
    land_value              DOUBLE,
    impro_value             DOUBLE,
    total_value             DOUBLE,
    last_sale_price         DOUBLE,
    last_sale_date          DATE
);

-- Geometry stored separately so tabular queries stay fast.
CREATE TABLE IF NOT EXISTS rof_gold.parcel_geometry (
    join_key        VARCHAR PRIMARY KEY,
    geom_wkt        VARCHAR,       -- full polygon WKT (EPSG:4326)
    centroid_lat    DOUBLE,
    centroid_lon    DOUBLE,
    area_sqmi       DOUBLE
);

-- ── Serving tables (pre-joined, app-ready) ──────────────────────────────────

CREATE TABLE IF NOT EXISTS rof_gold.parcel_shortlist (
    market_key                      VARCHAR,
    cbsa_code                       VARCHAR,
    zone_system                     VARCHAR,
    zone_id                         VARCHAR,
    zone_label                      VARCHAR,
    shortlist_rank_system           BIGINT,
    shortlist_rank_zone             BIGINT,
    parcel_uid                      VARCHAR,
    parcel_id                       VARCHAR,
    tract_geoid                     VARCHAR,
    county_geoid                    VARCHAR,
    county_name                     VARCHAR,
    state_abbr                      VARCHAR,
    land_use_code                   VARCHAR,
    retail_subtype                  VARCHAR,
    owner_name                      VARCHAR,
    site_addr                       VARCHAR,
    parcel_area_sqmi                DOUBLE,
    just_value                      DOUBLE,
    last_sale_date                  DATE,
    last_sale_price                 DOUBLE,
    local_retail_context_score      DOUBLE,
    mean_tract_score                DOUBLE,
    zone_quality_score              DOUBLE,
    parcel_characteristics_score    DOUBLE,
    shortlist_score                 DOUBLE,
    PRIMARY KEY (market_key, zone_system, parcel_uid)
);

CREATE TABLE IF NOT EXISTS rof_gold.parcel_zone_overlay (
    market_key                  VARCHAR,
    cbsa_code                   VARCHAR,
    zone_system                 VARCHAR,
    zone_id                     VARCHAR,
    zone_label                  VARCHAR,
    zone_order                  INTEGER,
    tracts                      BIGINT,
    total_population            DOUBLE,
    zone_area_sq_mi             DOUBLE,
    retail_parcel_count         HUGEINT,
    retail_area                 DOUBLE,
    retail_area_density         DOUBLE,
    local_retail_context_score  DOUBLE,
    mean_tract_score            DOUBLE,
    zone_quality_score          DOUBLE,
    PRIMARY KEY (market_key, zone_system, zone_id)
);

CREATE TABLE IF NOT EXISTS rof_gold.retail_intensity_by_tract (
    market_key                          VARCHAR,
    cbsa_code                           VARCHAR,
    county_geoid                        VARCHAR,
    tract_geoid                         VARCHAR,
    retail_parcel_count                 BIGINT,
    retail_area                         DOUBLE,
    retail_area_density                 DOUBLE,
    pctl_tract_retail_parcel_count      DOUBLE,
    pctl_tract_retail_area_density      DECIMAL(2,1),
    local_retail_context_score          DOUBLE,
    PRIMARY KEY (market_key, tract_geoid)
);

CREATE TABLE IF NOT EXISTS rof_gold.retail_parcel_tract_assignment (
    market_key          VARCHAR,
    cbsa_code           VARCHAR,
    county_geoid        VARCHAR,
    county_name         VARCHAR,
    parcel_uid          VARCHAR,
    join_key            VARCHAR,
    land_use_code       VARCHAR,
    retail_subtype      VARCHAR,
    tract_geoid         VARCHAR,
    assignment_method   VARCHAR,
    assignment_status   VARCHAR,
    PRIMARY KEY (market_key, parcel_uid)
);

-- ── User-authored tables (never overwritten by export pipeline) ─────────────

CREATE TABLE IF NOT EXISTS rof_gold.user_shortlist (
    parcel_uid      VARCHAR,
    market_key      VARCHAR,
    user_id         VARCHAR,
    -- status options: active | needs_review | watchlist | rejected
    status          VARCHAR DEFAULT 'active',
    notes           VARCHAR DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (parcel_uid, market_key, user_id)
);
