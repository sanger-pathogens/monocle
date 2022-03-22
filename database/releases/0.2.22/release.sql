
-- Add new institution

insert into api_institution (name, country, latitude, longitude)
values ('Universidad de Caldas', 'Colombia', 5.057045, -75.492802);

--
-- Update the database version
--
CALL update_database_version('0.2.22', 'new institution');
