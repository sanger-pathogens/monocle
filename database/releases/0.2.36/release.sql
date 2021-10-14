
-- Add new institutionw

insert into api_institution (name, country, latitude, longitude)
values ('Respiratory and Meningeal Pathogens Research Unit, University of the Witwatersrand', 'South Africa', -26.187832582, 28.024833234);

insert into api_institution (name, country, latitude, longitude)
values ('Pfizer Vaccine Research and Development', 'USA', 41.07514, -74.01978);

insert into api_institution (name, country, latitude, longitude)
values ('McGovern Medical School at UTHealth', 'USA', 29.7124564236886, 95.3973737452179);

insert into api_institution (name, country, latitude, longitude)
values ('G N Gabrichevsky Research Institute for Epidemiology and Microbiology', 'Russia', 55.83742, 37.48922);

insert into api_institution (name, country, latitude, longitude)
values ('Universidad de Buenos Aires', 'Argentina', 34.5998559, 58.373053);

insert into api_institution (name, country, latitude, longitude)
values ('University Hospital Carl Gustav Carus Dresden', 'Gabon', -0.89997, 11.68997);

insert into api_institution (name, country, latitude, longitude)
values ('Iaso Hospital', 'Greece', 37.98394, 23.72831);

insert into api_institution (name, country, latitude, longitude)
values ('University of North Carolina at Chapel Hill', 'Nicaragua', 12.60902, -85.29369);


--
-- Update the database version
--
CALL update_database_version('0.2.36', 'new institutions');
