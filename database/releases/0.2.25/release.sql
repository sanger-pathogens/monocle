# **************************************************************
# The in_silico table.
# **************************************************************

DROP TABLE IF EXISTS `in_silico`;

CREATE TABLE `in_silico` (
  `lane_id` varchar(256) NOT NULL,
  `gbs_typer_serotype` varchar(256),
  `MLST` varchar(256),
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
CALL update_database_version('0.2.25', 'Drop and create new in silico table where all columns are type varchar');
