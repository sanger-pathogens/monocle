# **************************************************************
# Increase varchar size for JUNO variants (in-silico table)
# **************************************************************

-- Add missing CHECK statement to Hetsites_50bp data type (gps_qc_data table)
ALTER TABLE `in_silico` MODIFY `twenty_three_S1_variant` VARCHAR(256);
ALTER TABLE `in_silico` MODIFY `twenty_three_S3_variant` VARCHAR(256);
ALTER TABLE `in_silico` MODIFY `GYRA_variant` VARCHAR(256);
ALTER TABLE `in_silico` MODIFY `PARC_variant` VARCHAR(256);


-- Update the database version
CALL update_database_version('0.9.5', 'Increase varchar size for JUNO variants (in-silico table)')
