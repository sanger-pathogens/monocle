# **************************************************************
# Update submitting institutions
# **************************************************************

-- 1. Add "Centre of Expertise and Biological Diagnostic of Cameroon (CEDBCAM)" institution in api_institution table

INSERT INTO api_institution (name, country, latitude, longitude)
VALUES ('Centre of Expertise and Biological Diagnostic of Cameroon (CEDBCAM)', 'Cameroon', 3.833870822724538, 11.486905970132005);

-- 2. Rename Institution
-- 2.1. Add new institution (Çukurova University, Faculty of Medicine, Department of Medical Microbiology) in api_institution table

INSERT INTO api_institution (name, country, latitude, longitude)
VALUES ('Çukurova University, Faculty of Medicine, Department of Medical Microbiology', 'Israel', 31.790605, 35.202278);

-- 2.2. Rename "Toros University" to "Çukurova University, Faculty of Medicine, Department of Medical Microbiology" in api_sample table

UPDATE api_sample
SET submitting_institution = 'Çukurova University, Faculty of Medicine, Department of Medical Microbiology'
WHERE submitting_institution = 'Toros University';

-- 2.3. Remove "Toros University" from api_institution table

DELETE FROM api_institution
WHERE name = 'Toros University';

--
-- Update the database version
--
CALL update_database_version('0.2.91', 'Update submitting institutions');
