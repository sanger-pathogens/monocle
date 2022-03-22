# **************************************************************
# Rename columns
# **************************************************************

ALTER TABLE `in_silico`
CHANGE `23S1_variant` `twenty_three_S1_variant` varchar(256);

ALTER TABLE `in_silico`
CHANGE `23S3_variant` `twenty_three_S3_variant` varchar(256);

CALL update_database_version('0.2.33', 'Change 23 to twenty_three in column names');
