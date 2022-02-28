import { DATA_TYPES } from "$lib/constants.js";

const DASHBOARD_API_ENDPOINT = "/dashboard-api";
const FETCH_ERROR_PATTER_NOT_FOUND = "404 ";
const FETCH_ERROR_UNKNOWN = "unknown error";
const HTTP_POST = "POST";
const JSON_HEADERS = { "Content-Type": "application/json" };

export function getInstitutionStatus(fetch) {
  return Promise.all([
    getInstitutions(fetch),
    getBatches(fetch),
    getSequencingStatus(fetch),
    getPipelineStatus(fetch)
  ])
    .then(([institutions, batches, sequencingStatus, pipelineStatus]) =>
      institutions && collateInstitutionStatus({
        institutions,
        batches,
        sequencingStatus,
        pipelineStatus
      }));
}

export function getProjectProgress(fetch) {
  return getProjectProgressData(fetch)
    .then((progress) => {
      const progressData = progress?.data;
      if (progressData) {
        return {
          dates: progressData.date,
          datasets: [{
            name: "received",
            values: progressData["samples received"]
          }, {
            name: "sequenced",
            values: progressData["samples sequenced"]
          }]
        };
      }
    });
}

//TODO use service workers to cache response
export function getBatches(fetch) {
  return fetchDashboardApiResource("get_batches", "batches", fetch);
}

export function getBulkDownloadInfo(params, fetch) {
  return fetchDashboardApiResource(
    "bulk_download_info", null, fetch, {
      method: HTTP_POST,
      headers: JSON_HEADERS,
      body: JSON.stringify(prepareBulkDownloadPayload(params))
    });
}

export function getBulkDownloadUrls(params, fetch) {
  return fetchDashboardApiResource(
    "bulk_download_urls", "download_urls", fetch, {
      method: HTTP_POST,
      headers: JSON_HEADERS,
      body: JSON.stringify(prepareBulkDownloadPayload(params))
    });
}

