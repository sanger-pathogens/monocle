# **************************************************************
# Monocle database sample table changes for extended metadata.
# This is a SQL version of the DJango migration, for use
# on the production database now that the Django component
# is being retired.
# **************************************************************

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

ALTER TABLE `api_sample` DROP INDEX `public_name`;
-- This next constraint name is different on dev/prod.
-- This is the production id...
ALTER TABLE `api_sample` DROP INDEX `api_sample_lane_id_ecee6aef_uniq`;

ALTER TABLE `api_sample` MODIFY `host_status` varchar(256) DEFAULT NULL;
ALTER TABLE `api_sample` MODIFY `serotype` varchar(7) DEFAULT NULL;
ALTER TABLE `api_sample` ADD `supplier_sample_name` varchar(256) NOT NULL AFTER `public_name`;
ALTER TABLE `api_sample` ADD `age_days` int(11) DEFAULT NULL;
ALTER TABLE `api_sample` ADD `age_group` varchar(30);
ALTER TABLE `api_sample` ADD `age_months` int(11) DEFAULT NULL;
ALTER TABLE `api_sample` ADD `age_weeks` int(11) DEFAULT NULL;
ALTER TABLE `api_sample` ADD `age_years` int(11) DEFAULT NULL;
ALTER TABLE `api_sample` ADD `ampicillin` varchar(30);
ALTER TABLE `api_sample` ADD `ampicillin_method` varchar(60);
ALTER TABLE `api_sample` ADD `apgar_score` smallint(6) DEFAULT NULL;
ALTER TABLE `api_sample` ADD `birthweight_gram` int(11) DEFAULT NULL;
ALTER TABLE `api_sample` ADD `cefazolin` varchar(30);
ALTER TABLE `api_sample` ADD `cefazolin_method` varchar(60);
ALTER TABLE `api_sample` ADD `cefotaxime` varchar(30);
ALTER TABLE `api_sample` ADD `cefotaxime_method` varchar(60);
ALTER TABLE `api_sample` ADD `cefoxitin` varchar(30);
ALTER TABLE `api_sample` ADD `cefoxitin_method` varchar(60);
ALTER TABLE `api_sample` ADD `ceftizoxime` varchar(30);
ALTER TABLE `api_sample` ADD `ceftizoxime_method` varchar(60);
ALTER TABLE `api_sample` ADD `ciprofloxacin` varchar(30);
ALTER TABLE `api_sample` ADD `ciprofloxacin_method` varchar(60);
ALTER TABLE `api_sample` ADD `city` varchar(200);
ALTER TABLE `api_sample` ADD `clindamycin` varchar(30);
ALTER TABLE `api_sample` ADD `clindamycin_method` varchar(60);
ALTER TABLE `api_sample` ADD `collection_day` smallint(6) DEFAULT NULL;
ALTER TABLE `api_sample` ADD `collection_month` smallint(6) DEFAULT NULL;
ALTER TABLE `api_sample` ADD `collection_year` smallint(6) DEFAULT NULL;
ALTER TABLE `api_sample` ADD `country` varchar(90);
ALTER TABLE `api_sample` ADD `county_state` varchar(200);
ALTER TABLE `api_sample` ADD `daptomycin` varchar(30);
ALTER TABLE `api_sample` ADD `daptomycin_method` varchar(60);
ALTER TABLE `api_sample` ADD `disease_onset` varchar(10);
ALTER TABLE `api_sample` ADD `disease_type` varchar(100);
ALTER TABLE `api_sample` ADD `erythromycin` varchar(30);
ALTER TABLE `api_sample` ADD `erythromycin_method` varchar(60);
ALTER TABLE `api_sample` ADD `gender` varchar(10);
ALTER TABLE `api_sample` ADD `gestational_age_weeks` smallint(6) DEFAULT NULL;
ALTER TABLE `api_sample` ADD `host_species` varchar(100);
ALTER TABLE `api_sample` ADD `infection_during_pregnancy` varchar(10);
ALTER TABLE `api_sample` ADD `isolation_source` varchar(100);
ALTER TABLE `api_sample` ADD `levofloxacin` varchar(30);
ALTER TABLE `api_sample` ADD `levofloxacin_method` varchar(60);
ALTER TABLE `api_sample` ADD `linezolid` varchar(30);
ALTER TABLE `api_sample` ADD `linezolid_method` varchar(60);
ALTER TABLE `api_sample` ADD `maternal_infection_type` varchar(100);
ALTER TABLE `api_sample` ADD `penicillin` varchar(30);
ALTER TABLE `api_sample` ADD `penicillin_method` varchar(60);
ALTER TABLE `api_sample` ADD `selection_random` varchar(10);
ALTER TABLE `api_sample` ADD `serotype_method` varchar(100);
ALTER TABLE `api_sample` ADD `study_name` varchar(600);
ALTER TABLE `api_sample` ADD `study_ref` varchar(400);
ALTER TABLE `api_sample` ADD `tetracycline` varchar(30);
ALTER TABLE `api_sample` ADD `tetracycline_method` varchar(60);
ALTER TABLE `api_sample` ADD `vancomycin` varchar(30);
ALTER TABLE `api_sample` ADD `vancomycin_method` varchar(60);

/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
