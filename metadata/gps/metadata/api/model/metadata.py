from dataclasses import dataclass

# THIS FILE IS AUTO-GENERATED BY update_config_files.py, DO NOT EDIT MANUALLY!


@dataclass
class Metadata:
    sample_name: str  # mandatory; contains illegal characters
    sanger_sample_id: str  # mandatory; must not contain illegal characters
    public_name: str  # mandatory; contains illegal characters
    study_name: str  # optional; contains illegal characters
    submitting_institution: str  # mandatory
    selection_random: str  # optional
    country: str  # optional
    region: str  # optional
    city: str  # optional
    facility_where_collected: str  # optional
    month_collection: str  # optional
    year_collection: str  # optional; must be a YYYY format year or '_'
    gender: str  # optional
    age_years: str  # optional; should be a valid 1 to 3 digit number
    age_months: str  # optional; should be a valid 1 to 4 digit number
    age_days: str  # optional; should be a valid 1 to 4 digit number
    clinical_manifestation: str  # optional
    source: str  # optional
    HIV_status: str  # optional
    underlying_conditions: str  # optional
    phenotypic_serotype_method: str  # optional
    phenotypic_serotype: str  # optional; contains illegal characters
    sequence_type: str  # optional; contains illegal characters
    penicillin: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_penicillin: str  # optional
    amoxicillin: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_amoxicillin: str  # optional
    cefotaxime: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_cefotaxime: str  # optional
    ceftriaxone: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_ceftriaxone: str  # optional
    cefuroxime: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_cefuroxime: str  # optional
    Meropenem: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_meropenem: str  # optional
    erythromycin: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_erythromycin: str  # optional
    clindamycin: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_clindamycin: str  # optional
    trim_sulfa: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_trim_sulfa: str  # optional
    vancomycin: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_vancomycin: str  # optional
    linezolid: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_linezolid: str  # optional
    ciprofloxacin: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_ciprofloxacin: str  # optional
    chloramphenicol: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_chloramphenicol: str  # optional
    tetracycline: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_tetracycline: str  # optional
    levofloxacin: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_levofloxacin: str  # optional
    synercid: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_synercid: str  # optional
    rifampin: str  # optional; should be a valid floating point number; can start with '>','<', '>=' or '<=' and optionally end with units "mm" or "µg/ml" ('u' permitted in place of 'µ'); or alternatively S, I, or R
    AST_method_rifampin: str  # optional
    aroe: str  # optional
    gdh: str  # optional
    gki: str  # optional
    recp: str  # optional
    spi: str  # optional
    xpt: str  # optional
    ddl: str  # optional
    comments: str  # optional
    vaccine_period: str  # optional
    intro_year: str  # optional
    PCV_type: str  # optional; should start with 'PCV' followed by a number, or '_'
    resolution: str  # optional
