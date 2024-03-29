from dataclasses import dataclass

# THIS FILE IS AUTO-GENERATED BY update_config_files.py, DO NOT EDIT MANUALLY!


@dataclass
class Metadata:
    public_name: str  # mandatory; contains illegal characters
    sanger_sample_id: str  # mandatory; contains illegal characters
    supplier_sample_name: str  # mandatory; contains illegal characters
    lane_id: str  # optional; is not a recognised lane Id format
    study_name: str  # optional; contains illegal characters
    study_ref: str  # optional; must be a comma-separated list of study references, e.g. PMID: 1234567, PMID: 23456789
    submitting_institution: str  # mandatory
    selection_random: str  # optional
    country: str  # optional
    county_state: str  # optional
    city: str  # optional
    collection_year: str  # optional; must be a YYYY format year
    collection_month: str  # optional; must be a MM format month
    collection_day: str  # optional; must be a DD format day
    host_species: str  # optional
    gender: str  # optional
    age_group: str  # optional
    age_years: str  # optional; should be a valid 1 to 3 digit number
    age_months: str  # optional; should be a valid 1 to 4 digit number
    age_weeks: str  # optional; should be a valid 1 to 4 digit number
    age_days: str  # optional; should be a valid 1 to 5 digit number
    host_status: str  # optional
    disease_type: str  # optional
    disease_onset: str  # optional
    isolation_source: str  # optional
    infection_during_pregnancy: str  # optional
    maternal_infection_type: str  # optional
    gestational_age_weeks: str  # optional; should be a valid 1 to 3 digit number
    birth_weight_gram: str  # optional; should be a valid 1 to 7 digit number
    apgar_score: str  # optional; should be a valid number between 0 and 10
    serotype: str  # optional
    serotype_method: str  # optional; is not in the list of legal options (latex agglutination, Lancefield, PCR, other)
    ceftizoxime: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    ceftizoxime_method: str  # optional
    cefoxitin: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    cefoxitin_method: str  # optional
    cefotaxime: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    cefotaxime_method: str  # optional
    cefazolin: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    cefazolin_method: str  # optional
    ampicillin: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    ampicillin_method: str  # optional
    penicillin: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    penicillin_method: str  # optional
    erythromycin: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    erythromycin_method: str  # optional
    clindamycin: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    clindamycin_method: str  # optional
    tetracycline: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    tetracycline_method: str  # optional
    levofloxacin: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    levofloxacin_method: str  # optional
    ciprofloxacin: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    ciprofloxacin_method: str  # optional
    daptomycin: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    daptomycin_method: str  # optional
    vancomycin: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    vancomycin_method: str  # optional
    linezolid: str  # optional; should be a valid floating point number, optionally with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    linezolid_method: str  # optional
