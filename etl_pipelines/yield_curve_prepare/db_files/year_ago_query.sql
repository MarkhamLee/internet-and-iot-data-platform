SELECT * FROM raw_yield_curve_data
ORDER BY "date" DESC
OFFSET 250 ROWS              
FETCH NEXT 1 ROWS ONLY;