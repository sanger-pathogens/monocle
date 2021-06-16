# **************************************************************
# Monocle database release process changes.
# **************************************************************

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Remove redundant tables
DROP TABLE IF EXISTS `django_content_type`;
DROP TABLE IF EXISTS `django_migrations`;

DROP TABLE IF EXISTS `database_version`;

CREATE TABLE `database_version` (
    `version` varchar(100) NOT NULL,
    `description` varchar(255) NULL,
    `applied` datetime(6) NOT NULL,
    PRIMARY KEY (`version`)
) DEFAULT CHARSET=utf8;

DROP PROCEDURE IF EXISTS `update_database_version`;

DELIMITER //
CREATE PROCEDURE update_database_version(IN in_version varchar(100), IN in_description varchar(255))
BEGIN
    INSERT INTO `database_version` (version, description, applied)
    VALUES (in_version, in_description, NOW());
END //
DELIMITER ;

--
-- Update the database version
--
CALL update_database_version('0.1.49', 'Django retirement');

/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;