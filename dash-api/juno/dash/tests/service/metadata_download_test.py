from   unittest      import TestCase
from   unittest.mock import patch
from   urllib.error  import URLError
from   DataSources.metadata_download  import MetadataDownload
from   DataSources.metadata_download  import Monocle_Download_Client
from   DataSources.metadata_download  import ProtocolError

import logging
logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='CRITICAL')

class MetadataDownloadTest(TestCase):

   test_config             = 'dash/tests/mock_data/data_sources.yml'
   bad_config              = 'dash/tests/mock_data/data_sources_bad.yml'
   genuine_api_host        = 'http://metadata-api/'
   bad_api_host            = 'http://no.such.host/'
   bad_api_endpoint        = '/no/such/endpoint'
   # this pattern should match a container on the docker network
   base_url_regex          = '^http://[\w\-]+$'
   endpoint_regex          = '(/[\w\-\.]+)+'
   # metadta and in silico data downloads require a list of strings, each is a sample ID & lane ID pair, colon-separated
   mock_download_param     = ['5903STDY8059053:31663_7#43']
   mock_bad_download       =  """{  "wrong key":
                                       {  "does": "not matter what appears here"
                                       }
                                    }"""

   # metadata as returned by the metadata API /download endpoint
   mock_metadata_download  =  """{  "download": [
                                       {  "sanger_sample_id":           { "order": 1, "name": "Sanger_Sample_ID", "value": "5903STDY8059053"},
                                          "supplier_sample_name":       { "order": 2, "name": "Supplier_Sample_Name", "value": ""},
                                          "public_name":                { "order": 3, "name": "Public_Name", "value": "JN_HK_GBS1WT"},
                                          "lane_id":                    { "order": 4, "name": "Lane_ID", "value": "31663_7#43"},
                                          "study_name":                 { "order": 5, "name": "Study_Name", "value": ""},
                                          "study_ref":                  { "order": 6, "name": "Study_Reference", "value": ""},
                                          "selection_random":           { "order": 7, "name": "Selection_Random", "value": ""},
                                          "country":                    { "order": 8, "name": "Country", "value": ""},
                                          "county_state":               { "order": 9, "name": "County / state", "value": ""},
                                          "city":                       { "order": 10, "name": "City", "value": ""},
                                          "submitting_institution":     { "order": 11, "name": "Submitting_Institution", "value": "The Chinese University of Hong Kong"},
                                          "collection_year":            { "order": 12, "name": "Collection_year", "value": ""},
                                          "collection_month":           { "order": 13, "name": "Collection_month", "value": ""},
                                          "collection_day":             { "order": 14, "name": "Collection_day", "value": ""},
                                          "host_species":               { "order": 15, "name": "Host_species", "value": ""},
                                          "gender":                     { "order": 16, "name": "Gender", "value": ""},
                                          "age_group":                  { "order": 17, "name": "Age_group", "value": ""},
                                          "age_years":                  { "order": 18, "name": "Age_years", "value": ""},
                                          "age_months":                 { "order": 19, "name": "Age_months", "value": ""},
                                          "age_weeks":                  { "order": 20, "name": "Age_weeks", "value": ""},
                                          "age_days":                   { "order": 21, "name": "Age_days", "value": ""},
                                          "host_status":                { "order": 22, "name": "Host_status", "value": "invasive"},
                                          "disease_type":               { "order": 23, "name": "Disease_type", "value": ""},
                                          "disease_onset":              { "order": 24, "name": "Disease_onset", "value": ""},
                                          "isolation_source":           { "order": 25, "name": "Isolation_source", "value": ""},
                                          "serotype":                   { "order": 26, "name": "Serotype", "value": "III-1"},
                                          "serotype_method":            { "order": 27, "name": "Serotype_method", "value": ""},
                                          "infection_during_pregnancy": { "order": 28, "name": "Infection_during_pregnancy", "value": ""},
                                          "maternal_infection_type":    { "order": 29, "name": "Maternal_infection_type", "value": ""},
                                          "gestational_age_weeks":      { "order": 30, "name": "Gestational_age_weeks", "value": ""},
                                          "birth_weight_gram":          { "order": 31, "name": "Birthweight_gram", "value": ""},
                                          "apgar_score":                { "order": 32, "name": "Apgar_score", "value": ""},
                                          "ceftizoxime":                { "order": 33, "name": "Ceftizoxime", "value": ""},
                                          "ceftizoxime_method":         { "order": 34, "name": "Ceftizoxime_method", "value": ""},
                                          "cefoxitin":                  { "order": 35, "name": "Cefoxitin", "value": ""},
                                          "cefoxitin_method":           { "order": 36, "name": "Cefoxitin_method", "value": ""},
                                          "cefotaxime":                 { "order": 37, "name": "Cefotaxime", "value": ""},
                                          "cefotaxime_method":          { "order": 38, "name": "Cefotaxime_method", "value": ""},
                                          "cefazolin":                  { "order": 39, "name": "Cefazolin", "value": ""},
                                          "cefazolin_method":           { "order": 40, "name": "Cefazolin_method", "value": ""},
                                          "ampicillin":                 { "order": 41, "name": "Ampicillin", "value": ""},
                                          "ampicillin_method":          { "order": 42, "name": "Ampicillin_method", "value": ""},
                                          "penicillin":                 { "order": 43, "name": "Penicillin", "value": ""},
                                          "penicillin_method":          { "order": 44, "name": "Penicillin_method", "value": ""},
                                          "erythromycin":               { "order": 45, "name": "Erythromycin", "value": ""},
                                          "erythromycin_method":        { "order": 46, "name": "Erythromycin_method", "value": ""},
                                          "clindamycin":                { "order": 47, "name": "Clindamycin", "value": ""},
                                          "clindamycin_method":         { "order": 48, "name": "Clindamycin_method", "value": ""},
                                          "tetracycline":               { "order": 49, "name": "Tetracycline", "value": ""},
                                          "tetracycline_method":        { "order": 50, "name": "Tetracycline_method", "value": ""},
                                          "levofloxacin":               { "order": 51, "name": "Levofloxacin", "value": ""},
                                          "levofloxacin_method":        { "order": 52, "name": "Levofloxacin_method", "value": ""},
                                          "ciprofloxacin":              { "order": 53, "name": "Ciprofloxacin", "value": ""},
                                          "ciprofloxacin_method":       { "order": 54, "name": "Ciprofloxacin_method", "value": ""},
                                          "daptomycin":                 { "order": 55, "name": "Daptomycin", "value": ""},
                                          "daptomycin_method":          { "order": 56, "name": "Daptomycin_method", "value": ""},
                                          "vancomycin":                 { "order": 57, "name": "Vancomycin", "value": ""},
                                          "vancomycin_method":          { "order": 58, "name": "Vancomycin_method", "value": ""},
                                          "linezolid":                  { "order": 59, "name": "Linezolid", "value": ""},
                                          "linezolid_method":           { "order": 60, "name": "Linezolid_method", "value": ""},
                                          "additional_metadata":        { "order": 61, "name": "Additional_metadata", "value": ""}
                                          }
                                    ]
                                 }"""

   # these are the metadata as they should be returned by MetadataDownload.get_metadata()
   # currently they are merely a python dict that exactly matches the JSON returned by the metadata API
   expected_metadata       =  {  "sanger_sample_id":           { "order": 1, "name": "Sanger_Sample_ID", "value": "5903STDY8059053"},
                                 "supplier_sample_name":       { "order": 2, "name": "Supplier_Sample_Name", "value": ""},
                                 "public_name":                { "order": 3, "name": "Public_Name", "value": "JN_HK_GBS1WT"},
                                 "lane_id":                    { "order": 4, "name": "Lane_ID", "value": "31663_7#43"},
                                 "study_name":                 { "order": 5, "name": "Study_Name", "value": ""},
                                 "study_ref":                  { "order": 6, "name": "Study_Reference", "value": ""},
                                 "selection_random":           { "order": 7, "name": "Selection_Random", "value": ""},
                                 "country":                    { "order": 8, "name": "Country", "value": ""},
                                 "county_state":               { "order": 9, "name": "County / state", "value": ""},
                                 "city":                       { "order": 10, "name": "City", "value": ""},
                                 "submitting_institution":     { "order": 11, "name": "Submitting_Institution", "value": "The Chinese University of Hong Kong"},
                                 "collection_year":            { "order": 12, "name": "Collection_year", "value": ""},
                                 "collection_month":           { "order": 13, "name": "Collection_month", "value": ""},
                                 "collection_day":             { "order": 14, "name": "Collection_day", "value": ""},
                                 "host_species":               { "order": 15, "name": "Host_species", "value": ""},
                                 "gender":                     { "order": 16, "name": "Gender", "value": ""},
                                 "age_group":                  { "order": 17, "name": "Age_group", "value": ""},
                                 "age_years":                  { "order": 18, "name": "Age_years", "value": ""},
                                 "age_months":                 { "order": 19, "name": "Age_months", "value": ""},
                                 "age_weeks":                  { "order": 20, "name": "Age_weeks", "value": ""},
                                 "age_days":                   { "order": 21, "name": "Age_days", "value": ""},
                                 "host_status":                { "order": 22, "name": "Host_status", "value": "invasive"},
                                 "disease_type":               { "order": 23, "name": "Disease_type", "value": ""},
                                 "disease_onset":              { "order": 24, "name": "Disease_onset", "value": ""},
                                 "isolation_source":           { "order": 25, "name": "Isolation_source", "value": ""},
                                 "serotype":                   { "order": 26, "name": "Serotype", "value": "III-1"},
                                 "serotype_method":            { "order": 27, "name": "Serotype_method", "value": ""},
                                 "infection_during_pregnancy": { "order": 28, "name": "Infection_during_pregnancy", "value": ""},
                                 "maternal_infection_type":    { "order": 29, "name": "Maternal_infection_type", "value": ""},
                                 "gestational_age_weeks":      { "order": 30, "name": "Gestational_age_weeks", "value": ""},
                                 "birth_weight_gram":          { "order": 31, "name": "Birthweight_gram", "value": ""},
                                 "apgar_score":                { "order": 32, "name": "Apgar_score", "value": ""},
                                 "ceftizoxime":                { "order": 33, "name": "Ceftizoxime", "value": ""},
                                 "ceftizoxime_method":         { "order": 34, "name": "Ceftizoxime_method", "value": ""},
                                 "cefoxitin":                  { "order": 35, "name": "Cefoxitin", "value": ""},
                                 "cefoxitin_method":           { "order": 36, "name": "Cefoxitin_method", "value": ""},
                                 "cefotaxime":                 { "order": 37, "name": "Cefotaxime", "value": ""},
                                 "cefotaxime_method":          { "order": 38, "name": "Cefotaxime_method", "value": ""},
                                 "cefazolin":                  { "order": 39, "name": "Cefazolin", "value": ""},
                                 "cefazolin_method":           { "order": 40, "name": "Cefazolin_method", "value": ""},
                                 "ampicillin":                 { "order": 41, "name": "Ampicillin", "value": ""},
                                 "ampicillin_method":          { "order": 42, "name": "Ampicillin_method", "value": ""},
                                 "penicillin":                 { "order": 43, "name": "Penicillin", "value": ""},
                                 "penicillin_method":          { "order": 44, "name": "Penicillin_method", "value": ""},
                                 "erythromycin":               { "order": 45, "name": "Erythromycin", "value": ""},
                                 "erythromycin_method":        { "order": 46, "name": "Erythromycin_method", "value": ""},
                                 "clindamycin":                { "order": 47, "name": "Clindamycin", "value": ""},
                                 "clindamycin_method":         { "order": 48, "name": "Clindamycin_method", "value": ""},
                                 "tetracycline":               { "order": 49, "name": "Tetracycline", "value": ""},
                                 "tetracycline_method":        { "order": 50, "name": "Tetracycline_method", "value": ""},
                                 "levofloxacin":               { "order": 51, "name": "Levofloxacin", "value": ""},
                                 "levofloxacin_method":        { "order": 52, "name": "Levofloxacin_method", "value": ""},
                                 "ciprofloxacin":              { "order": 53, "name": "Ciprofloxacin", "value": ""},
                                 "ciprofloxacin_method":       { "order": 54, "name": "Ciprofloxacin_method", "value": ""},
                                 "daptomycin":                 { "order": 55, "name": "Daptomycin", "value": ""},
                                 "daptomycin_method":          { "order": 56, "name": "Daptomycin_method", "value": ""},
                                 "vancomycin":                 { "order": 57, "name": "Vancomycin", "value": ""},
                                 "vancomycin_method":          { "order": 58, "name": "Vancomycin_method", "value": ""},
                                 "linezolid":                  { "order": 59, "name": "Linezolid", "value": ""},
                                 "linezolid_method":           { "order": 60, "name": "Linezolid_method", "value": ""},
                                 "additional_metadata":        { "order": 61, "name": "Additional_metadata", "value": ""}
                                 }

   mock_in_silico_data_download  =  """{  "download": [
                                             {  "lane_id":        {"order": 0,  "name": "lane_id", "value": "50000_2#287"},
                                                "cps_type":       {"order": 1,  "name": "cps_type", "value": "III"},
                                                "ST":             {"order": 2,  "name": "ST", "value": "ST-II"},
                                                "adhP":           {"order": 3,  "name": "adhP", "value": "3"},
                                                "pheS":           {"order": 4,  "name": "pheS", "value": "11"},
                                                "atr":            {"order": 5,  "name": "atr", "value": "0"},
                                                "glnA":           {"order": 6,  "name": "glnA", "value": "16"},
                                                "sdhA":           {"order": 7,  "name": "sdhA", "value": "14"},
                                                "glcK":           {"order": 8,  "name": "glcK", "value": "31"},
                                                "tkt":            {"order": 9,  "name": "tkt", "value": "6"},
                                                "twenty_three_S1":{"order": 10, "name": "twenty_three_S1", "value": "pos"},
                                                "twenty_three_S3":{"order": 11, "name": "twenty_three_S3", "value": "pos"},
                                                "CAT":            {"order": 12, "name": "CAT", "value": "neg"},
                                                "ERMB":        	{"order": 13, "name": "ERMB", "value": "neg"},
                                                "ERMT":        	{"order": 14, "name": "ERMT", "value": "neg"},
                                                "FOSA":        	{"order": 15, "name": "FOSA", "value": "neg"},
                                                "GYRA":        	{"order": 16, "name": "GYRA", "value": "pos"},
                                                "LNUB":        	{"order": 17, "name": "LNUB", "value": "neg"},
                                                "LSAC":        	{"order": 18, "name": "LSAC", "value": "neg"},
                                                "MEFA":        	{"order": 19, "name": "MEFA", "value": "neg"},
                                                "MPHC":        	{"order": 20, "name": "MPHC", "value": "neg"},
                                                "MSRA":        	{"order": 21, "name": "MSRA", "value": "neg"},
                                                "MSRD":        	{"order": 22, "name": "MSRD", "value": "neg"},
                                                "PARC":        	{"order": 23, "name": "PARC", "value": "pos"},
                                                "RPOBGBS_1":   	{"order": 24, "name": "RPOBGBS_1", "value": "neg"},
                                                "RPOBGBS_2":   	{"order": 25, "name": "RPOBGBS_2", "value": "neg"},
                                                "RPOBGBS_3":   	{"order": 26, "name": "RPOBGBS_3", "value": "neg"},
                                                "RPOBGBS_4":   	{"order": 27, "name": "RPOBGBS_4", "value": "neg"},
                                                "SUL2":        	{"order": 28, "name": "SUL2", "value": "neg"},
                                                "TETB": 				{"order": 29, "name": "TETB", "value": "neg"},
                                                "TETL": 				{"order": 30, "name": "TETL", "value": "neg"},
                                                "TETM": 				{"order": 31, "name": "TETM", "value": "pos"},
                                                "TETO": 				{"order": 32, "name": "TETO", "value": "neg"},
                                                "TETS": 				{"order": 33, "name": "TETS", "value": "neg"},
                                                "ALP1": 				{"order": 34, "name": "ALP1", "value": "neg"},
                                                "ALP23": 		   {"order": 35, "name": "ALP23", "value": "neg"},
                                                "ALPHA":          {"order": 36, "name": "ALPHA", "value": "neg"},
                                                "HVGA": 				{"order": 37, "name": "HVGA", "value": "pos"},
                                                "PI1": 				{"order": 38, "name": "PI1", "value": "pos"},
                                                "PI2A1": 		   {"order": 39, "name": "PI2A1", "value": "neg"},
                                                "PI2A2": 		   {"order": 40, "name": "PI2A2", "value": "neg"},
                                                "PI2B": 				{"order": 41, "name": "PI2B", "value": "pos"},
                                                "RIB": 				{"order": 42, "name": "RIB", "value": "pos"},
                                                "SRR1": 				{"order": 43, "name": "SRR1", "value": "neg"},
                                                "SRR2": 				{"order": 44, "name": "SRR2", "value": "pos"},
                                                "GYRA_variant":   {"order": 45, "name": "GYRA_variant", "value": "GYRA-T78Q,L55A"},
                                                "PARC_variant":   {"order": 46, "name": "PARC_variant", "value": "PARC-Q17S"}
                                                }
                                          ]
                                       }"""

   # these are the metadata as they should be returned by MetadataDownload.get_in_silicoPdata()
   # currently they are merely a python dict that exactly matches the JSON returned by the metadata API
   expected_in_silico_data = {   "lane_id":        {"order": 0,  "name": "lane_id", "value": "50000_2#287"},
                                 "cps_type":       {"order": 1,  "name": "cps_type", "value": "III"},
                                 "ST":             {"order": 2,  "name": "ST", "value": "ST-II"},
                                 "adhP":           {"order": 3,  "name": "adhP", "value": "3"},
                                 "pheS":           {"order": 4,  "name": "pheS", "value": "11"},
                                 "atr":            {"order": 5,  "name": "atr", "value": "0"},
                                 "glnA":           {"order": 6,  "name": "glnA", "value": "16"},
                                 "sdhA":           {"order": 7,  "name": "sdhA", "value": "14"},
                                 "glcK":           {"order": 8,  "name": "glcK", "value": "31"},
                                 "tkt":            {"order": 9,  "name": "tkt", "value": "6"},
                                 "twenty_three_S1":{"order": 10, "name": "twenty_three_S1", "value": "pos"},
                                 "twenty_three_S3":{"order": 11, "name": "twenty_three_S3", "value": "pos"},
                                 "CAT":            {"order": 12, "name": "CAT", "value": "neg"},
                                 "ERMB":        	{"order": 13, "name": "ERMB", "value": "neg"},
                                 "ERMT":        	{"order": 14, "name": "ERMT", "value": "neg"},
                                 "FOSA":        	{"order": 15, "name": "FOSA", "value": "neg"},
                                 "GYRA":        	{"order": 16, "name": "GYRA", "value": "pos"},
                                 "LNUB":        	{"order": 17, "name": "LNUB", "value": "neg"},
                                 "LSAC":        	{"order": 18, "name": "LSAC", "value": "neg"},
                                 "MEFA":        	{"order": 19, "name": "MEFA", "value": "neg"},
                                 "MPHC":        	{"order": 20, "name": "MPHC", "value": "neg"},
                                 "MSRA":        	{"order": 21, "name": "MSRA", "value": "neg"},
                                 "MSRD":        	{"order": 22, "name": "MSRD", "value": "neg"},
                                 "PARC":        	{"order": 23, "name": "PARC", "value": "pos"},
                                 "RPOBGBS_1":   	{"order": 24, "name": "RPOBGBS_1", "value": "neg"},
                                 "RPOBGBS_2":   	{"order": 25, "name": "RPOBGBS_2", "value": "neg"},
                                 "RPOBGBS_3":   	{"order": 26, "name": "RPOBGBS_3", "value": "neg"},
                                 "RPOBGBS_4":   	{"order": 27, "name": "RPOBGBS_4", "value": "neg"},
                                 "SUL2":        	{"order": 28, "name": "SUL2", "value": "neg"},
                                 "TETB": 				{"order": 29, "name": "TETB", "value": "neg"},
                                 "TETL": 				{"order": 30, "name": "TETL", "value": "neg"},
                                 "TETM": 				{"order": 31, "name": "TETM", "value": "pos"},
                                 "TETO": 				{"order": 32, "name": "TETO", "value": "neg"},
                                 "TETS": 				{"order": 33, "name": "TETS", "value": "neg"},
                                 "ALP1": 				{"order": 34, "name": "ALP1", "value": "neg"},
                                 "ALP23": 		   {"order": 35, "name": "ALP23", "value": "neg"},
                                 "ALPHA":          {"order": 36, "name": "ALPHA", "value": "neg"},
                                 "HVGA": 				{"order": 37, "name": "HVGA", "value": "pos"},
                                 "PI1": 				{"order": 38, "name": "PI1", "value": "pos"},
                                 "PI2A1": 		   {"order": 39, "name": "PI2A1", "value": "neg"},
                                 "PI2A2": 		   {"order": 40, "name": "PI2A2", "value": "neg"},
                                 "PI2B": 				{"order": 41, "name": "PI2B", "value": "pos"},
                                 "RIB": 				{"order": 42, "name": "RIB", "value": "pos"},
                                 "SRR1": 				{"order": 43, "name": "SRR1", "value": "neg"},
                                 "SRR2": 				{"order": 44, "name": "SRR2", "value": "pos"},
                                 "GYRA_variant":   {"order": 45, "name": "GYRA_variant", "value": "GYRA-T78Q,L55A"},
                                 "PARC_variant":   {"order": 46, "name": "PARC_variant", "value": "PARC-Q17S"}
                                 }


   def setUp(self):
      self.download           = MetadataDownload(set_up=False)
      self.download.dl_client = Monocle_Download_Client(set_up=False)
      self.download.dl_client.set_up(self.test_config)

   def test_init(self):
      self.assertIsInstance(self.download,            MetadataDownload)
      self.assertIsInstance(self.download.dl_client,  Monocle_Download_Client)
            
   def test_init_values(self):
      self.assertRegex(self.download.dl_client.config['base_url'],   self.base_url_regex)
      self.assertRegex(self.download.dl_client.config['swagger'],    self.endpoint_regex)
      self.assertRegex(self.download.dl_client.config['download'],   self.endpoint_regex)
      self.assertIsInstance(self.download.dl_client.config['metadata_key'], type('a string'))
 
   def test_reject_bad_config(self):
      with self.assertRaises(KeyError):
         doomed = Monocle_Download_Client(set_up=False)
         doomed.set_up(self.bad_config)
         
   def test_missing_config(self):
      with self.assertRaises(FileNotFoundError):
         doomed = Monocle_Download_Client(set_up=False)
         doomed.set_up('no_such_config.yml')
         
   def test_reject_bad_url(self):
      with self.assertRaises(URLError):
         doomed = Monocle_Download_Client(set_up=False)
         doomed.set_up(self.test_config)
         doomed.config['base_url']=self.bad_api_host
         endpoint = doomed.config['download']+self.mock_download_param[0]
         doomed.make_request(endpoint)
         
   def test_reject_bad_endpoint(self):
      with self.assertRaises(URLError):
         doomed = Monocle_Download_Client(set_up=False)
         doomed.set_up(self.test_config)
         doomed.config['base_url']=self.genuine_api_host
         endpoint = self.bad_api_endpoint+self.mock_download_param[0]
         doomed.make_request(endpoint)
 
   @patch.object(Monocle_Download_Client, 'make_request')
   def test_download_metadata(self, mock_request):
      mock_request.return_value = self.mock_metadata_download
      lanes = self.download.get_metadata(self.mock_download_param)
      # response should be list of dict
      self.assertIsInstance(lanes, type(['a', 'list']))
      this_lane = lanes[0]
      self.assertIsInstance(this_lane, type({'a': 'dict'}))
      # check all the expected keys are present
      for expected_key in self.expected_metadata.keys():
         self.assertTrue(expected_key in this_lane, msg="required key '{}' not found in lane dict".format(expected_key))
      # check data are correct
      self.assertEqual(this_lane, self.expected_metadata, msg="returned metadata differ from expected metadata")

   @patch.object(Monocle_Download_Client, 'make_request')
   def test_reject_bad_download_metadata_response(self, mock_request):
      with self.assertRaises(ProtocolError):
         mock_request.return_value = self.mock_bad_download
         self.download.get_metadata(self.mock_download_param[0])

   @patch.object(Monocle_Download_Client, 'make_request')
   def test_download_in_silico_data(self, mock_request):
      mock_request.return_value = self.mock_in_silico_data_download
      lanes = self.download.get_in_silico_data(self.mock_download_param)
      # response should be list of dict
      self.assertIsInstance(lanes, type(['a', 'list']))
      this_lane = lanes[0]
      self.assertIsInstance(this_lane, type({'a': 'dict'}))
      # check all the expected keys are present
      for expected_key in self.expected_in_silico_data.keys():
         self.assertTrue(expected_key in this_lane, msg="required key '{}' not found in lane dict".format(expected_key))
      # check data are correct
      self.assertEqual(this_lane, self.expected_in_silico_data, msg="returned in silico data differ from expected data")

   @patch.object(Monocle_Download_Client, 'make_request')
   def test_reject_bad_download_in_silico_data_response(self, mock_request):
      with self.assertRaises(ProtocolError):
         mock_request.return_value = self.mock_bad_download
         self.download.get_in_silico_data(self.mock_download_param[0])
