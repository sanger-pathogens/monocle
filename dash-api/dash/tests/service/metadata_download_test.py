import logging
import urllib.parse
import urllib.request
from unittest import TestCase
from unittest.mock import patch

from DataSources.metadata_download import MetadataDownload, MonocleDownloadClient, ProtocolError

logging.basicConfig(format="%(asctime)-15s %(levelname)s:  %(message)s", level="CRITICAL")

INSTITUTIONS = {"TheChiUniHonKon": {"name": "The Chinese University of Hong Kong"}}


class MetadataDownloadTest(TestCase):

    test_config = "dash/tests/mock_data/data_sources.yml"
    bad_config = "dash/tests/mock_data/data_sources_bad.yml"
    genuine_api_host = "http://metadata-api/"
    bad_api_host = "http://no.such.host/"
    bad_api_endpoint = "/no/such/endpoint"
    # this pattern should match a container on the docker network
    base_url_regex = "^http://[\\w\\-]+(/[\\w\\-]+)*$"
    endpoint_regex = "(/[\\w\\-\\.]+)+"
    mock_project = "juno"
    # metadata, in silico and QC data downloads require a list of strings, each is a sample ID & lane ID pair, colon-separated
    mock_download_param = ["5903STDY8059053:31663_7#43"]
    mock_bad_download = """{  "wrong key":
                                       {  "does": "not matter what appears here"
                                       }
                                    }"""

    # metadata as returned by the metadata API /download endpoint
    mock_metadata_download = """{  "download": [
                                       {  "sanger_sample_id":           { "order": 1, "title": "Sanger_Sample_ID", "value": "5903STDY8059053"},
                                          "supplier_sample_name":       { "order": 2, "title": "Supplier_Sample_Name", "value": ""},
                                          "public_name":                { "order": 3, "title": "Public_Name", "value": "JN_HK_GBS1WT"},
                                          "lane_id":                    { "order": 4, "title": "Lane_ID", "value": "31663_7#43"},
                                          "study_name":                 { "order": 5, "title": "Study_Name", "value": ""},
                                          "study_ref":                  { "order": 6, "title": "Study_Reference", "value": ""},
                                          "selection_random":           { "order": 7, "title": "Selection_Random", "value": ""},
                                          "country":                    { "order": 8, "title": "Country", "value": ""},
                                          "county_state":               { "order": 9, "title": "County / state", "value": ""},
                                          "city":                       { "order": 10, "title": "City", "value": ""},
                                          "submitting_institution":     { "order": 11, "title": "Submitting_Institution", "value": "TheChiUniHonKon"},
                                          "collection_year":            { "order": 12, "title": "Collection_year", "value": ""},
                                          "collection_month":           { "order": 13, "title": "Collection_month", "value": ""},
                                          "collection_day":             { "order": 14, "title": "Collection_day", "value": ""},
                                          "host_species":               { "order": 15, "title": "Host_species", "value": ""},
                                          "gender":                     { "order": 16, "title": "Gender", "value": ""},
                                          "age_group":                  { "order": 17, "title": "Age_group", "value": ""},
                                          "age_years":                  { "order": 18, "title": "Age_years", "value": ""},
                                          "age_months":                 { "order": 19, "title": "Age_months", "value": ""},
                                          "age_weeks":                  { "order": 20, "title": "Age_weeks", "value": ""},
                                          "age_days":                   { "order": 21, "title": "Age_days", "value": ""},
                                          "host_status":                { "order": 22, "title": "Host_status", "value": "invasive"},
                                          "disease_type":               { "order": 23, "title": "Disease_type", "value": ""},
                                          "disease_onset":              { "order": 24, "title": "Disease_onset", "value": ""},
                                          "isolation_source":           { "order": 25, "title": "Isolation_source", "value": ""},
                                          "serotype":                   { "order": 26, "title": "Serotype", "value": "III-1"},
                                          "serotype_method":            { "order": 27, "title": "Serotype_method", "value": ""},
                                          "infection_during_pregnancy": { "order": 28, "title": "Infection_during_pregnancy", "value": ""},
                                          "maternal_infection_type":    { "order": 29, "title": "Maternal_infection_type", "value": ""},
                                          "gestational_age_weeks":      { "order": 30, "title": "Gestational_age_weeks", "value": ""},
                                          "birth_weight_gram":          { "order": 31, "title": "Birthweight_gram", "value": ""},
                                          "apgar_score":                { "order": 32, "title": "Apgar_score", "value": ""},
                                          "ceftizoxime":                { "order": 33, "title": "Ceftizoxime", "value": ""},
                                          "ceftizoxime_method":         { "order": 34, "title": "Ceftizoxime_method", "value": ""},
                                          "cefoxitin":                  { "order": 35, "title": "Cefoxitin", "value": ""},
                                          "cefoxitin_method":           { "order": 36, "title": "Cefoxitin_method", "value": ""},
                                          "cefotaxime":                 { "order": 37, "title": "Cefotaxime", "value": ""},
                                          "cefotaxime_method":          { "order": 38, "title": "Cefotaxime_method", "value": ""},
                                          "cefazolin":                  { "order": 39, "title": "Cefazolin", "value": ""},
                                          "cefazolin_method":           { "order": 40, "title": "Cefazolin_method", "value": ""},
                                          "ampicillin":                 { "order": 41, "title": "Ampicillin", "value": ""},
                                          "ampicillin_method":          { "order": 42, "title": "Ampicillin_method", "value": ""},
                                          "penicillin":                 { "order": 43, "title": "Penicillin", "value": ""},
                                          "penicillin_method":          { "order": 44, "title": "Penicillin_method", "value": ""},
                                          "erythromycin":               { "order": 45, "title": "Erythromycin", "value": ""},
                                          "erythromycin_method":        { "order": 46, "title": "Erythromycin_method", "value": ""},
                                          "clindamycin":                { "order": 47, "title": "Clindamycin", "value": ""},
                                          "clindamycin_method":         { "order": 48, "title": "Clindamycin_method", "value": ""},
                                          "tetracycline":               { "order": 49, "title": "Tetracycline", "value": ""},
                                          "tetracycline_method":        { "order": 50, "title": "Tetracycline_method", "value": ""},
                                          "levofloxacin":               { "order": 51, "title": "Levofloxacin", "value": ""},
                                          "levofloxacin_method":        { "order": 52, "title": "Levofloxacin_method", "value": ""},
                                          "ciprofloxacin":              { "order": 53, "title": "Ciprofloxacin", "value": ""},
                                          "ciprofloxacin_method":       { "order": 54, "title": "Ciprofloxacin_method", "value": ""},
                                          "daptomycin":                 { "order": 55, "title": "Daptomycin", "value": ""},
                                          "daptomycin_method":          { "order": 56, "title": "Daptomycin_method", "value": ""},
                                          "vancomycin":                 { "order": 57, "title": "Vancomycin", "value": ""},
                                          "vancomycin_method":          { "order": 58, "title": "Vancomycin_method", "value": ""},
                                          "linezolid":                  { "order": 59, "title": "Linezolid", "value": ""},
                                          "linezolid_method":           { "order": 60, "title": "Linezolid_method", "value": ""},
                                          "additional_metadata":        { "order": 61, "title": "Additional_metadata", "value": ""}
                                          }
                                    ]
                                 }"""

    # these are the metadata as they should be returned by MetadataDownload.get_metadata()
    # currently they are merely a python dict that exactly matches the JSON returned by the metadata API
    expected_metadata = {
        "sanger_sample_id": {"order": 1, "title": "Sanger_Sample_ID", "value": "5903STDY8059053"},
        "supplier_sample_name": {"order": 2, "title": "Supplier_Sample_Name", "value": ""},
        "public_name": {"order": 3, "title": "Public_Name", "value": "JN_HK_GBS1WT"},
        "lane_id": {"order": 4, "title": "Lane_ID", "value": "31663_7#43"},
        "study_name": {"order": 5, "title": "Study_Name", "value": ""},
        "study_ref": {"order": 6, "title": "Study_Reference", "value": ""},
        "selection_random": {"order": 7, "title": "Selection_Random", "value": ""},
        "country": {"order": 8, "title": "Country", "value": ""},
        "county_state": {"order": 9, "title": "County / state", "value": ""},
        "city": {"order": 10, "title": "City", "value": ""},
        "submitting_institution": {
            "order": 11,
            "title": "Submitting_Institution",
            "value": "The Chinese University of Hong Kong",
        },
        "collection_year": {"order": 12, "title": "Collection_year", "value": ""},
        "collection_month": {"order": 13, "title": "Collection_month", "value": ""},
        "collection_day": {"order": 14, "title": "Collection_day", "value": ""},
        "host_species": {"order": 15, "title": "Host_species", "value": ""},
        "gender": {"order": 16, "title": "Gender", "value": ""},
        "age_group": {"order": 17, "title": "Age_group", "value": ""},
        "age_years": {"order": 18, "title": "Age_years", "value": ""},
        "age_months": {"order": 19, "title": "Age_months", "value": ""},
        "age_weeks": {"order": 20, "title": "Age_weeks", "value": ""},
        "age_days": {"order": 21, "title": "Age_days", "value": ""},
        "host_status": {"order": 22, "title": "Host_status", "value": "invasive"},
        "disease_type": {"order": 23, "title": "Disease_type", "value": ""},
        "disease_onset": {"order": 24, "title": "Disease_onset", "value": ""},
        "isolation_source": {"order": 25, "title": "Isolation_source", "value": ""},
        "serotype": {"order": 26, "title": "Serotype", "value": "III-1"},
        "serotype_method": {"order": 27, "title": "Serotype_method", "value": ""},
        "infection_during_pregnancy": {"order": 28, "title": "Infection_during_pregnancy", "value": ""},
        "maternal_infection_type": {"order": 29, "title": "Maternal_infection_type", "value": ""},
        "gestational_age_weeks": {"order": 30, "title": "Gestational_age_weeks", "value": ""},
        "birth_weight_gram": {"order": 31, "title": "Birthweight_gram", "value": ""},
        "apgar_score": {"order": 32, "title": "Apgar_score", "value": ""},
        "ceftizoxime": {"order": 33, "title": "Ceftizoxime", "value": ""},
        "ceftizoxime_method": {"order": 34, "title": "Ceftizoxime_method", "value": ""},
        "cefoxitin": {"order": 35, "title": "Cefoxitin", "value": ""},
        "cefoxitin_method": {"order": 36, "title": "Cefoxitin_method", "value": ""},
        "cefotaxime": {"order": 37, "title": "Cefotaxime", "value": ""},
        "cefotaxime_method": {"order": 38, "title": "Cefotaxime_method", "value": ""},
        "cefazolin": {"order": 39, "title": "Cefazolin", "value": ""},
        "cefazolin_method": {"order": 40, "title": "Cefazolin_method", "value": ""},
        "ampicillin": {"order": 41, "title": "Ampicillin", "value": ""},
        "ampicillin_method": {"order": 42, "title": "Ampicillin_method", "value": ""},
        "penicillin": {"order": 43, "title": "Penicillin", "value": ""},
        "penicillin_method": {"order": 44, "title": "Penicillin_method", "value": ""},
        "erythromycin": {"order": 45, "title": "Erythromycin", "value": ""},
        "erythromycin_method": {"order": 46, "title": "Erythromycin_method", "value": ""},
        "clindamycin": {"order": 47, "title": "Clindamycin", "value": ""},
        "clindamycin_method": {"order": 48, "title": "Clindamycin_method", "value": ""},
        "tetracycline": {"order": 49, "title": "Tetracycline", "value": ""},
        "tetracycline_method": {"order": 50, "title": "Tetracycline_method", "value": ""},
        "levofloxacin": {"order": 51, "title": "Levofloxacin", "value": ""},
        "levofloxacin_method": {"order": 52, "title": "Levofloxacin_method", "value": ""},
        "ciprofloxacin": {"order": 53, "title": "Ciprofloxacin", "value": ""},
        "ciprofloxacin_method": {"order": 54, "title": "Ciprofloxacin_method", "value": ""},
        "daptomycin": {"order": 55, "title": "Daptomycin", "value": ""},
        "daptomycin_method": {"order": 56, "title": "Daptomycin_method", "value": ""},
        "vancomycin": {"order": 57, "title": "Vancomycin", "value": ""},
        "vancomycin_method": {"order": 58, "title": "Vancomycin_method", "value": ""},
        "linezolid": {"order": 59, "title": "Linezolid", "value": ""},
        "linezolid_method": {"order": 60, "title": "Linezolid_method", "value": ""},
        "additional_metadata": {"order": 61, "title": "Additional_metadata", "value": ""},
    }

    mock_in_silico_data_download = """{  "download": [
                                             {  "lane_id":        {"order": 0,  "title": "Sample_id", "value": "50000_2#287"},
                                                "cps_type":       {"order": 1,  "title": "cps_type", "value": "III"},
                                                "ST":             {"order": 2,  "title": "ST", "value": "ST-II"},
                                                "adhP":           {"order": 3,  "title": "adhP", "value": "3"},
                                                "pheS":           {"order": 4,  "title": "pheS", "value": "11"},
                                                "atr":            {"order": 5,  "title": "atr", "value": "0"},
                                                "glnA":           {"order": 6,  "title": "glnA", "value": "16"},
                                                "sdhA":           {"order": 7,  "title": "sdhA", "value": "14"},
                                                "glcK":           {"order": 8,  "title": "glcK", "value": "31"},
                                                "tkt":            {"order": 9,  "title": "tkt", "value": "6"},
                                                "twenty_three_S1":{"order": 10, "title": "twenty_three_S1", "value": "pos"},
                                                "twenty_three_S3":{"order": 11, "title": "twenty_three_S3", "value": "pos"},
                                                "AAC6APH2":     {"order": 12, "title": "AAC6APH2", "value": "neg"},
                                                "AADECC":       {"order": 13, "title": "AADECC", "value": "neg"},
                                                "ANT6":         {"order": 14, "title": "ANT6", "value": "neg"},
                                                "APH3III":      {"order": 15, "title": "APH3III", "value": "neg"},
                                                "APH3OTHER":    {"order": 16, "title": "APH3OTHER", "value": "neg"},
                                                "CATPC194":     {"order": 17, "title": "CATPC194", "value": "neg"},
                                                "CATQ":         {"order": 18, "title": "CATQ", "value": "neg"},
                                                "ERMA":         {"order": 19, "title": "ERMA", "value": "neg"},
                                                "ERMB":        	{"order": 20, "title": "ERMB", "value": "neg"},
                                                "ERMT":        	{"order": 21, "title": "ERMT", "value": "neg"},
                                                "LNUB":        	{"order": 22, "title": "LNUB", "value": "neg"},
                                                "LNUC":        	{"order": 23, "title": "LNUC", "value": "neg"},
                                                "LSAC":        	{"order": 24, "title": "LSAC", "value": "neg"},
                                                "MEFA":        	{"order": 25, "title": "MEFA", "value": "neg"},
                                                "MPHC":        	{"order": 26, "title": "MPHC", "value": "neg"},
                                                "MSRA":        	{"order": 27, "title": "MSRA", "value": "neg"},
                                                "MSRD":        	{"order": 28, "title": "MSRD", "value": "neg"},
                                                "FOSA":        	{"order": 29, "title": "FOSA", "value": "neg"},
                                                "GYRA":        	{"order": 30, "title": "GYRA", "value": "pos"},
                                                "PARC":        	{"order": 31, "title": "PARC", "value": "pos"},
                                                "RPOBGBS_1":   	{"order": 32, "title": "RPOBGBS_1", "value": "neg"},
                                                "RPOBGBS_2":   	{"order": 33, "title": "RPOBGBS_2", "value": "neg"},
                                                "RPOBGBS_3":   	{"order": 34, "title": "RPOBGBS_3", "value": "neg"},
                                                "RPOBGBS_4":   	{"order": 35, "title": "RPOBGBS_4", "value": "neg"},
                                                "SUL2":        	{"order": 36, "title": "SUL2", "value": "neg"},
                                                "TETB": 				{"order": 37, "title": "TETB", "value": "neg"},
                                                "TETL": 				{"order": 38, "title": "TETL", "value": "neg"},
                                                "TETM": 				{"order": 39, "title": "TETM", "value": "pos"},
                                                "TETO": 				{"order": 40, "title": "TETO", "value": "neg"},
                                                "TETS": 				{"order": 41, "title": "TETS", "value": "neg"},
                                                "ALP1": 				{"order": 42, "title": "ALP1", "value": "neg"},
                                                "ALP23": 		   {"order": 43, "title": "ALP23", "value": "neg"},
                                                "ALPHA":          {"order": 44, "title": "ALPHA", "value": "neg"},
                                                "HVGA": 				{"order": 45, "title": "HVGA", "value": "pos"},
                                                "PI1": 				{"order": 46, "title": "PI1", "value": "pos"},
                                                "PI2A1": 		   {"order": 47, "title": "PI2A1", "value": "neg"},
                                                "PI2A2": 		   {"order": 48, "title": "PI2A2", "value": "neg"},
                                                "PI2B": 				{"order": 49, "title": "PI2B", "value": "pos"},
                                                "RIB": 				{"order": 50, "title": "RIB", "value": "pos"},
                                                "SRR1": 				{"order": 51, "title": "SRR1", "value": "neg"},
                                                "SRR2": 				{"order": 52, "title": "SRR2", "value": "pos"},
                                                "twenty_three_S1_variant": {"order": 53, "title": "twenty_three_S1_variant", "value": ""},
                                                "twenty_three_S3_variant": {"order": 54, "title": "twenty_three_S3_variant", "value": ""},
                                                "GYRA_variant":   {"order": 55, "title": "GYRA_variant", "value": "GYRA-T78Q,L55A"},
                                                "PARC_variant":   {"order": 56, "title": "PARC_variant", "value": "PARC-Q17S"},
                                                "RPOBGBS_1_variant": {"order": 57, "title": "RPOBGBS_1_variant", "value": ""},
                                                "RPOBGBS_2_variant": {"order": 58, "title": "RPOBGBS_2_variant", "value": ""},
                                                "RPOBGBS_3_variant": {"order": 59, "title": "RPOBGBS_3_variant", "value": ""},
                                                "RPOBGBS_4_variant": {"order": 60, "title": "RPOBGBS_4_variant", "value": ""}
                                                }
                                          ]
                                       }"""

    # these are the metadata as they should be returned by MetadataDownload.get_in_silicoPdata()
    # currently they are merely a python dict that exactly matches the JSON returned by the metadata API
    expected_in_silico_data = {
        "lane_id": {"order": 0, "title": "Sample_id", "value": "50000_2#287"},
        "cps_type": {"order": 1, "title": "cps_type", "value": "III"},
        "ST": {"order": 2, "title": "ST", "value": "ST-II"},
        "adhP": {"order": 3, "title": "adhP", "value": "3"},
        "pheS": {"order": 4, "title": "pheS", "value": "11"},
        "atr": {"order": 5, "title": "atr", "value": "0"},
        "glnA": {"order": 6, "title": "glnA", "value": "16"},
        "sdhA": {"order": 7, "title": "sdhA", "value": "14"},
        "glcK": {"order": 8, "title": "glcK", "value": "31"},
        "tkt": {"order": 9, "title": "tkt", "value": "6"},
        "twenty_three_S1": {"order": 10, "title": "twenty_three_S1", "value": "pos"},
        "twenty_three_S3": {"order": 11, "title": "twenty_three_S3", "value": "pos"},
        "AAC6APH2": {"order": 12, "title": "AAC6APH2", "value": "neg"},
        "AADECC": {"order": 13, "title": "AADECC", "value": "neg"},
        "ANT6": {"order": 14, "title": "ANT6", "value": "neg"},
        "APH3III": {"order": 15, "title": "APH3III", "value": "neg"},
        "APH3OTHER": {"order": 16, "title": "APH3OTHER", "value": "neg"},
        "CATPC194": {"order": 17, "title": "CATPC194", "value": "neg"},
        "CATQ": {"order": 18, "title": "CATQ", "value": "neg"},
        "ERMA": {"order": 19, "title": "ERMA", "value": "neg"},
        "ERMB": {"order": 20, "title": "ERMB", "value": "neg"},
        "ERMT": {"order": 21, "title": "ERMT", "value": "neg"},
        "LNUB": {"order": 22, "title": "LNUB", "value": "neg"},
        "LNUC": {"order": 23, "title": "LNUC", "value": "neg"},
        "LSAC": {"order": 24, "title": "LSAC", "value": "neg"},
        "MEFA": {"order": 25, "title": "MEFA", "value": "neg"},
        "MPHC": {"order": 26, "title": "MPHC", "value": "neg"},
        "MSRA": {"order": 27, "title": "MSRA", "value": "neg"},
        "MSRD": {"order": 28, "title": "MSRD", "value": "neg"},
        "FOSA": {"order": 29, "title": "FOSA", "value": "neg"},
        "GYRA": {"order": 30, "title": "GYRA", "value": "pos"},
        "PARC": {"order": 31, "title": "PARC", "value": "pos"},
        "RPOBGBS_1": {"order": 32, "title": "RPOBGBS_1", "value": "neg"},
        "RPOBGBS_2": {"order": 33, "title": "RPOBGBS_2", "value": "neg"},
        "RPOBGBS_3": {"order": 34, "title": "RPOBGBS_3", "value": "neg"},
        "RPOBGBS_4": {"order": 35, "title": "RPOBGBS_4", "value": "neg"},
        "SUL2": {"order": 36, "title": "SUL2", "value": "neg"},
        "TETB": {"order": 37, "title": "TETB", "value": "neg"},
        "TETL": {"order": 38, "title": "TETL", "value": "neg"},
        "TETM": {"order": 39, "title": "TETM", "value": "pos"},
        "TETO": {"order": 40, "title": "TETO", "value": "neg"},
        "TETS": {"order": 41, "title": "TETS", "value": "neg"},
        "ALP1": {"order": 42, "title": "ALP1", "value": "neg"},
        "ALP23": {"order": 43, "title": "ALP23", "value": "neg"},
        "ALPHA": {"order": 44, "title": "ALPHA", "value": "neg"},
        "HVGA": {"order": 45, "title": "HVGA", "value": "pos"},
        "PI1": {"order": 46, "title": "PI1", "value": "pos"},
        "PI2A1": {"order": 47, "title": "PI2A1", "value": "neg"},
        "PI2A2": {"order": 48, "title": "PI2A2", "value": "neg"},
        "PI2B": {"order": 49, "title": "PI2B", "value": "pos"},
        "RIB": {"order": 50, "title": "RIB", "value": "pos"},
        "SRR1": {"order": 51, "title": "SRR1", "value": "neg"},
        "SRR2": {"order": 52, "title": "SRR2", "value": "pos"},
        "twenty_three_S1_variant": {"order": 53, "title": "twenty_three_S1_variant", "value": ""},
        "twenty_three_S3_variant": {"order": 54, "title": "twenty_three_S3_variant", "value": ""},
        "GYRA_variant": {"order": 55, "title": "GYRA_variant", "value": "GYRA-T78Q,L55A"},
        "PARC_variant": {"order": 56, "title": "PARC_variant", "value": "PARC-Q17S"},
        "RPOBGBS_1_variant": {"order": 57, "title": "RPOBGBS_1_variant", "value": ""},
        "RPOBGBS_2_variant": {"order": 58, "title": "RPOBGBS_2_variant", "value": ""},
        "RPOBGBS_3_variant": {"order": 59, "title": "RPOBGBS_3_variant", "value": ""},
        "RPOBGBS_4_variant": {"order": 60, "title": "RPOBGBS_4_variant", "value": ""},
    }

    mock_qc_data_download = """{  "download": [
                                       {  "lane_id":        {"order": 0,  "title": "lane_id", "value": "50000_2#287"},
                                          "rel_abun_sa":    {"order": 1,  "title": "rel_abun_sa", "value": "86.54"}
                                          }
                                    ]
                                 }"""

    # these are the metadata as they should be returned by MetadataDownload.get_qc_data()
    # currently they are merely a python dict that exactly matches the JSON returned by the metadata API
    expected_qc_data = {
        "lane_id": {"order": 0, "title": "lane_id", "value": "50000_2#287"},
        "rel_abun_sa": {"order": 1, "title": "rel_abun_sa", "value": "86.54"},
    }

    def setUp(self):
        self.download = MetadataDownload(set_up=False)
        self.download._institutions = None
        self.download.download_client = MonocleDownloadClient(set_up=False)
        self.download.download_client.set_up(self.test_config)

    def test_init(self):
        self.assertIsInstance(self.download, MetadataDownload)
        self.assertIsInstance(self.download.download_client, MonocleDownloadClient)

    def test_init_values(self):
        self.assertRegex(self.download.download_client.config[self.mock_project]["base_url"], self.base_url_regex)
        self.assertRegex(self.download.download_client.config[self.mock_project]["swagger"], self.endpoint_regex)
        self.assertRegex(self.download.download_client.config[self.mock_project]["download"], self.endpoint_regex)
        self.assertIsInstance(self.download.download_client.config[self.mock_project]["metadata_key"], str)

    def test_reject_bad_config(self):
        with self.assertRaises(KeyError):
            doomed = MonocleDownloadClient(set_up=False)
            doomed.set_up(self.bad_config)

    def test_missing_config(self):
        with self.assertRaises(FileNotFoundError):
            doomed = MonocleDownloadClient(set_up=False)
            doomed.set_up("no_such_config.yml")

    def test_reject_bad_url(self):
        with self.assertRaises(urllib.error.URLError):
            doomed = MonocleDownloadClient(set_up=False)
            doomed.set_up(self.test_config)
            doomed.config[self.mock_project]["base_url"] = self.bad_api_host
            endpoint = doomed.config[self.mock_project]["download"] + self.mock_download_param[0]
            doomed.make_request("http://fake-container" + endpoint)

    def test_reject_bad_endpoint(self):
        with self.assertRaises(urllib.error.URLError):
            doomed = MonocleDownloadClient(set_up=False)
            doomed.set_up(self.test_config)
            doomed.config[self.mock_project]["base_url"] = self.genuine_api_host
            endpoint = self.bad_api_endpoint + self.mock_download_param[0]
            doomed.make_request("http://fake-container" + endpoint)

    @patch("DataSources.metadata_download.MonocleSampleTracking")
    @patch.object(MonocleDownloadClient, "make_request")
    def test_download_metadata(self, mock_request, mock_sample_tracking_services):
        mock_request.return_value = self.mock_metadata_download
        mock_sample_tracking_services.return_value.get_institutions.return_value = INSTITUTIONS

        lanes = self.download.get_metadata(self.mock_project, self.mock_download_param)

        # response should be list of dict
        self.assertIsInstance(lanes, list)
        this_lane = lanes[0]
        self.assertIsInstance(this_lane, dict)
        # check all the expected keys are present
        for expected_key in self.expected_metadata.keys():
            self.assertTrue(
                expected_key in this_lane, msg="required key '{}' not found in lane dict".format(expected_key)
            )
        # check data are correct
        self.assertEqual(this_lane, self.expected_metadata, msg="returned metadata differ from expected metadata")

    @patch("DataSources.metadata_download.MonocleSampleTracking")
    @patch.object(MonocleDownloadClient, "make_request")
    def test_download_metadata_does_not_replace_submitting_institution_key_if_institution_is_not_in_institution_list(
        self, mock_request, mock_sample_tracking_services
    ):
        mock_request.return_value = self.mock_metadata_download
        mock_sample_tracking_services.return_value.get_institutions.return_value = {}

        lanes = self.download.get_metadata(self.mock_project, self.mock_download_param)

        expected_submitting_institution = dict(self.expected_metadata["submitting_institution"])
        expected_submitting_institution["value"] = list(INSTITUTIONS.keys())[0]
        self.assertEqual(lanes[0]["submitting_institution"], expected_submitting_institution)

    @patch("DataSources.metadata_download.MonocleSampleTracking")
    @patch.object(MonocleDownloadClient, "make_request")
    def test_download_metadata_with_samples_without_submitting_institution(
        self, mock_request, mock_sample_tracking_services
    ):
        mock_request.return_value = '{"download": [{"sanger_sample_id": {"value": "fake_id"}}]}'
        mock_sample_tracking_services.return_value.get_institutions.return_value = INSTITUTIONS

        lanes = self.download.get_metadata(self.mock_project, self.mock_download_param)

        expected_lane = {"sanger_sample_id": {"value": "fake_id"}}
        self.assertEqual(lanes[0], expected_lane)

    @patch.object(MonocleDownloadClient, "make_request")
    def test_reject_bad_download_metadata_response(self, mock_request):
        with self.assertRaises(ProtocolError):
            mock_request.return_value = self.mock_bad_download
            self.download.get_metadata(self.mock_project, self.mock_download_param[0])

    @patch.object(MonocleDownloadClient, "make_request")
    def test_download_in_silico_data(self, mock_request):
        mock_request.return_value = self.mock_in_silico_data_download
        lanes = self.download.get_in_silico_data(self.mock_project, self.mock_download_param)
        # response should be list of dict
        self.assertIsInstance(lanes, list)
        this_lane = lanes[0]
        self.assertIsInstance(this_lane, dict)
        # check all the expected keys are present
        for expected_key in self.expected_in_silico_data.keys():
            self.assertTrue(
                expected_key in this_lane, msg="required key '{}' not found in lane dict".format(expected_key)
            )
        # check data are correct
        self.maxDiff = None
        self.assertEqual(
            this_lane, self.expected_in_silico_data, msg="returned in silico data differ from expected data"
        )

    @patch.object(MonocleDownloadClient, "make_request")
    def test_download_qc_data(self, mock_request):
        mock_request.return_value = self.mock_qc_data_download
        lanes = self.download.get_qc_data(self.mock_project, self.mock_download_param)
        # response should be list of dict
        self.assertIsInstance(lanes, list)
        this_lane = lanes[0]
        self.assertIsInstance(this_lane, dict)
        # check all the expected keys are present
        for expected_key in self.expected_qc_data.keys():
            self.assertTrue(
                expected_key in this_lane, msg="required key '{}' not found in lane dict".format(expected_key)
            )
        # check data are correct
        self.maxDiff = None
        self.assertEqual(this_lane, self.expected_qc_data, msg="returned QC data differ from expected data")

    @patch.object(MonocleDownloadClient, "make_request")
    def test_reject_bad_download_qc_data_response(self, mock_request):
        with self.assertRaises(ProtocolError):
            mock_request.return_value = self.mock_bad_download
            self.download.get_qc_data(self.mock_project, self.mock_download_param[0])

    @patch.object(urllib.request, "urlopen")
    def test_download_qc_data_when_no_qc_data_available(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError("not found", 404, "", "", "")
        lanes = self.download.get_qc_data(self.mock_project, self.mock_download_param)
        # response should be and empty list in case of a 404
        self.assertIsInstance(lanes, list)
        self.assertEqual(len(lanes), 0, msg="list was not empty as expected")
