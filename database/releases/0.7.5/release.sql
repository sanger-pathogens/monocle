# ***************************************************************
# qc_data field HET_SNPs_status increased size
# ***************************************************************

ALTER TABLE `qc_data` MODIFY `QC_pipeline_version` VARCHAR(256) NOT NULL;

CALL update_database_version('0.7.5', 'bug fix for JUNO QC data');
