# **************************************************************
# The gps_qc_data table.
# **************************************************************

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP TABLE IF EXISTS `gps_qc_data`;

CREATE TABLE IF NOT EXISTS `gps_qc_data` (
  `lane_id`	varchar(256) NOT NULL,
  `sample_name`	varchar(256) NOT NULL,
  `sample_accession` varchar(256) NOT NULL,
  `lane_accession` varchar(256) NOT NULL,
  `supplier_name` varchar(256),
  `public_name` varchar(256) NOT NULL,
  `Streptococcus_pneumoniae` decimal(3,2),
  `total_length` int(11),
  `No_contigs` int(11),
  `genome_covered` decimal(3,2),
  `depth_of_coverage` decimal(3,2),
  `X_Het_SNPs_Total_No_of_SNPs` decimal(3,2),
  `qc` varchar(30),
  `Hetsites_50bp` int(11),
PRIMARY KEY (`lane_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
