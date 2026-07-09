# Florida County Manual Config Stanzas

Set these once in your R session before using any county stanza:

```r
property_tax_root <- Sys.getenv("PROPERTY_TAX_ROOT")
duckdb_path <- Sys.getenv("ROF_DUCKDB_PATH")
parcel_geom_root <- file.path(property_tax_root, "parcel_geom")
```

## Alachua County

```r
state <- "FL"
county_name <- "Alachua County"
county_tag <- "alachua_fl"
county_geoid <- "12001"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NAL11F202501.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "alachua_2025Ppar", "alachua_2025Ppar.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```

## Baker County

```r
state <- "FL"
county_name <- "Baker County"
county_tag <- "baker_fl"
county_geoid <- "12003"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NALBAKER12F202502VAB.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "baker_2025Ppar", "baker_2025Ppar.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```

## Clay County

```r
state <- "FL"
county_name <- "Clay County"
county_tag <- "clay_fl"
county_geoid <- "12019"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NALCLAY20F202502.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "clay_2025Ppar", "clay_2025Ppar.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```

## Duval County

```r
state <- "FL"
county_name <- "Duval County"
county_tag <- "duval_fl"
county_geoid <- "12031"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NALDUVAL26F202501.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "duval_2025Ppar", "duval_2025Ppar.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```

## Gilchrist County

```r
state <- "FL"
county_name <- "Gilchrist County"
county_tag <- "gilchrist_fl"
county_geoid <- "12041"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NAL31F202502VAB.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "gilchrist_2025Ppar", "gilchrist_2025Ppar.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```

## Lake County

```r
state <- "FL"
county_name <- "Lake County"
county_tag <- "lake_fl"
county_geoid <- "12069"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NAL45F202501.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "lake_2025Ppar", "lake_2025Ppar.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```

## Levy County

```r
state <- "FL"
county_name <- "Levy County"
county_tag <- "levy_fl"
county_geoid <- "12075"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NAL48F202501.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "levy_2025par", "levy_2025par.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```

## Nassau County

```r
state <- "FL"
county_name <- "Nassau County"
county_tag <- "nassau_fl"
county_geoid <- "12089"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NALNASSAU55F202501.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "nassau_2025par", "nassau_2025par.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```

## Orange County

```r
state <- "FL"
county_name <- "Orange County"
county_tag <- "orange_fl"
county_geoid <- "12095"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NAL58F202501.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "orange_2025par", "orange_2025par.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```

## Osceola County

```r
state <- "FL"
county_name <- "Osceola County"
county_tag <- "osceola_fl"
county_geoid <- "12097"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NAL59F202501.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "osceola_2025par", "osceola_2025par.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```

## Seminole County

```r
state <- "FL"
county_name <- "Seminole County"
county_tag <- "seminole_fl"
county_geoid <- "12117"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NAL69F202501.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "seminole_2025par", "seminole_2025par.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```

## St. Johns County

```r
state <- "FL"
county_name <- "St. Johns County"
county_tag <- "stjohns_fl"
county_geoid <- "12109"
tabular_path <- file.path(property_tax_root, "fl", "data", "tabular", "NALSTJOHN65F202502.csv")
geom_path <- file.path(property_tax_root, "fl", "data", "stjohns_2025par", "stjohns_2025par.shp")
parcel_duckdb_schema <- "rof_parcel"
repair_invalid_geom <- FALSE
```
