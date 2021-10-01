# **************************************************************
# Include more variant columns in in_silico table
# **************************************************************

ALTER TABLE `in_silico`
ADD COLUMN `23S1_variant` varchar(256) AFTER `SRR2`;

ALTER TABLE `in_silico`
ADD COLUMN `23S3_variant` varchar(256) AFTER `23S1_variant`;

ALTER TABLE `in_silico`
ADD COLUMN `RPOBGBS_1_variant` varchar(256),
ADD COLUMN `RPOBGBS_2_variant` varchar(256),
ADD COLUMN `RPOBGBS_3_variant` varchar(256),
ADD COLUMN `RPOBGBS_4_variant` varchar(256);

CALL update_database_version('0.2.32', 'Add 23S1_variant, 23S3_variant, RPOBGBS_1_variant, RPOBGBS_2_variant, RPOBGBS_3_variant and RPOBGBS_4_variant columns');