export function getColumns(fetch) {
  // FIXME replace w/ a call to the API
  return Promise.resolve({
      "metadata": {
        "categories": [
          {
            "name": "Sample Identifiers",
            "fields": [
              {
                "name": "public_name",
                "display": true,
                "order": 1,
                "spreadsheet heading": "Public_Name",
                "display name": "Public Name",
                "filter type": "none"
              },
              {
                "name": "sanger_sample_id",
                "display": true,
                "order": 2,
                "spreadsheet heading": "Sanger_Sample_ID",
                "display name": "Sanger Sample ID",
                "filter type": "none"
              },
              {
                "name": "supplier_sample_name",
                "display": true,
                "order": 3,
                "spreadsheet heading": "Supplier_Sample_Name",
                "display name": "Supplier Sample Name",
                "filter type": "none"
              },
              {
                "name": "lane_id",
                "display": true,
                "order": 4,
                "spreadsheet heading": "Lane_ID",
                "display name": "Lane ID",
                "filter type": "none"
              }
            ]
          },
          {
            "name": "Study Identifiers",
            "fields": [
              {
                "name": "study_name",
                "display": true,
                "order": 5,
                "spreadsheet heading": "Study_Name",
                "display name": "Study Name",
                "filter type": "none"
              },
              {
                "name": "study_ref",
                "display": true,
                "order": 6,
                "spreadsheet heading": "Study_Reference",
                "display name": "Study Reference",
                "filter type": "none"
              },
              {
                "name": "submitting_institution",
                "display": true,
                "order": 11,
                "spreadsheet heading": "Submitting_Institution",
                "display name": "Submitting Institution",
                "filter type": "discrete"
              }
            ]
          },
          {
            "name": "Collection Information",
            "fields": [
              {
                "name": "selection_random",
                "display": true,
                "order": 7,
                "spreadsheet heading": "Selection_Random",
                "display name": "Selection Random",
                "filter type": "discrete"
              },
              {
                "name": "country",
                "display": true,
                "order": 8,
                "spreadsheet heading": "Country",
                "display name": "Country",
                "filter type": "discrete"
              },
              {
                "name": "county_state",
                "display": true,
                "order": 9,
                "spreadsheet heading": "County/state",
                "display name": "County/state",
                "filter type": "discrete"
              },
              {
                "name": "city",
                "display": true,
                "order": 10,
                "spreadsheet heading": "City",
                "display name": "City",
                "filter type": "discrete"
              },
              {
                "name": "collection_year",
                "display": true,
                "order": 12,
                "spreadsheet heading": "Collection_year",
                "display name": "Collection year",
                "filter type": "numeric"
              },
              {
                "name": "collection_month",
                "display": true,
                "order": 13,
                "spreadsheet heading": "Collection_month",
                "display name": "Collection month",
                "filter type": "discrete"
              },
              {
                "name": "collection_day",
                "display": true,
                "order": 14,
                "spreadsheet heading": "Collection_day",
                "display name": "Collection day",
                "filter type": "discrete"
              }
            ]
          },
          {
            "name": "Host Information",
            "fields": [
              {
                "name": "host_species",
                "display": true,
                "order": 15,
                "spreadsheet heading": "Host_species",
                "display name": "Host species",
                "filter type": "discrete"
              },
              {
                "name": "gender",
                "display": true,
                "order": 16,
                "spreadsheet heading": "Gender",
                "display name": "Gender",
                "filter type": "discrete"
              },
              {
                "name": "age_group",
                "display": true,
                "order": 17,
                "spreadsheet heading": "Age_group",
                "display name": "Age group",
                "filter type": "discrete"
              },
              {
                "name": "age_years",
                "display": true,
                "order": 18,
                "spreadsheet heading": "Age_years",
                "display name": "Age years",
                "filter type": "numeric"
              },
              {
                "name": "age_months",
                "display": true,
                "order": 19,
                "spreadsheet heading": "Age_months",
                "display name": "Age months",
                "filter type": "numeric"
              },
              {
                "name": "age_weeks",
                "display": true,
                "order": 20,
                "spreadsheet heading": "Age_weeks",
                "display name": "Age weeks",
                "filter type": "numeric"
              },
              {
                "name": "age_days",
                "display": true,
                "order": 21,
                "spreadsheet heading": "Age_days",
                "display name": "Age days",
                "filter type": "numeric"
              },
              {
                "name": "host_status",
                "display": true,
                "order": 22,
                "spreadsheet heading": "Host_status",
                "display name": "Host status",
                "filter type": "discrete"
              },
              {
                "name": "disease_type",
                "display": true,
                "order": 23,
                "spreadsheet heading": "Disease_type",
                "display name": "Disease type",
                "filter type": "discrete"
              },
              {
                "name": "disease_onset",
                "display": true,
                "order": 24,
                "spreadsheet heading": "Disease_onset",
                "display name": "Disease onset",
                "filter type": "discrete"
              },
              {
                "name": "isolation_source",
                "display": true,
                "order": 25,
                "spreadsheet heading": "Isolation_source",
                "display name": "Isolation source",
                "filter type": "discrete"
              },
              {
                "name": "infection_during_pregnancy",
                "display": true,
                "order": 28,
                "spreadsheet heading": "Infection_during_pregnancy",
                "display name": "Infection during pregnancy",
                "filter type": "discrete"
              },
              {
                "name": "maternal_infection_type",
                "display": true,
                "order": 29,
                "spreadsheet heading": "Maternal_infection_type",
                "display name": "Maternal infection type",
                "filter type": "discrete"
              },
              {
                "name": "gestational_age_weeks",
                "display": true,
                "order": 30,
                "spreadsheet heading": "Gestational_age_weeks",
                "display name": "Gestational age weeks",
                "filter type": "numeric"
              },
              {
                "name": "birth_weight_gram",
                "display": true,
                "order": 31,
                "spreadsheet heading": "Birthweight_gram",
                "display name": "Birth weight gram",
                "filter type": "numeric"
              },
              {
                "name": "apgar_score",
                "display": true,
                "order": 32,
                "spreadsheet heading": "Apgar_score",
                "display name": "Apgar score",
                "filter type": "numeric"
              }
            ]
          },
          {
            "name": "Serotyping",
            "fields": [
              {
                "name": "serotype",
                "display": true,
                "order": 26,
                "spreadsheet heading": "Serotype",
                "display name": "Serotype",
                "filter type": "discrete"
              },
              {
                "name": "serotype_method",
                "display": true,
                "order": 27,
                "spreadsheet heading": "Serotype_method",
                "display name": "Serotype method",
                "filter type": "discrete"
              }
            ]
          },
          {
            "name": "Antimicrobial Susceptibility",
            "fields": [
              {
                "name": "ceftizoxime",
                "display": true,
                "order": 33,
                "spreadsheet heading": "Ceftizoxime",
                "display name": "Ceftizoxime",
                "filter type": "discrete"
              },
              {
                "name": "ceftizoxime_method",
                "display": true,
                "order": 34,
                "spreadsheet heading": "Ceftizoxime_method",
                "display name": "Ceftizoxime method",
                "filter type": "discrete"
              },
              {
                "name": "cefoxitin",
                "display": true,
                "order": 35,
                "spreadsheet heading": "Cefoxitin",
                "display name": "Cefoxitin",
                "filter type": "discrete"
              },
              {
                "name": "cefoxitin_method",
                "display": true,
                "order": 36,
                "spreadsheet heading": "Cefoxitin_method",
                "display name": "Cefoxitin method",
                "filter type": "discrete"
              },
              {
                "name": "cefotaxime",
                "display": true,
                "order": 37,
                "spreadsheet heading": "Cefotaxime",
                "display name": "Cefotaxime",
                "filter type": "discrete"
              },
              {
                "name": "cefotaxime_method",
                "display": true,
                "order": 38,
                "spreadsheet heading": "Cefotaxime_method",
                "display name": "Cefotaxime method",
                "filter type": "discrete"
              },
              {
                "name": "cefazolin",
                "display": true,
                "order": 39,
                "spreadsheet heading": "Cefazolin",
                "display name": "Cefazolin",
                "filter type": "discrete"
              },
              {
                "name": "cefazolin_method",
                "display": true,
                "order": 40,
                "spreadsheet heading": "Cefazolin_method",
                "display name": "Cefazolin method",
                "filter type": "discrete"
              },
              {
                "name": "ampicillin",
                "display": true,
                "order": 41,
                "spreadsheet heading": "Ampicillin",
                "display name": "Ampicillin",
                "filter type": "discrete"
              },
              {
                "name": "ampicillin_method",
                "display": true,
                "order": 42,
                "spreadsheet heading": "Ampicillin_method",
                "display name": "Ampicillin method",
                "filter type": "discrete"
              },
              {
                "name": "penicillin",
                "display": true,
                "order": 43,
                "spreadsheet heading": "Penicillin",
                "display name": "Penicillin",
                "filter type": "discrete"
              },
              {
                "name": "penicillin_method",
                "display": true,
                "order": 44,
                "spreadsheet heading": "Penicillin_method",
                "display name": "Penicillin method",
                "filter type": "discrete"
              },
              {
                "name": "erythromycin",
                "display": true,
                "order": 45,
                "spreadsheet heading": "Erythromycin",
                "display name": "Erythromycin",
                "filter type": "discrete"
              },
              {
                "name": "erythromycin_method",
                "display": true,
                "order": 46,
                "spreadsheet heading": "Erythromycin_method",
                "display name": "Erythromycin method",
                "filter type": "discrete"
              },
              {
                "name": "clindamycin",
                "display": true,
                "order": 47,
                "spreadsheet heading": "Clindamycin",
                "display name": "Clindamycin",
                "filter type": "discrete"
              },
              {
                "name": "clindamycin_method",
                "display": true,
                "order": 48,
                "spreadsheet heading": "Clindamycin_method",
                "display name": "Clindamycin method",
                "filter type": "discrete"
              },
              {
                "name": "tetracycline",
                "display": true,
                "order": 49,
                "spreadsheet heading": "Tetracycline",
                "display name": "Tetracycline",
                "filter type": "discrete"
              },
              {
                "name": "tetracycline_method",
                "display": true,
                "order": 50,
                "spreadsheet heading": "Tetracycline_method",
                "display name": "Tetracycline method",
                "filter type": "discrete"
              },
              {
                "name": "levofloxacin",
                "display": true,
                "order": 51,
                "spreadsheet heading": "Levofloxacin",
                "display name": "Levofloxacin",
                "filter type": "discrete"
              },
              {
                "name": "levofloxacin_method",
                "display": true,
                "order": 52,
                "spreadsheet heading": "Levofloxacin_method",
                "display name": "Levofloxacin method",
                "filter type": "discrete"
              },
              {
                "name": "ciprofloxacin",
                "display": true,
                "order": 53,
                "spreadsheet heading": "Ciprofloxacin",
                "display name": "Ciprofloxacin",
                "filter type": "discrete"
              },
              {
                "name": "ciprofloxacin_method",
                "display": true,
                "order": 54,
                "spreadsheet heading": "Ciprofloxacin_method",
                "display name": "Ciprofloxacin method",
                "filter type": "discrete"
              },
              {
                "name": "daptomycin",
                "display": true,
                "order": 55,
                "spreadsheet heading": "Daptomycin",
                "display name": "Daptomycin",
                "filter type": "discrete"
              },
              {
                "name": "daptomycin_method",
                "display": true,
                "order": 56,
                "spreadsheet heading": "Daptomycin_method",
                "display name": "Daptomycin method",
                "filter type": "discrete"
              },
              {
                "name": "vancomycin",
                "display": true,
                "order": 57,
                "spreadsheet heading": "Vancomycin",
                "display name": "Vancomycin",
                "filter type": "discrete"
              },
              {
                "name": "vancomycin_method",
                "display": true,
                "order": 58,
                "spreadsheet heading": "Vancomycin_method",
                "display name": "Vancomycin method",
                "filter type": "discrete"
              },
              {
                "name": "linezolid",
                "display": true,
                "order": 59,
                "spreadsheet heading": "Linezolid",
                "display name": "Linezolid",
                "filter type": "discrete"
              },
              {
                "name": "linezolid_method",
                "display": true,
                "order": 60,
                "spreadsheet heading": "Linezolid_method",
                "display name": "Linezolid method",
                "filter type": "discrete"
              }
            ]
          }
        ]
      },
      "in silico": {
        "categories": [
          {
            "name": "Sample Identifiers",
            "fields": [
              {
                "name": "lane_id",
                "display": false,
                "spreadsheet heading": "Sample_id",
                "display name": "Sample id"
              }
            ]
          },
          {
            "name": "Serotype",
            "fields": [
              {
                "name": "cps_type",
                "display": true,
                "order": 1,
                "spreadsheet heading": "cps_type",
                "display name": "cps type",
                "filter type": "discrete"
              }
            ]
          },
          {
            "name": "MLST and Allele Frequencies",
            "fields": [
              {
                "name": "ST",
                "display": true,
                "order": 2,
                "spreadsheet heading": "ST",
                "display name": "ST",
                "filter type": "discrete"
              },
              {
                "name": "adhP",
                "display": true,
                "order": 3,
                "spreadsheet heading": "adhP",
                "display name": "adhP",
                "filter type": "discrete"
              },
              {
                "name": "pheS",
                "display": true,
                "order": 4,
                "spreadsheet heading": "pheS",
                "display name": "pheS",
                "filter type": "discrete"
              },
              {
                "name": "atr",
                "display": true,
                "order": 5,
                "spreadsheet heading": "atr",
                "display name": "atr",
                "filter type": "discrete"
              },
              {
                "name": "glnA",
                "display": true,
                "order": 6,
                "spreadsheet heading": "glnA",
                "display name": "glnA",
                "filter type": "discrete"
              },
              {
                "name": "sdhA",
                "display": true,
                "order": 7,
                "spreadsheet heading": "sdhA",
                "display name": "sdhA",
                "filter type": "discrete"
              },
              {
                "name": "glcK",
                "display": true,
                "order": 8,
                "spreadsheet heading": "glcK",
                "display name": "glcK",
                "filter type": "discrete"
              },
              {
                "name": "tkt",
                "display": true,
                "order": 9,
                "spreadsheet heading": "tkt",
                "display name": "tkt",
                "filter type": "discrete"
              },
              {
                "name": "23S1",
                "display": true,
                "order": 10,
                "spreadsheet heading": "23S1",
                "display name": "23S1",
                "filter type": "discrete"
              },
              {
                "name": "23S3",
                "display": true,
                "order": 11,
                "spreadsheet heading": "23S3",
                "display name": "23S3",
                "filter type": "discrete"
              }
            ]
          },
          {
            "name": "AMR Alleles",
            "fields": [
              {
                "name": "AAC6APH2",
                "display": true,
                "order": 12,
                "spreadsheet heading": "AAC6APH2",
                "display name": "AAC6APH2",
                "filter type": "discrete"
              },
              {
                "name": "AADECC",
                "display": true,
                "order": 13,
                "spreadsheet heading": "AADECC",
                "display name": "AADECC",
                "filter type": "discrete"
              },
              {
                "name": "ANT6",
                "display": true,
                "order": 14,
                "spreadsheet heading": "ANT6",
                "display name": "ANT6",
                "filter type": "discrete"
              },
              {
                "name": "APH3III",
                "display": true,
                "order": 15,
                "spreadsheet heading": "APH3III",
                "display name": "APH3III",
                "filter type": "discrete"
              },
              {
                "name": "APH3OTHER",
                "display": true,
                "order": 16,
                "spreadsheet heading": "APH3OTHER",
                "display name": "APH3OTHER",
                "filter type": "discrete"
              },
              {
                "name": "CATPC194",
                "display": true,
                "order": 17,
                "spreadsheet heading": "CATPC194",
                "display name": "CATPC194",
                "filter type": "discrete"
              },
              {
                "name": "CATQ",
                "display": true,
                "order": 18,
                "spreadsheet heading": "CATQ",
                "display name": "CATQ",
                "filter type": "discrete"
              },
              {
                "name": "ERMA",
                "display": true,
                "order": 19,
                "spreadsheet heading": "ERMA",
                "display name": "ERMA",
                "filter type": "discrete"
              },
              {
                "name": "ERMB",
                "display": true,
                "order": 20,
                "spreadsheet heading": "ERMB",
                "display name": "ERMB",
                "filter type": "discrete"
              },
              {
                "name": "ERMT",
                "display": true,
                "order": 21,
                "spreadsheet heading": "ERMT",
                "display name": "ERMT",
                "filter type": "discrete"
              },
              {
                "name": "LNUB",
                "display": true,
                "order": 22,
                "spreadsheet heading": "LNUB",
                "display name": "LNUB",
                "filter type": "discrete"
              },
              {
                "name": "LNUC",
                "display": true,
                "order": 23,
                "spreadsheet heading": "LNUC",
                "display name": "LNUC",
                "filter type": "discrete"
              },
              {
                "name": "LSAC",
                "display": true,
                "order": 24,
                "spreadsheet heading": "LSAC",
                "display name": "LSAC",
                "filter type": "discrete"
              },
              {
                "name": "MEFA",
                "display": true,
                "order": 25,
                "spreadsheet heading": "MEFA",
                "display name": "MEFA",
                "filter type": "discrete"
              },
              {
                "name": "MPHC",
                "display": true,
                "order": 26,
                "spreadsheet heading": "MPHC",
                "display name": "MPHC",
                "filter type": "discrete"
              },
              {
                "name": "MSRA",
                "display": true,
                "order": 27,
                "spreadsheet heading": "MSRA",
                "display name": "MSRA",
                "filter type": "discrete"
              },
              {
                "name": "MSRD",
                "display": true,
                "order": 28,
                "spreadsheet heading": "MSRD",
                "display name": "MSRD",
                "filter type": "discrete"
              },
              {
                "name": "FOSA",
                "display": true,
                "order": 29,
                "spreadsheet heading": "FOSA",
                "display name": "FOSA",
                "filter type": "discrete"
              },
              {
                "name": "GYRA",
                "display": true,
                "order": 30,
                "spreadsheet heading": "GYRA",
                "display name": "GYRA",
                "filter type": "discrete"
              },
              {
                "name": "PARC",
                "display": true,
                "order": 31,
                "spreadsheet heading": "PARC",
                "display name": "PARC",
                "filter type": "discrete"
              },
              {
                "name": "RPOBGBS_1",
                "display": true,
                "order": 32,
                "spreadsheet heading": "RPOBGBS-1",
                "display name": "RPOBGBS-1",
                "filter type": "discrete"
              },
              {
                "name": "RPOBGBS_2",
                "display": true,
                "order": 33,
                "spreadsheet heading": "RPOBGBS-2",
                "display name": "RPOBGBS-2",
                "filter type": "discrete"
              },
              {
                "name": "RPOBGBS_3",
                "display": true,
                "order": 34,
                "spreadsheet heading": "RPOBGBS-3",
                "display name": "RPOBGBS-3",
                "filter type": "discrete"
              },
              {
                "name": "RPOBGBS_4",
                "display": true,
                "order": 35,
                "spreadsheet heading": "RPOBGBS-4",
                "display name": "RPOBGBS-4",
                "filter type": "discrete"
              },
              {
                "name": "SUL2",
                "display": true,
                "order": 36,
                "spreadsheet heading": "SUL2",
                "display name": "SUL2",
                "filter type": "discrete"
              },
              {
                "name": "TETB",
                "display": true,
                "order": 37,
                "spreadsheet heading": "TETB",
                "display name": "TETB",
                "filter type": "discrete"
              },
              {
                "name": "TETL",
                "display": true,
                "order": 38,
                "spreadsheet heading": "TETL",
                "display name": "TETL",
                "filter type": "discrete"
              },
              {
                "name": "TETM",
                "display": true,
                "order": 39,
                "spreadsheet heading": "TETM",
                "display name": "TETM",
                "filter type": "discrete"
              },
              {
                "name": "TETO",
                "display": true,
                "order": 40,
                "spreadsheet heading": "TETO",
                "display name": "TETO",
                "filter type": "discrete"
              },
              {
                "name": "TETS",
                "display": true,
                "order": 41,
                "spreadsheet heading": "TETS",
                "display name": "TETS",
                "filter type": "discrete"
              }
            ]
          },
          {
            "name": "Surface Proteins",
            "fields": [
              {
                "name": "ALP1",
                "display": true,
                "order": 42,
                "spreadsheet heading": "ALP1",
                "display name": "ALP1",
                "filter type": "discrete"
              },
              {
                "name": "ALP23",
                "display": true,
                "order": 43,
                "spreadsheet heading": "ALP23",
                "display name": "ALP23",
                "filter type": "discrete"
              },
              {
                "name": "ALPHA",
                "display": true,
                "order": 44,
                "spreadsheet heading": "ALPHA",
                "display name": "ALPHA",
                "filter type": "discrete"
              },
              {
                "name": "HVGA",
                "display": true,
                "order": 45,
                "spreadsheet heading": "HVGA",
                "display name": "HVGA",
                "filter type": "discrete"
              },
              {
                "name": "PI1",
                "display": true,
                "order": 46,
                "spreadsheet heading": "PI1",
                "display name": "PI1",
                "filter type": "discrete"
              },
              {
                "name": "PI2A1",
                "display": true,
                "order": 47,
                "spreadsheet heading": "PI2A1",
                "display name": "PI2A1",
                "filter type": "discrete"
              },
              {
                "name": "PI2A2",
                "display": true,
                "order": 48,
                "spreadsheet heading": "PI2A2",
                "display name": "PI2A2",
                "filter type": "discrete"
              },
              {
                "name": "PI2B",
                "display": true,
                "order": 49,
                "spreadsheet heading": "PI2B",
                "display name": "PI2B",
                "filter type": "discrete"
              },
              {
                "name": "RIB",
                "display": true,
                "order": 50,
                "spreadsheet heading": "RIB",
                "display name": "RIB",
                "filter type": "discrete"
              },
              {
                "name": "SRR1",
                "display": true,
                "order": 51,
                "spreadsheet heading": "SRR1",
                "display name": "SRR1",
                "filter type": "discrete"
              },
              {
                "name": "SRR2",
                "display": true,
                "order": 52,
                "spreadsheet heading": "SRR2",
                "display name": "SRR2",
                "filter type": "discrete"
              }
            ]
          },
          {
            "name": "AMR Variants",
            "fields": [
              {
                "name": "twenty_three_S1_variant",
                "display": true,
                "order": 53,
                "spreadsheet heading": "23S1_variant",
                "display name": "23S1 variant",
                "filter type": "discrete"
              },
              {
                "name": "twenty_three_S3_variant",
                "display": true,
                "order": 54,
                "spreadsheet heading": "23S3_variant",
                "display name": "23S3 variant",
                "filter type": "discrete"
              },
              {
                "name": "GYRA_variant",
                "display": true,
                "order": 55,
                "spreadsheet heading": "GYRA_variant",
                "display name": "GYRA variant",
                "filter type": "discrete"
              },
              {
                "name": "PARC_variant",
                "display": true,
                "order": 56,
                "spreadsheet heading": "PARC_variant",
                "display name": "PARC variant",
                "filter type": "discrete"
              },
              {
                "name": "RPOBGBS_1_variant",
                "display": true,
                "order": 57,
                "spreadsheet heading": "RPOBGBS-1_variant",
                "display name": "RPOBGBS-1 variant",
                "filter type": "discrete"
              },
              {
                "name": "RPOBGBS_2_variant",
                "display": true,
                "order": 58,
                "spreadsheet heading": "RPOBGBS-2_variant",
                "display name": "RPOBGBS-2 variant",
                "filter type": "discrete"
              },
              {
                "name": "RPOBGBS_3_variant",
                "display": true,
                "order": 59,
                "spreadsheet heading": "RPOBGBS-3_variant",
                "display name": "RPOBGBS-3 variant",
                "filter type": "discrete"
              },
              {
                "name": "RPOBGBS_4_variant",
                "display": true,
                "order": 60,
                "spreadsheet heading": "RPOBGBS-4_variant",
                "display name": "RPOBGBS-4 variant",
                "filter type": "discrete"
              }
            ]
          }
        ]
      }
    });
}

