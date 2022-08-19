# **************************************************************
# Fix MySQL data type for GPS QC table
# **************************************************************

-- Add missing CHECK statement to Hetsites_50bp data type (gps_qc_data table)
ALTER TABLE `gps_qc_data` MODIFY `Hetsites_50bp` SMALLINT(4) CHECK (Hetsites_50bp>=0 AND Hetsites_50bp<=5000);

-- Update the database version
CALL update_database_version('0.9.1', 'Fix MySQL data type for GPS QC table');
