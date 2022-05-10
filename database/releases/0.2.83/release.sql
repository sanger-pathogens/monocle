# **************************************************************
# Add new institutions in api_institution
# **************************************************************

-- Add new institutions

insert into api_institution (name, country, latitude, longitude)
values ('Istituto Superiore di Sanità', 'Italy', 41.904144, 12.51806);

insert into api_institution (name, country, latitude, longitude)
values ('Toros University', 'Turkey', 36.790048, 34.593931);

--
-- Update the database version
--
CALL update_database_version('0.2.83', 'Add new institutions');
