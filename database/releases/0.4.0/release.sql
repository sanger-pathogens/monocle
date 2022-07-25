ALTER TABLE api_sample DROP FOREIGN KEY api_sample_submitting_instituti_7e1c7c4d_fk_api_insti;

DROP TABLE IF EXISTS api_institution;


-- Convert institution names to institution keys for `submitting_institution` column of `api_sample` table.UPDATE api_sample SET submitting_institution = 'CDCGPS' WHERE submitting_institution = 'CDC (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'EmoUniGPS' WHERE submitting_institution = 'Emory University (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'MalLivWelTruGPS' WHERE submitting_institution = 'Malawi Liverpool Wellcome Trust (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'MRCUniTheGamGPS' WHERE submitting_institution = 'MRC Unit The Gambia (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'NICGPS' WHERE submitting_institution = 'NICD (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'ANLGPS' WHERE submitting_institution = 'ANLIS (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'CHRGPS' WHERE submitting_institution = 'CHRF (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'InsAdoLutGPS' WHERE submitting_institution = 'Institute Adolfo Lutz (IAL) (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'TheRepResAndPra' WHERE submitting_institution = 'The Republican Research And Practical Center For Epidemiology And Microbiology (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'HosSanJoaDeDeu' WHERE submitting_institution = 'Hospital Sant Joan De Deu (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'CNRGPS' WHERE submitting_institution = 'CNRP/ACTIV (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'TheUniOfHonKon' WHERE submitting_institution = 'The University Of Hong Kong (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'TemStrChiHosGPS' WHERE submitting_institution = 'Temple Street Childrens Hospital (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'SorUniMedCenGPS' WHERE submitting_institution = 'Soroka University Medical Center (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'KemInsOfMedSci' WHERE submitting_institution = 'Kempegowda Institute Of Medical Sciences (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'CamOxfMedResUni' WHERE submitting_institution = 'Cambodia Oxford Medical Research Unit (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'FacOfMedAndPha' WHERE submitting_institution = 'Faculty Of Medicine And Pharmacy Of Casablanca (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'UniOfSouGPS' WHERE submitting_institution = 'University Of Southampton (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'UniOfNebMedCen' WHERE submitting_institution = 'University Of Nebraska Medical Center (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'OxfVacGroGPS' WHERE submitting_institution = 'Oxford Vaccine Group (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'PNGGPS' WHERE submitting_institution = 'PNGIMR (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'NatMedInsGPS' WHERE submitting_institution = 'National Medicines Institute (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'MGRGPS' WHERE submitting_institution = 'MGRIEM (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'NatLabOfHeaEnv' WHERE submitting_institution = 'National Laboratory Of Health Environment And Food (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'AMPGPS' WHERE submitting_institution = 'AMP (Public GPS samples)';

UPDATE api_sample SET submitting_institution = 'ShoGPS' WHERE submitting_institution = 'Shoklo-Malaria-Research-Unit (Public GPS samples)';


-- Convert institution names to institution keys for `submitting_institution` column of `gps_sample` table.UPDATE gps_sample SET submitting_institution = 'WelSanIns' WHERE submitting_institution = 'Wellcome Sanger Institute';

UPDATE gps_sample SET submitting_institution = 'CentDisCont' WHERE submitting_institution = 'Centers for Disease Control and Prevention';

UPDATE gps_sample SET submitting_institution = 'UlmUni' WHERE submitting_institution = 'Ulm University';

UPDATE gps_sample SET submitting_institution = 'LabCenEstPar' WHERE submitting_institution = 'Laboratório Central do Estado do Paraná';

UPDATE gps_sample SET submitting_institution = 'MinHeaCenLab' WHERE submitting_institution = 'Ministry of Health, Central Laboratories';

UPDATE gps_sample SET submitting_institution = 'TheChiUniHonKon' WHERE submitting_institution = 'The Chinese University of Hong Kong';

UPDATE gps_sample SET submitting_institution = 'UniFedRioJan' WHERE submitting_institution = 'Universidade Federal do Rio de Janeiro';

UPDATE gps_sample SET submitting_institution = 'UniEstLon' WHERE submitting_institution = 'Universidade Estadual de Londrina';

UPDATE gps_sample SET submitting_institution = 'UniFedMinGer' WHERE submitting_institution = 'Universidade Federal de Minas Gerais';

UPDATE gps_sample SET submitting_institution = 'FioRon' WHERE submitting_institution = 'Fiocruz Rondônia';

UPDATE gps_sample SET submitting_institution = 'UniEstPau' WHERE submitting_institution = 'Universidade Estadual Paulista';

UPDATE gps_sample SET submitting_institution = 'UniFedLav' WHERE submitting_institution = 'Universidade Federal de Lavras';

UPDATE gps_sample SET submitting_institution = 'UniFedFlu' WHERE submitting_institution = 'Universidade Federal Fluminense';

UPDATE gps_sample SET submitting_institution = 'StGeoUniLon' WHERE submitting_institution = 'St George''s, University of London';

UPDATE gps_sample SET submitting_institution = 'PubHeaEng' WHERE submitting_institution = 'Public Health England';

UPDATE gps_sample SET submitting_institution = 'UniCal' WHERE submitting_institution = 'Universidad de Caldas';

UPDATE gps_sample SET submitting_institution = 'ResMenPatResUni' WHERE submitting_institution = 'Respiratory and Meningeal Pathogens Research Unit, University of the Witwatersrand';

UPDATE gps_sample SET submitting_institution = 'PfiVacResDev' WHERE submitting_institution = 'Pfizer Vaccine Research and Development';

UPDATE gps_sample SET submitting_institution = 'McGMedSchUTH' WHERE submitting_institution = 'McGovern Medical School at UTHealth';

UPDATE gps_sample SET submitting_institution = 'GNGabResInsEpi' WHERE submitting_institution = 'G N Gabrichevsky Research Institute for Epidemiology and Microbiology';

UPDATE gps_sample SET submitting_institution = 'UniBueAir' WHERE submitting_institution = 'Universidad de Buenos Aires';

UPDATE gps_sample SET submitting_institution = 'UniHosCarGusCar' WHERE submitting_institution = 'University Hospital Carl Gustav Carus Dresden';

UPDATE gps_sample SET submitting_institution = 'IasHos' WHERE submitting_institution = 'Iaso Hospital';

UPDATE gps_sample SET submitting_institution = 'UniNorCarChaHil' WHERE submitting_institution = 'University of North Carolina at Chapel Hill';

UPDATE gps_sample SET submitting_institution = 'IstSupSan' WHERE submitting_institution = 'Istituto Superiore di Sanità';

UPDATE gps_sample SET submitting_institution = 'ÇukUniFacMedDep' WHERE submitting_institution = 'Çukurova University, Faculty of Medicine, Department of Medical Microbiology';

UPDATE gps_sample SET submitting_institution = 'CenExpBioDiaCam' WHERE submitting_institution = 'Centre of Expertise and Biological Diagnostic of Cameroon (CEDBCAM)';


CALL update_database_version('0.4.0', 'drop FK constraint in api_sample; drop api_institution; replace institution names w/ institution keys in api_sample and gps_sample');
