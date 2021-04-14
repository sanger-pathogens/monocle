from dataclasses import dataclass


@dataclass
class Metadata:
    sanger_sample_id: str
    lane_id: str
    submitting_institution: str
    supplier_sample_name: str
    public_name: str
    host_status: str
    study_name: str
    study_ref: str
    selection_random: str
    country: str
    county_state: str
    city: str
    collection_year: str
    collection_month: str
    collection_day: str
    host_species: str
    gender: str
    age_group: str
    age_years: str
    age_months: str
    age_weeks: str
    age_days: str
    disease_type: str
    disease_onset: str
    isolation_source: str
    serotype: str
    serotype_method: str
    infection_during_pregnancy: str
    maternal_infection_type: str
    gestational_age_weeks: str
    birth_weight_gram: str
    apgar_score: str
    ceftizoxime: str
    ceftizoxime_method: str
    cefoxitin: str
    cefoxitin_method: str
    cefotaxime: str
    cefotaxime_method: str
    cefazolin: str
    cefazolin_method: str
    ampicillin: str
    ampicillin_method: str
    penicillin: str
    penicillin_method: str
    erythromycin: str
    erythromycin_method: str
    clindamycin: str
    clindamycin_method: str
    tetracycline: str
    tetracycline_method: str
    levofloxacin: str
    levofloxacin_method: str
    ciprofloxacin: str
    ciprofloxacin_method: str
    daptomycin: str
    daptomycin_method: str
    vancomycin: str
    vancomycin_method: str
    linezolid: str
    linezolid_method: str
    additional_metadata: str
