# **************************************************************
# Change MLST column name in in_silico table.
# **************************************************************

ALTER TABLE `in_silico` CHANGE `MLST` `ST` varchar(256);

CALL update_database_version('0.2.29', 'Rename MLST to ST');
