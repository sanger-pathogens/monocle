# **************************************************************
# Include more resistance genes and rearrange columns in in_silico table
# **************************************************************

ALTER TABLE `in_silico`
DROP COLUMN `CAT`;

ALTER TABLE `in_silico`
ADD COLUMN `AAC6APH2` varchar(30) AFTER `twenty_three_S3`;

ALTER TABLE `in_silico`
ADD COLUMN `AADECC` varchar(30) AFTER `AAC6APH2`;

ALTER TABLE `in_silico`
ADD COLUMN `ANT6` varchar(30) AFTER `AADECC`;

ALTER TABLE `in_silico`
ADD COLUMN `APH3III` varchar(30) AFTER `ANT6`;

ALTER TABLE `in_silico`
ADD COLUMN `APH3OTHER` varchar(30) AFTER `APH3III`;

ALTER TABLE `in_silico`
ADD COLUMN `CATPC194` varchar(30) AFTER `APH3OTHER`;

ALTER TABLE `in_silico`
ADD COLUMN `CATQ` varchar(30) AFTER `CATPC194`;

ALTER TABLE `in_silico`
MODIFY COLUMN `FOSA` varchar(30) AFTER `MSRD`;

ALTER TABLE `in_silico`
MODIFY COLUMN `GYRA` varchar(30) AFTER `FOSA`;

ALTER TABLE `in_silico`
ADD COLUMN `ERMA` varchar(30) AFTER `CATQ`;

ALTER TABLE `in_silico`
ADD COLUMN `LNUC` varchar(30) AFTER `LNUB`;

CALL update_database_version('0.2.40', 'Remove CAT, add AAC6APH2, AADECC, ANT6, APH3III, APH3OTHER, CATPC194, CATQ, ERMA, LNUC and move FOSA and GYRA');
