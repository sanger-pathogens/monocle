# **************************************************************
# The gps_sample table.
# **************************************************************

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP TABLE IF EXISTS `gps_sample`;

CREATE TABLE `gps_sample` (
  # THIS TABLE DEFINITION IS AUTO-GENERATED BY config/update_config_files.py, DO NOT EDIT MANUALLY!
  `sanger_sample_id` VARCHAR(256) NOT NULL,
  `sample_name` VARCHAR(256) NOT NULL,
  `public_name` VARCHAR(256) NOT NULL,
  `study_name` VARCHAR(600),
  `submitting_institution` VARCHAR(256) NOT NULL,
  `selection_random` VARCHAR(10) DEFAULT NULL,
  `continent` VARCHAR(90),
  `country` VARCHAR(90),
  `region` VARCHAR(90),
  `city` VARCHAR(200),
  `facility_where_collected` VARCHAR(256) DEFAULT NULL,
  `month_collection` VARCHAR(10) DEFAULT NULL,
  `year_collection` SMALLINT(4),
  `gender` VARCHAR(10) DEFAULT NULL,
  `age_years` VARCHAR(30),
  `age_months` SMALLINT(10),
  `age_days` SMALLINT(10),
  `clinical_manifestation` VARCHAR(256),
  `source` VARCHAR(100),
  `HIV_status` VARCHAR(10),
  `underlying_conditions` VARCHAR(256),
  `phenotypic_serotype_method` VARCHAR(100),
  `phenotypic_serotype` VARCHAR(100),
  `sequence_type` VARCHAR(256),
  `aroE` SMALLINT(3),
  `gdh` SMALLINT(3),
  `gki` SMALLINT(3),
  `recP` SMALLINT(3),
  `spi` VARCHAR(30),
  `xpt` SMALLINT(4),
  `ddl` SMALLINT(3),
  `AST_method_penicillin` VARCHAR(60),
  `penicillin` VARCHAR(30),
  `AST_method_amoxicillin` VARCHAR(60),
  `amoxicillin` VARCHAR(30),
  `AST_method_cefotaxime` VARCHAR(60),
  `cefotaxime` VARCHAR(30),
  `AST_method_ceftriaxone` VARCHAR(60),
  `ceftriaxone` VARCHAR(30),
  `AST_method_cefuroxime` VARCHAR(60),
  `cefuroxime` VARCHAR(30),
  `AST_method_meropenem` VARCHAR(60),
  `meropenem` VARCHAR(30),
  `AST_method_erythromycin` VARCHAR(60),
  `erythromycin` VARCHAR(30),
  `AST_method_clindamycin` VARCHAR(60),
  `clindamycin` VARCHAR(30),
  `AST_method_trim_sulfa` VARCHAR(60),
  `trim_sulfa` VARCHAR(30),
  `AST_method_vancomycin` VARCHAR(60),
  `vancomycin` VARCHAR(30),
  `AST_method_linezolid` VARCHAR(60),
  `linezolid` VARCHAR(30),
  `AST_method_ciprofloxacin` VARCHAR(60),
  `ciprofloxacin` VARCHAR(30),
  `AST_method_chloramphenicol` VARCHAR(60),
  `chloramphenicol` VARCHAR(30),
  `AST_method_tetracycline` VARCHAR(60),
  `tetracycline` VARCHAR(30),
  `AST_method_levofloxacin` VARCHAR(60),
  `levofloxacin` VARCHAR(30),
  `AST_method_synercid` VARCHAR(60),
  `synercid` VARCHAR(30),
  `AST_method_rifampin` VARCHAR(60),
  `rifampin` VARCHAR(30),
  `comments` VARCHAR(256),
  `latitude` DECIMAL(9,6) CHECK (latitude>=-180 AND latitude<=180),
  `longitude` DECIMAL(9,6) CHECK (longitude>=-180 AND longitude<=180),
  `resolution` SMALLINT(1),
  `vaccine_period` VARCHAR(30),
  `intro_year` SMALLINT(4),
  `PCV_type` VARCHAR(100),
  # END OF AUTO_GENERATED SECTION
  PRIMARY KEY (`public_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
