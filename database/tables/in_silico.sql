# **************************************************************
# The in_silico table.
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
  `lane_id` varchar(256) NOT NULL,
  `cps_type` varchar(256),
  `ST` varchar(256),
  `adhP` varchar(30),
  `pheS` varchar(30),
  `atr` varchar(30),
  `glnA` varchar(30),
  `sdhA` varchar(30),
  `glcK` varchar(30),
  `tkt` varchar(30),
  `twenty_three_S1` varchar(30),
  `twenty_three_S3` varchar(30),
  `CAT` varchar(30),
  `ERMB` varchar(30),
  `ERMT` varchar(30),
  `FOSA` varchar(30),
  `GYRA` varchar(30),
  `LNUB` varchar(30),
  `LSAC` varchar(30),
  `MEFA` varchar(30),
  `MPHC` varchar(30),
  `MSRA` varchar(30),
  `MSRD` varchar(30),
  `PARC` varchar(30),
  `RPOBGBS_1` varchar(30),
  `RPOBGBS_2` varchar(30),
  `RPOBGBS_3` varchar(30),
  `RPOBGBS_4` varchar(30),
  `SUL2` varchar(30),
  `TETB` varchar(30),
  `TETL` varchar(30),
  `TETM` varchar(30),
  `TETO` varchar(30),
  `TETS` varchar(30),
  `ALP1` varchar(30),
  `ALP23` varchar(30),
  `ALPHA` varchar(30),
  `HVGA` varchar(30),
  `PI1` varchar(30),
  `PI2A1` varchar(30),
  `PI2A2` varchar(30),
  `PI2B` varchar(30),
  `RIB` varchar(30),
  `SRR1` varchar(30),
  `SRR2` varchar(30),
  `GYRA_variant` varchar(256),
  `PARC_variant` varchar(256),
  PRIMARY KEY (`lane_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
