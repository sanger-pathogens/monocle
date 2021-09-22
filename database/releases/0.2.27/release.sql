# **************************************************************
# Change column name in in_silico table.
# **************************************************************

ALTER TABLE `in_silico` CHANGE `gbs_typer_serotype` `cps_type` varchar(256);

CALL update_database_version('0.2.27', 'Rename gbs_typer_serotype to cps_type');
