

-- Add new institutions
insert into api_institution (name, country, latitude, longitude)
values ('Universidade Federal de Minas Gerais', 'Brazil', -19.869089, -43.966383);

insert into api_institution (name, country, latitude, longitude)
values ('Universidade Estadual de Londrina', 'Brazil', -23.325303, -51.199978);


--
-- Update the database version
--
CALL update_database_version('0.1.52', 'Two new institutions');