export function getDistinctColumnValues(columns, fetch) {
  const { payload } = columns.reduce((accum, column) => {
      const { payload, dataTypeToPayloadIndex } = accum;
      let payloadIndex = dataTypeToPayloadIndex[column.dataType];
      if (payloadIndex === undefined) {
        payloadIndex = payload.length;
        dataTypeToPayloadIndex[column.dataType] = payloadIndex;
        payload.push({ "field type": column.dataType, "field names": [] });
      }
      payload[payloadIndex]["field names"].push(column.name);
      return accum;
    }, { payload: [], dataTypeToPayloadIndex: {} }
  );

  return fetchDashboardApiResource("get_distinct_values", "distinct values", fetch, {
    method: HTTP_POST,
    headers: JSON_HEADERS,
    body: JSON.stringify(payload)
  });
}

export function getInstitutions(fetch) {
  return fetchDashboardApiResource(
    "get_institutions", "institutions", fetch);
}

export function getSampleMetadata({
  instKeyBatchDatePairs,
  filter,
  columns,
  numRows,
  startRow,
  asCsv
},
fetch
) {
  const payload = {
    "sample filters": {
      batches: transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs)
    }
  };

  addFiltersToPayload({ ...filter, payload });

  if (Number.isInteger(numRows)) {
    payload["num rows"] = numRows;
  }
  if (Number.isInteger(startRow)) {
    payload["start row"] = startRow;
  }

  if (asCsv === true) {
    payload["as csv"] = true;
    return fetch(`${DASHBOARD_API_ENDPOINT}/get_metadata`, {
      method: HTTP_POST,
      headers: JSON_HEADERS,
      body: JSON.stringify(payload)
    })
      .then((response) =>
        response.ok ? response.blob() : Promise.reject(`${response.status} ${response.statusText}`))
      .catch((err) =>
        handleFetchError(err, "get_metadata"));
  }
  else {
    addColumnsToPayload(columns, payload);
  }

  return fetchDashboardApiResource(
    "get_metadata", null, fetch, {
      method: HTTP_POST,
      headers: JSON_HEADERS,
      body: JSON.stringify(payload)
    });
}

