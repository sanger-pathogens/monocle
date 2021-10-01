# **************************************************************
# Include more variant columns in in_silico table
# **************************************************************

ALTER TABLE `in_silico`
ADD COLUMN `23S1_variant` varchar(256) AFTER `SRR2`;

ALTER TABLE `in_silico`
ADD COLUMN `23S3_variant` varchar(256) AFTER `23S1_variant`,

ALTER TABLE `in_silico`
ADD COLUMN `RPOBGBS-1_variant` varchar(256),
ADD COLUMN `RPOBGBS-2_variant` varchar(256),
ADD COLUMN `RPOBGBS-3_variant` varchar(256),
ADD COLUMN `RPOBGBS-4_variant` varchar(256);

CALL update_database_version('0.2.32', 'Add 23S1_variant, 23S3_variant, RPOBGBS-1_variant, RPOBGBS-2_variant, RPOBGBS-3_variant and RPOBGBS-4_variant columns');
