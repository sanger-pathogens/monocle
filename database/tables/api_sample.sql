# **************************************************************
# The api_sample table.
# **************************************************************

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP TABLE IF EXISTS `api_sample`;

CREATE TABLE `api_sample` (
  # THIS TABLE DEFINITION IS AUTO-GENERATED BY update_config_files.py, DO NOT EDIT MANUALLY!
  `public_name` VARCHAR(256) NOT NULL,
  `sanger_sample_id` VARCHAR(256) NOT NULL,
  `supplier_sample_name` VARCHAR(20) NOT NULL,
  `lane_id` VARCHAR(256) DEFAULT NULL,
  `study_name` VARCHAR(600) DEFAULT NULL,
  `study_ref` VARCHAR(400) DEFAULT NULL,
  `submitting_institution` VARCHAR(256) NOT NULL,
  `selection_random` VARCHAR(10) DEFAULT NULL,
  `country` VARCHAR(90) DEFAULT NULL,
  `county_state` VARCHAR(200) DEFAULT NULL,
  `city` VARCHAR(200) DEFAULT NULL,
  `collection_year` smallint(6) DEFAULT NULL,
  `collection_month` smallint(6) DEFAULT NULL,
  `collection_day` smallint(6) DEFAULT NULL,
  `host_species` VARCHAR(100) DEFAULT NULL,
  `gender` VARCHAR(10) DEFAULT NULL,
  `age_group` VARCHAR(30) DEFAULT NULL,
  `age_years` int(11) DEFAULT NULL,
  `age_months` int(11) DEFAULT NULL,
  `age_weeks` int(11) DEFAULT NULL,
  `age_days` int(11) DEFAULT NULL,
  `host_status` VARCHAR(256) DEFAULT NULL,
  `disease_type` VARCHAR(100) DEFAULT NULL,
  `disease_onset` VARCHAR(10) DEFAULT NULL,
  `isolation_source` VARCHAR(100) DEFAULT NULL,
  `infection_during_pregnancy` VARCHAR(10) DEFAULT NULL,
  `maternal_infection_type` VARCHAR(100) DEFAULT NULL,
  `gestational_age_weeks` smallint(6) DEFAULT NULL,
  `birth_weight_gram` int(11) DEFAULT NULL,
  `apgar_score` smallint(6) DEFAULT NULL,
  `serotype` VARCHAR(7) DEFAULT NULL,
  `serotype_method` VARCHAR(100) DEFAULT NULL,
  `ceftizoxime` VARCHAR(30) DEFAULT NULL,
  `ceftizoxime_method` VARCHAR(60) DEFAULT NULL,
  `cefoxitin` VARCHAR(30) DEFAULT NULL,
  `cefoxitin_method` VARCHAR(60) DEFAULT NULL,
  `cefotaxime` VARCHAR(30) DEFAULT NULL,
  `cefotaxime_method` VARCHAR(60) DEFAULT NULL,
  `cefazolin` VARCHAR(30) DEFAULT NULL,
  `cefazolin_method` VARCHAR(60) DEFAULT NULL,
  `ampicillin` VARCHAR(30) DEFAULT NULL,
  `ampicillin_method` VARCHAR(60) DEFAULT NULL,
  `penicillin` VARCHAR(30) DEFAULT NULL,
  `penicillin_method` VARCHAR(60) DEFAULT NULL,
  `erythromycin` VARCHAR(30) DEFAULT NULL,
  `erythromycin_method` VARCHAR(60) DEFAULT NULL,
  `clindamycin` VARCHAR(30) DEFAULT NULL,
  `clindamycin_method` VARCHAR(60) DEFAULT NULL,
  `tetracycline` VARCHAR(30) DEFAULT NULL,
  `tetracycline_method` VARCHAR(60) DEFAULT NULL,
  `levofloxacin` VARCHAR(30) DEFAULT NULL,
  `levofloxacin_method` VARCHAR(60) DEFAULT NULL,
  `ciprofloxacin` VARCHAR(30) DEFAULT NULL,
  `ciprofloxacin_method` VARCHAR(60) DEFAULT NULL,
  `daptomycin` VARCHAR(30) DEFAULT NULL,
  `daptomycin_method` VARCHAR(60) DEFAULT NULL,
  `vancomycin` VARCHAR(30) DEFAULT NULL,
  `vancomycin_method` VARCHAR(60) DEFAULT NULL,
  `linezolid` VARCHAR(30) DEFAULT NULL,
  `linezolid_method` VARCHAR(60) DEFAULT NULL,
  # END OF AUTO_GENERATED SECTION
  PRIMARY KEY (`sanger_sample_id`),
  KEY `api_sample_submitting_institution_fk` (`submitting_institution`),
  CONSTRAINT `api_sample_submitting_institution_fk` FOREIGN KEY (`submitting_institution`) REFERENCES `api_institution` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
