-- Database changes required for the first metadata code release

-- Remove the current samples, so we can reload
delete from api_sample;

-- Update Hong Kong country name
update api_institution set country = 'China [Hong Kong]' where name = 'The Chinese University of Hong Kong';

-- Add new institution
insert into api_institution (name, country, latitude, longitude)
values ('Laboratório Central do Estado do Paraná', 'Brazil', -25.42537, -49.25920);

-- This institution will no longer be used
delete from api_institution where name = 'Ministry of Health, Central laboratories';
