

-- Add new institutions
insert into api_institution (name, country, latitude, longitude)
values ('Fiocruz Rondônia', 'Brazil', -8.761944, -63.903889);

insert into api_institution (name, country, latitude, longitude)
values ('Universidade Estadual Paulista', 'Brazil', -22.8172, -47.0694);

insert into api_institution (name, country, latitude, longitude)
values ('Universidade Federal de Lavras', 'Brazil', -21.245, -45);

insert into api_institution (name, country, latitude, longitude)
values ('Universidade Federal Fluminense', 'Brazil', -22.904167, -43.116667);

insert into api_institution (name, country, latitude, longitude)
values ('Ulm University', 'Egypt', 26.42231, 29.227089);

insert into api_institution (name, country, latitude, longitude)
values ('St George''s, University of London', 'UK', 51.426944, -0.174722);

insert into api_institution (name, country, latitude, longitude)
values ('Public Health England', 'UK', 51.5018, -0.1091);


--
-- Update the database version
--
CALL update_database_version('0.2.5', '7 new institutions');
