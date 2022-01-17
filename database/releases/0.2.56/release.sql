DROP TABLE IF EXISTS `qc_data`;

CREATE TABLE `qc_data` (
  `lane_id` varchar(256) NOT NULL,
  `rel_abun_sa` DECIMAL(5,2) UNSIGNED,
  # if mysql 8, prefer:
  # `rel_abun_sa` DECIMAL(5,2) CHECK (rel_abun_sa>=0 AND rel_abun_sa<=100),
  PRIMARY KEY (`lane_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CALL update_database_version('0.2.56', 'Drop and create new QC data table.');
