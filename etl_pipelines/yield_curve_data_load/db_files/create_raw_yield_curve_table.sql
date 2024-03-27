CREATE TABLE IF NOT EXISTS raw_yield_curve_data (
  "date" date PRIMARY_KEY,
  "1_mo" numeric,
  "2_mo" numeric,
  "3_mo" numeric,
  "4_mo" numeric,
  "6_mo" numeric,
  "1_yr" numeric,
  "2_yr" numeric,
  "3_yr" numeric,
  "5_yr" numeric,
  "7_yr" numeric,
  "10_yr" numeric,
  "20_yr" numeric,
  "30_yr" numeric
) 
