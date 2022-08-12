# **************************************************************
# Fix v 3.4 GPS tables
# **************************************************************

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- fix gps_in_silico table

DROP TABLE IF EXISTS `gps_in_silico`;

CREATE TABLE IF NOT EXISTS `gps_in_silico` (
  # THIS TABLE DEFINITION IS AUTO-GENERATED BY config/update_config_files.py, DO NOT EDIT MANUALLY!
  `lane_id` VARCHAR(256) NOT NULL,
  `sample` VARCHAR(256) NOT NULL,
  `public_name` VARCHAR(256) NOT NULL,
  `ERR` VARCHAR(256),
  `ERS` VARCHAR(256),
  `no_of_genome` SMALLINT(6) DEFAULT NULL,
  `duplicate` VARCHAR(30),
  `Paper_1` VARCHAR(30),
  `In_Silico_St` VARCHAR(20) NOT NULL,
  `aroE` VARCHAR(30),
  `gdh` VARCHAR(30),
  `gki` VARCHAR(30),
  `recP` VARCHAR(30),
  `spi` VARCHAR(30),
  `xpt` VARCHAR(30),
  `ddl` VARCHAR(30),
  `country` VARCHAR(256),
  `Continent` VARCHAR(256),
  `Manifest_type` VARCHAR(30),
  `children_under_5yrs` VARCHAR(30),
  `GPSC` SMALLINT(4),
  `GPSC__colour` VARCHAR(30),
  `In_silico_serotype` VARCHAR(30),
  `In_silico_serotype__colour` VARCHAR(30),
  `pbp1a` VARCHAR(30),
  `pbp2b` VARCHAR(30),
  `pbp2x` VARCHAR(30),
  `WGS_PEN` VARCHAR(30),
  `WGS_PEN_SIR_Meningitis` VARCHAR(30),
  `WGS_PEN_SIR_Nonmeningitis` VARCHAR(30),
  `WGS_AMO` VARCHAR(30),
  `WGS_AMO_SIR` VARCHAR(30),
  `WGS_MER` VARCHAR(30),
  `WGS_MER_SIR` VARCHAR(30),
  `WGS_TAX` VARCHAR(30),
  `WGS_TAX_SIR_Meningitis` VARCHAR(30),
  `WGS_TAX_SIR_Nonmeningitis` VARCHAR(30),
  `WGS_CFT` VARCHAR(30),
  `WGS_CFT_SIR_Meningitis` VARCHAR(30),
  `WGS_CFT_SIR_Nonmeningitis` VARCHAR(30),
  `WGS_CFX` VARCHAR(30),
  `WGS_CFX_SIR` VARCHAR(30),
  `WGS_ERY` VARCHAR(30),
  `WGS_ERY_SIR` VARCHAR(30),
  `WGS_CLI` VARCHAR(30),
  `WGS_CLI_SIR` VARCHAR(30),
  `WGS_SYN` VARCHAR(30),
  `WGS_SYN_SIR` VARCHAR(30),
  `WGS_LZO` VARCHAR(30),
  `WGS_LZO_SIR` VARCHAR(30),
  `WGS_ERY_CLI` VARCHAR(30),
  `WGS_COT` VARCHAR(30),
  `WGS_COT_SIR` VARCHAR(30),
  `WGS_TET` VARCHAR(30),
  `WGS_TET_SIR` VARCHAR(30),
  `WGS_DOX` VARCHAR(30),
  `WGS_DOX_SIR` VARCHAR(30),
  `WGS_LFX` VARCHAR(30),
  `WGS_LFX_SIR` VARCHAR(30),
  `WGS_CHL` VARCHAR(30),
  `WGS_CHL_SIR` VARCHAR(30),
  `WGS_RIF` VARCHAR(30),
  `WGS_RIF_SIR` VARCHAR(30),
  `WGS_VAN` VARCHAR(30),
  `WGS_VAN_SIR` VARCHAR(30),
  `EC` VARCHAR(60),
  `Cot` VARCHAR(100),
  `Tet__autocolour` VARCHAR(30),
  `FQ__autocolour` VARCHAR(400),
  `Other` VARCHAR(256),
  `PBP1A_2B_2X__autocolour` VARCHAR(30),
  `WGS_PEN_SIR_Meningitis__colour` VARCHAR(30),
  `WGS_PEN_SIR_Nonmeningitis__colour` VARCHAR(30),
  `WGS_AMO_SIR__colour` VARCHAR(30),
  `WGS_MER_SIR__colour` VARCHAR(30),
  `WGS_TAX_SIR_Meningitis__colour` VARCHAR(30),
  `WGS_TAX_SIR_Nonmeningitis__colour` VARCHAR(30),
  `WGS_CFT_SIR_Meningitis__colour` VARCHAR(30),
  `WGS_CFT_SIR_Nonmeningitis__colour` VARCHAR(30),
  `WGS_CFX_SIR__colour` VARCHAR(30),
  `WGS_ERY_SIR__colour` VARCHAR(30),
  `WGS_CLI_SIR__colour` VARCHAR(30),
  `WGS_SYN_SIR__colour` VARCHAR(30),
  `WGS_LZO_SIR__colour` VARCHAR(30),
  `WGS_COT_SIR__colour` VARCHAR(30),
  `WGS_TET_SIR__colour` VARCHAR(30),
  `WGS_DOX_SIR__colour` VARCHAR(30),
  `WGS_LFX_SIR__colour` VARCHAR(30),
  `WGS_CHL_SIR__colour` VARCHAR(30),
  `WGS_RIF_SIR__colour` VARCHAR(30),
  `WGS_VAN_SIR__colour` VARCHAR(30),
  `ermB` VARCHAR(30),
  `ermB__colour` VARCHAR(30),
  `mefA` VARCHAR(30),
  `mefA__colour` VARCHAR(30),
  `folA_I100L` VARCHAR(30),
  `folA_I100L__colour` VARCHAR(30),
  `folP__autocolour` VARCHAR(30),
  `cat` VARCHAR(30),
  `cat__colour` VARCHAR(30),
  `PCV7` VARCHAR(30),
  `PCV10` VARCHAR(30),
  `PCV13` VARCHAR(30),
  `PCV15` VARCHAR(30),
  `PCV20` VARCHAR(30),
  `Pneumosil` VARCHAR(30),
  `Published` VARCHAR(30),
  # END OF AUTO_GENERATED SECTION
  PRIMARY KEY (`lane_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- fix gps_sample table

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
  `age_months` DECIMAL(5,2),
  `age_days` SMALLINT(4),
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
  `latitude` DECIMAL(13,10) CHECK (latitude>=-180 AND latitude<=180),
  `longitude` DECIMAL(13,10) CHECK (longitude>=-180 AND longitude<=180),
  `resolution` SMALLINT(1),
  `vaccine_period` VARCHAR(30),
  `intro_year` SMALLINT(4),
  `PCV_type` VARCHAR(100),
  # END OF AUTO_GENERATED SECTION
  PRIMARY KEY (`public_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- Update the database version
CALL update_database_version('0.7.4', 'Fix v 3.4 GPS tables');


/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
