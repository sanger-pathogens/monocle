# **************************************************************
# Rename submitting institution and remove non-submitting one
# **************************************************************

-- Rename Faculty of Pharmacy, Suez Canal University as Ulm Univesity in api_sample table

UPDATE api_sample
SET submitting_institution = 'Ulm University'
WHERE submitting_institution = 'Faculty of Pharmacy, Suez Canal University';

-- Remove Faculty of Pharmacy, Suez Canal University from api_institution table

DELETE FROM api_institution
WHERE name = 'Faculty of Pharmacy, Suez Canal University';

--
-- Update the database version
--
CALL update_database_version('0.2.87', 'Rename submitting instituon and remove redundant/non-submitting one');
