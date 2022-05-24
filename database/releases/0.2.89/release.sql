# **************************************************************
# Create gps_in_silico and gps_qc_data tables.
# **************************************************************

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- gps_in_silico table

DROP TABLE IF EXISTS `gps_in_silico`;

CREATE TABLE IF NOT EXISTS `gps_in_silico` (
  `lane_id`	varchar(256) NOT NULL,
  `public_name`	varchar(256) NOT NULL,
  `sample` varchar(30),
  `ERR`	varchar(30),
  `ERS`	varchar(30),
  `no_of_genome` smallint(6) DEFAULT NULL,
  `duplicate` varchar(30),
  `Paper_1`	varchar(30),
  `In_Silico_St` varchar(256),
  `Aroe` varchar(30),
  `Gdh` varchar(30),
  `Gki` varchar(30),
  `Recp` varchar(30),
  `Spi` varchar(30),
  `Xpt` varchar(30),
  `Ddl` varchar(30),
  `country`	varchar(256),
  `Manifest_type` varchar(30),
  `children<5yrs` varchar(30),
  `GPSC_PoPUNK2` varchar(30),
  `GPSC_PoPUNK2__colour` varchar(30),
  `In_Silico_serotype` varchar(30),
  `In_Silico_serotype__colour` varchar(30),
  `PBP1A` varchar(30),
  `PBP2B` varchar(30),
  `PBP2X` varchar(30),
  `WGS_PEN` varchar(30),
  `WGS_PEN_SIR_Meningitis` varchar(30),
  `WGS_PEN_SIR_Nonmeningitis` varchar(30),
  `WGS_AMO` varchar(30),
  `WGS_AMO_SIR` varchar(30),
  `WGS_MER` varchar(30),
  `WGS_MER_SIR` varchar(30),
  `WGS_TAX` varchar(30),
  `WGS_TAX_SIR_Meningitis` varchar(30),
  `WGS_TAX_SIR_Nonmeningitis` varchar(30),
  `WGS_CFT` varchar(30),
  `WGS_CFT_SIR_Meningitis` varchar(30),
  `WGS_CFT_SIR_Nonmeningitis` varchar(30),
  `WGS_CFX` varchar(30),
  `WGS_CFX_SIR` varchar(30),
  `WGS_ERY` varchar(30),
  `WGS_ERY_SIR` varchar(30),
  `WGS_CLI` varchar(30),
  `WGS_CLI_SIR` varchar(30),
  `WGS_SYN` varchar(30),
  `WGS_SYN_SIR` varchar(30),
  `WGS_LZO` varchar(30),
  `WGS_LZO_SIR` varchar(30),
  `WGS_ERY_CLI` varchar(30),
  `WGS_COT` varchar(30),
  `WGS_COT_SIR` varchar(30),
  `WGS_TET` varchar(30),
  `WGS_TET_SIR` varchar(30),
  `WGS_DOX` varchar(30),
  `WGS_DOX_SIR` varchar(30),
  `WGS_LFX` varchar(30),
  `WGS_LFX_SIR` varchar(30),
  `WGS_CHL` varchar(30),
  `WGS_CHL_SIR` varchar(30),
  `WGS_RIF` varchar(30),
  `WGS_RIF_SIR` varchar(30),
  `WGS_VAN` varchar(30),
  `WGS_VAN_SIR` varchar(30),
  `EC` varchar(30),
  `Cot` varchar(30),
  `Tet__autocolour` varchar(30),
  `FQ__autocolour` varchar(30),
  `Other` varchar(30),
  `PBP1A_2B_2X__autocolour` varchar(30),
  `WGS_PEN_SIR_Meningitis__colour` varchar(30),
  `WGS_PEN_SIR_Nonmeningitis__colour` varchar(30),
  `WGS_AMO_SIR__colour` varchar(30),
  `WGS_MER_SIR__colour` varchar(30),
  `WGS_TAX_SIR_Meningitis__colour` varchar(30),
  `WGS_TAX_SIR_Nonmeningitis__colour` varchar(30),
  `WGS_CFT_SIR_Meningitis__colour` varchar(30),
  `WGS_CFT_SIR_Nonmeningitis__colour` varchar(30),
  `WGS_CFX_SIR__colour` varchar(30),
  `WGS_ERY_SIR__colour` varchar(30),
  `WGS_CLI_SIR__colour` varchar(30),
  `WGS_SYN_SIR__colour` varchar(30),
  `WGS_LZO_SIR__colour` varchar(30),
  `WGS_COT_SIR__colour` varchar(30),
  `WGS_TET_SIR__colour` varchar(30),
  `WGS_DOX_SIR__colour` varchar(30),
  `WGS_LFX_SIR__colour` varchar(30),
  `WGS_CHL_SIR__colour` varchar(30),
  `WGS_RIF_SIR__colour` varchar(30),
  `WGS_VAN_SIR__colour` varchar(30),
  `ermB` varchar(30),
  `ermB__colour` varchar(30),
  `mefA` varchar(30),
  `mefA__colour` varchar(30),
  `folA_I100L` varchar(30),
  `folA_I100L__colour` varchar(30),
  `folP__autocolour` varchar(30),
  `cat` varchar(30),
  `cat__colour` varchar(30),
  `PCV7` varchar(30),
  `PCV10` varchar(30),
  `PCV13` varchar(30),
  `PCV15` varchar(30),
  `PCV20` varchar(30),
  `Pneumosil` varchar(30),
  `Published(Y/N)` varchar(30),
  PRIMARY KEY (`lane_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- gps_qc_data table

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


-- Update the database version
CALL update_database_version('0.2.89', 'Create gps_in_silico and gps_qc_data tables');


/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;