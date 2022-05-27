# **************************************************************
# Add submitting institutions (for public GPS samples)
# **************************************************************


INSERT INTO api_institution (name, country, latitude, longitude)
VALUES ('CDC (Public GPS samples)','USA', 42.047428, -93.580467),
('Emory University (Public GPS samples)', 'USA', 33.792519, -84.323997),
('Malawi Liverpool Wellcome Trust (Public GPS samples)', 'Malawi' , 27.055010 , -81.961100),
('MRC Unit The Gambia (Public GPS samples)', 'Gambia' , 13.451290, -16.573000),
('NICD (Public GPS samples)', 'South Africa', -22.829994682193732, 27.25766324673691),
('ANLIS (Public GPS samples)', 'Argentina', -34.64110907894502, -58.390067743704286),
('CHRF (Public GPS samples)', 'Bangladesh', 23.773394027792204, 90.36676319775704),
('Institute Adolfo Lutz (IAL) (Public GPS samples)', 'Brazil', -23.554984438633692, -46.6683855715648),
('The Republican Research And Practical Center For Epidemiology And Microbiology (Public GPS samples)', 'Belarus' , 53.91649115020525, 27.632343971843884),
('Hospital Sant Joan De Deu (Public GPS samples)', 'Spain' , 41.40940548411539, 2.1004165270656534),
('CNRP/ACTIV (Public GPS samples)', 'France' , 48.79600079773016, 2.4636164838052905),
('The University Of Hong Kong (Public GPS samples)', 'China' ,22.28341669656049, 114.13672302893),
('Temple Street Childrens Hospital (Public GPS samples)', 'Ireland' ,53.356915045656635, -6.26205066015516),
('Soroka University Medical Center (Public GPS samples)', 'Israel' ,31.25849515212287, 34.80086731197016),
('Kempegowda Institute Of Medical Sciences (Public GPS samples)', 'India' ,12.928359031920744, 77.56311155137153),
('Cambodia Oxford Medical Research Unit (Public GPS samples)', 'India' ,12.787259471356087, 77.75736068753895),
('Faculty Of Medicine And Pharmacy Of Casablanca (Public GPS samples)', 'Morocco' ,33.574883191863215, -7.622347911249464),
('University Of Southampton (Public GPS samples)', 'UK' ,50.93525116692545, -1.3956735719181292),
('University Of Nebraska Medical Center (Public GPS samples)', 'USA' ,41.255016194411446, -95.97588431651644),
('Oxford Vaccine Group (Public GPS samples)', 'UK' ,51.74896377967918, -1.210755544891653),
('PNGIMR (Public GPS samples)', 'Papua New Guinea' ,-6.083231921940738, 145.38631744042257),
('National Medicines Institute (Public GPS samples)', 'Poland' ,52.34031686144253, 20.980032022221824),
('MGRIEM (Public GPS samples)', 'Russian Federation' , 0.0,0.0),
('National Laboratory Of Health Environment And Food (Public GPS samples)', 'Slovenia' ,46.5628772458123, 15.674129351851665),
('AMP (Public GPS samples)', 'Togo' ,10.86769356632183, 0.19747497014965634),
('Shoklo-Malaria-Research-Unit (Public GPS samples)', 'Thailand' ,16.70791185825175, 98.55892819718358)
;

--
-- Update the database version
--
CALL update_database_version('0.2.92', 'Update submitting institutions');
