# **************************************************************
# Increase varchar size for JUNO variants (in-silico table)
# **************************************************************

-- Amend VARCHAR size
ALTER TABLE `in_silico` MODIFY `twenty_three_S1_variant` VARCHAR(256);
ALTER TABLE `in_silico` MODIFY `twenty_three_S3_variant` VARCHAR(256);
ALTER TABLE `in_silico` MODIFY `GYRA_variant` VARCHAR(256);
ALTER TABLE `in_silico` MODIFY `PARC_variant` VARCHAR(256);


-- Update the database version
CALL update_database_version('0.9.5', 'Increase varchar size for JUNO variants (in-silico table)')
