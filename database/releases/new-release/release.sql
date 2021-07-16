-- =====================================
-- Remove redundant tables.
-- =====================================

drop table api_affiliation;
drop table refresh_token_refreshtoken;
drop table api_user;
drop table auth_group_permissions;
drop table auth_group;
drop table auth_permission;

--
-- Update the database version
--
CALL update_database_version('???', 'Removed all redundant tables');
