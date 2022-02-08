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
  `lane_id` varchar(256) DEFAULT NULL,
  `sanger_sample_id` varchar(256) NOT NULL,
  `public_name` varchar(256) NOT NULL,
  `host_status` varchar(256) DEFAULT NULL,
  `serotype` varchar(7) DEFAULT NULL,
  `submitting_institution` varchar(256) NOT NULL,
  `age_days` int(11) DEFAULT NULL,
  `age_group` varchar(30),
  `age_months` int(11) DEFAULT NULL,
  `age_weeks` int(11) DEFAULT NULL,
  `age_years` int(11) DEFAULT NULL,
  `ampicillin` varchar(30),
  `ampicillin_method` varchar(60),
  `apgar_score` smallint(6) DEFAULT NULL,
  `birth_weight_gram` int(11) DEFAULT NULL,
  `cefazolin` varchar(30),
  `cefazolin_method` varchar(60),
  `cefotaxime` varchar(30),
  `cefotaxime_method` varchar(60),
  `cefoxitin` varchar(30),
  `cefoxitin_method` varchar(60),
  `ceftizoxime` varchar(30),
  `ceftizoxime_method` varchar(60),
  `ciprofloxacin` varchar(30),
  `ciprofloxacin_method` varchar(60),
  `city` varchar(200),
  `clindamycin` varchar(30),
  `clindamycin_method` varchar(60),
  `collection_day` smallint(6) DEFAULT NULL,
  `collection_month` smallint(6) DEFAULT NULL,
  `collection_year` smallint(6) DEFAULT NULL,
  `country` varchar(90),
  `county_state` varchar(200),
  `daptomycin` varchar(30),
  `daptomycin_method` varchar(60),
  `disease_onset` varchar(10),
  `disease_type` varchar(100),
  `erythromycin` varchar(30),
  `erythromycin_method` varchar(60),
  `gender` varchar(10),
  `gestational_age_weeks` smallint(6) DEFAULT NULL,
  `host_species` varchar(100),
  `infection_during_pregnancy` varchar(10),
  `isolation_source` varchar(100),
  `levofloxacin` varchar(30),
  `levofloxacin_method` varchar(60),
  `linezolid` varchar(30),
  `linezolid_method` varchar(60),
  `maternal_infection_type` varchar(100),
  `penicillin` varchar(30),
  `penicillin_method` varchar(60),
  `selection_random` varchar(10),
  `serotype_method` varchar(100),
  `study_name` varchar(600),
  `study_ref` varchar(400),
  `supplier_sample_name` varchar(256) NOT NULL,
  `tetracycline` varchar(30),
  `tetracycline_method` varchar(60),
  `vancomycin` varchar(30),
  `vancomycin_method` varchar(60),
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
