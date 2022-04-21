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
  `sample_name` varchar(256) NOT NULL,
  `public_name` varchar(256) NOT NULL,
  `study_name` varchar(600),
  `selection_random` varchar(256),
  `country` varchar(90),
  `region` varchar(90),
  `city` varchar(200),
  `facility_where_collected` varchar(256),
  `submitting_institution` varchar(256) NOT NULL,
  `month_collection` varchar(10) DEFAULT NULL,
  `year_collection` smallint(6) DEFAULT NULL,
  `gender_m/f` varchar(10),
  `age_years` int(11) DEFAULT NULL,
  `age_months` int(11) DEFAULT NULL,
  `age_days` int(11) DEFAULT NULL,
  `clinical_manifestation` varchar(256),
  `source` varchar(100),
  `HIV_status` varchar(10),
  `underlying_conditions` varchar(256),
  `phenotypic_serotype_method` varchar(100),
  `phenotypic_serotype` varchar(100),
  `sequence_type` varchar(256),
  `aroe` varchar(100),
  `gdh` varchar(100),
  `gki` varchar(100),
  `recp` varchar(100),
  `spi` varchar(100),
  `xpt` varchar(100),
  `ddl` varchar(100),
  `AST_method_penicillin` varchar(60),
  `penicillin` varchar(30),
  `AST_method_amoxicillin` varchar(60),
  `amoxicillin` varchar(30),
  `AST_method_cefotaxime` varchar(60),
  `cefotaxime` varchar(30),
  `AST_method_ceftriaxone` varchar(60),
  `ceftriaxone` varchar(30),
  `AST_method_cefuroxime` varchar(60),
  `cefuroxime` varchar(30),
  `AST_method_meropenem` varchar(60),
  `meropenem` varchar(30),
  `AST_method_erythromycin` varchar(60),
  `erythromycin` varchar(30),
  `AST_method_clindamycin` varchar(60),
  `clindamycin` varchar(30),
  `AST_method_trim/sulfa` varchar(60),
  `trim/sulfa` varchar(30),
  `AST_method_vancomycin` varchar(60),
  `vancomycin` varchar(30),
  `AST_method_linezolid` varchar(60),
  `linezolid` varchar(30),
  `AST_method_ciprofloxacin` varchar(60),
  `ciprofloxacin` varchar(30),
  `AST_method_chloramphenicol` varchar(60),
  `chloramphenicol` varchar(30),
  `AST_method_tetracycline` varchar(60),
  `tetracycline` varchar(30),
  `AST_method_levofloxacin` varchar(60),
  `levofloxacin` varchar(30),
  `AST_method_synercid` varchar(60),
  `synercid` varchar(30),
  `AST_method_rifampin` varchar(60),
  `rifampin` varchar(30),
  `comments` varchar(256),
  `vaccine_period` varchar(200),
  `intro_year` smallint(6) DEFAULT NULL,
  `PCV_type` varchar(100),
  `resolution` smallint(4),
  PRIMARY KEY (`public_name`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