export function getUserDetails(fetch) {
  return fetchDashboardApiResource(
    "get_user_details", "user_details", fetch);
}

function getProjectProgressData(fetch) {
  return fetchDashboardApiResource(
    "get_progress", "progress_graph", fetch);
}

function getSequencingStatus(fetch) {
  return fetchDashboardApiResource(
    "sequencing_status_summary", "sequencing_status", fetch);
}

function getPipelineStatus(fetch) {
  return fetchDashboardApiResource(
    "pipeline_status_summary", "pipeline_status", fetch);
}

function fetchDashboardApiResource(endpoint, resourceKey, fetch, fetchOptions) {
  return (fetchOptions ?
    fetch(`${DASHBOARD_API_ENDPOINT}/${endpoint}`, fetchOptions) :
    fetch(`${DASHBOARD_API_ENDPOINT}/${endpoint}`)
  )
    .then((response) =>
      response.ok ? response.json() : Promise.reject(`${response.status} ${response.statusText}`))
    .then((payload) => resourceKey ? payload?.[resourceKey] : payload)
    .catch((err) => handleFetchError(err, endpoint, resourceKey));
}

function handleFetchError(err = FETCH_ERROR_UNKNOWN, endpoint, resourceKey) {
  if (err.startsWith?.(FETCH_ERROR_PATTER_NOT_FOUND)) {
    return Promise.resolve();
  }
  console.error(resourceKey ?
    `Error while fetching resource w/ key "${resourceKey}" from endpoint ${endpoint}: ${err}` :
    `Error while fetching resource from endpoint ${endpoint}: ${err}`
  );
  return Promise.reject(err);
}

