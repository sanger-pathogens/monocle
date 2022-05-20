# **************************************************************
# Rename submitting institution
# **************************************************************

-- Add new institution (Ministry of Health, Central Laboratories) in api_institution table

INSERT INTO api_institution (name, country, latitude, longitude)
VALUES ('Ministry of Health, Central Laboratories', 'Israel', 31.790605, 35.202278);

-- Rename National Reference Laboratories to Ministry of Health, Central Laboratories in api_sample table

UPDATE api_sample
SET submitting_institution = 'Ministry of Health, Central Laboratories'
WHERE submitting_institution = 'National Reference Laboratories';

-- Remove National Reference Laboratories to Ministry of Health, Central Laboratories in api_sample table

DELETE FROM api_institution
WHERE name = 'National Reference Laboratories';

--
-- Update the database version
--
CALL update_database_version('0.2.88', 'Rename submitting institution');
