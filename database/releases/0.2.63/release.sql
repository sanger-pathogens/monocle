--
-- Change column names to match spreadheet headings/API keys
--


ALTER TABLE api_sample CHANGE submitting_institution_id  submitting_institution  varchar(256);
ALTER TABLE api_sample CHANGE birthweight_gram           birth_weight_gram       int(11);
ALTER TABLE api_sample CHANGE sample_id                  sanger_sample_id        varchar(256);

--
-- Update the database version
--
CALL update_database_version('0.2.63', 'change db columns to match names used in metadata spreadsheets and API keys');