function collateInstitutionStatus({
  institutions,
  batches,
  sequencingStatus,
  pipelineStatus
}) {
  return Object.keys(institutions)
    .map((institutionKey) => ({
      name: institutions[institutionKey].name,
      batches: batches[institutionKey],
      sequencingStatus: sequencingStatus[institutionKey],
      pipelineStatus: {
        sequencedSuccess: sequencingStatus[institutionKey].success,
        ...pipelineStatus[institutionKey]
      },
      key: institutionKey
    }));
}

function prepareBulkDownloadPayload({
  instKeyBatchDatePairs,
  filter,
  assemblies,
  annotations,
  reads
}) {
  const payload = {
    "sample filters": {
      batches: transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs)
    },
    assemblies,
    annotations,
    reads
  };

  addFiltersToPayload({ ...filter, payload });

  return payload;
}

function addColumnsToPayload(columns = {}, payload) {
  DATA_TYPES.forEach((dataType) => {
    if (columns[dataType]?.length) {
      payload[`${dataType} columns`] = columns[dataType];
    }
    else {
      payload[dataType] = false;
    }
  });
}

function addFiltersToPayload({ filterState = {}, payload, distinctColumnValues }) {
  DATA_TYPES.forEach((dataType) => {
    const filterStateForDataType = filterState[dataType] || {};
    const columnNames = Object.keys(filterStateForDataType);
    if (columnNames.length) {
      const payloadFilter = {};
      columnNames.forEach((columnName) => {
        if (filterStateForDataType[columnName].exclude) {
          const valuesToExclude = new Set(filterStateForDataType[columnName].values);
          payloadFilter[columnName] = distinctColumnValues[dataType][columnName].filter((columnValue) =>
            !valuesToExclude.has(columnValue));
        }
        else {
          payloadFilter[columnName] = filterStateForDataType[columnName].values;
        }
      });
      payload["sample filters"][dataType] = payloadFilter;
    }
  });
}

export function transformInstKeyBatchDatePairsIntoPayload(instKeyBatchDatePairs = []) {
  return instKeyBatchDatePairs.map(([instKey, batchDate]) => (
    { "institution key": instKey, "batch date": batchDate }
  ));
}
