# **************************************************************
# Update JUNO in_silico table
# **************************************************************

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP TABLE IF EXISTS `in_silico`;

CREATE TABLE `in_silico` (
  # THIS TABLE DEFINITION IS AUTO-GENERATED BY config/update_config_files.py, DO NOT EDIT MANUALLY!
  `lane_id` VARCHAR(256) NOT NULL,
  `cps_type` VARCHAR(20),
  `ST` VARCHAR(10),
  `adhP` VARCHAR(10),
  `pheS` VARCHAR(10),
  `atr` VARCHAR(10),
  `glnA` VARCHAR(10),
  `sdhA` VARCHAR(10),
  `glcK` VARCHAR(10),
  `tkt` VARCHAR(10),
  `AAC6APH2` VARCHAR(10),
  `ANT6IA` VARCHAR(10),
  `APH3III` VARCHAR(10),
  `AADE` VARCHAR(10),
  `CATPC194` VARCHAR(10),
  `CATQ` VARCHAR(10),
  `ERMA` VARCHAR(10),
  `ERMB` VARCHAR(10),
  `ERMT` VARCHAR(10),
  `LNUB` VARCHAR(10),
  `LNUC` VARCHAR(10),
  `LSAC` VARCHAR(10),
  `LSAE` VARCHAR(10),
  `MEFA` VARCHAR(10),
  `MSRD` VARCHAR(10),
  `TETB` VARCHAR(10),
  `TETL` VARCHAR(10),
  `TETM` VARCHAR(10),
  `TETW` VARCHAR(10),
  `TETO` VARCHAR(10),
  `TETS` VARCHAR(10),
  `TETO32O` VARCHAR(10),
  `TETOW` VARCHAR(10),
  `TETOW32O` VARCHAR(10),
  `TETOW32OWO` VARCHAR(10),
  `TETOWO` VARCHAR(10),
  `TETSM` VARCHAR(10),
  `TETW32O` VARCHAR(10),
  `ALP1` VARCHAR(10),
  `ALP23` VARCHAR(10),
  `ALPHA` VARCHAR(10),
  `HVGA` VARCHAR(10),
  `PI1` VARCHAR(10),
  `PI2A1` VARCHAR(10),
  `PI2A2` VARCHAR(10),
  `PI2B` VARCHAR(10),
  `RIB` VARCHAR(10),
  `SRR1` VARCHAR(10),
  `SRR2` VARCHAR(10),
  `twenty_three_S1_variant` VARCHAR(10),
  `twenty_three_S3_variant` VARCHAR(10),
  `GYRA_variant` VARCHAR(10),
  `PARC_variant` VARCHAR(10),
  `TYPER_PIPELINE_VERSION` VARCHAR(10) NOT NULL,
  # END OF AUTO_GENERATED SECTION
  PRIMARY KEY (`lane_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- Update the database version
CALL update_database_version('0.9.0', 'Update JUNO in_silico table');


/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
