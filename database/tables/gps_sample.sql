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
  `study_name` varchar(256) NOT NULL,
  `selection_random` varchar(256) NOT NULL,
  `country` varchar(256) NOT NULL,
  `region` varchar(256) NOT NULL,
  `city` varchar(256) NOT NULL,
  `facility_where_collected` varchar(256) NOT NULL,
  `submitting_institution` varchar(256) NOT NULL,
  `month_collection` varchar(256) NOT NULL,
  `year_collection` int,
  `gender_m/f` varchar(256) NOT NULL,
  `age_years` int,
  `age_months` varchar(256) NOT NULL,
  `age_days` varchar(256) NOT NULL,
  `clinical_manifestation` varchar(256) NOT NULL,
  `source` varchar(256) NOT NULL,
  `HIV_status` varchar(256) NOT NULL,
  `underlying_conditions` varchar(256) NOT NULL,
  `phenotypic_serotype_method` varchar(256) NOT NULL,
  `phenotypic_serotype` varchar(256) NOT NULL,
  `sequence_type` varchar(256) NOT NULL,
  `aroe` varchar(256) NOT NULL,
  `gdh` varchar(256) NOT NULL,
  `gki` varchar(256) NOT NULL,
  `recp` varchar(256) NOT NULL,
  `spi` varchar(256) NOT NULL,
  `xpt` varchar(256) NOT NULL,
  `ddl` varchar(256) NOT NULL,
  `AST_method_Penicillin` varchar(256) NOT NULL,
  `Penicillin` varchar(256) NOT NULL,
  `AST_method_Amoxicillin` varchar(256) NOT NULL,
  `Amoxicillin` varchar(256) NOT NULL,
  `AST_method_Cefotaxime` varchar(256) NOT NULL,
  `cefotaxime` varchar(256) NOT NULL,
  `AST_method_Ceftriaxone` varchar(256) NOT NULL,
  `ceftriaxone` varchar(256) NOT NULL,
  `AST_method_cefuroxime` varchar(256) NOT NULL,
  `cefuroxime` varchar(256) NOT NULL,
  `AST_method_meropenem` varchar(256) NOT NULL,
  `Meropenem` varchar(256) NOT NULL,
  `AST_method_erythromycin` varchar(256) NOT NULL,
  `erythromycin` varchar(256) NOT NULL,
  `AST_method_clindamycin` varchar(256) NOT NULL,
  `clindamycin` varchar(256) NOT NULL,
  `AST_method_Trim/Sulfa` varchar(256) NOT NULL,
  `trim/sulfa` varchar(256) NOT NULL,
  `AST_method_vancomycin` varchar(256) NOT NULL,
  `vancomycin` varchar(256) NOT NULL,
  `AST_method_linezolid` varchar(256) NOT NULL,
  `linezolid` varchar(256) NOT NULL,
  `AST_method_Ciprofloxacin` varchar(256) NOT NULL,
  `ciprofloxacin` varchar(256) NOT NULL,
  `AST_method_chloramphenicol` varchar(256) NOT NULL,
  `chloramphenicol` varchar(256) NOT NULL,
  `AST_method_tetracycline` varchar(256) NOT NULL,
  `tetracycline` varchar(256) NOT NULL,
  `AST_method_levofloxacin` varchar(256) NOT NULL,
  `levofloxacin` varchar(256) NOT NULL,
  `AST_method_synercid` varchar(256) NOT NULL,
  `synercid` varchar(256) NOT NULL,
  `AST_method_rifampin` varchar(256) NOT NULL,
  `rifampin` varchar(256) NOT NULL,
  `comments` varchar(256) NOT NULL,
  `vaccine_period` varchar(256) NOT NULL,
  `intro_year` int,
  `PCV_type` varchar(256) NOT NULL,
  `latitude` real,
  `longitude` real,
  `resolution` int,
  PRIMARY KEY (`public_name`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
