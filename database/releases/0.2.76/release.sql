# **************************************************************
# Replace common variants "*" with empty values (in silico data)
# **************************************************************

-- affected fields: twenty_three_S1_variant, twenty_three_S3_variant, GYRA_variant, PARC_variant, RPOBGBS_1_variant, RPOBGBS_2_variant, RPOBGBS_3_variant, RPOBGBS_4_variant

UPDATE in_silico 
SET twenty_three_S1_variant = ''
WHERE twenty_three_S1_variant = '*';

UPDATE in_silico 
SET twenty_three_S3_variant = ''
WHERE twenty_three_S3_variant = '*';

UPDATE in_silico 
SET GYRA_variant = ''
WHERE GYRA_variant = '*';

UPDATE in_silico 
SET PARC_variant = ''
WHERE PARC_variant = '*';

UPDATE in_silico 
SET RPOBGBS_1_variant = ''
WHERE RPOBGBS_1_variant = '*';

UPDATE in_silico 
SET RPOBGBS_2_variant = ''
WHERE RPOBGBS_2_variant = '*';

UPDATE in_silico 
SET RPOBGBS_3_variant = ''
WHERE RPOBGBS_3_variant = '*';

UPDATE in_silico 
SET RPOBGBS_4_variant = ''
WHERE RPOBGBS_4_variant = '*';

-- Update the database version
CALL update_database_version('0.2.76', 'Replace * with empty values. Affected: twenty_three_S1_variant, twenty_three_S3_variant, GYRA_variant, PARC_variant, RPOBGBS_1_variant, RPOBGBS_2_variant, RPOBGBS_3_variant, RPOBGBS_4_variant');
