from metadata.api.model.in_silico_data import InSilicoData
from metadata.api.model.metadata import Metadata
from metadata.api.model.qc_data import QCData

""" Some test data to use in unit tests... """

TEST_SAMPLE_1_DICT = dict(
    lane_id="2000_2#10",
    submitting_institution="UniversityA",
    supplier_sample_name="SUPPLIER_1",
    public_name="PUB_NAME_1",
    host_status="CARRIAGE",
    study_name="My_study1",
    study_ref="5201",
    selection_random="Y",
    country="UK",
    county_state="Cambridgeshire",
    city="Cambridge",
    collection_year="2019",
    collection_month="12",
    collection_day="05",
    host_species="human",
    gender="M",
    age_group="adult",
    age_years="35",
    age_months="10",
    age_weeks="2",
    age_days="2",
    disease_type="GBS",
    disease_onset="EOD",
    isolation_source="blood",
    serotype="IV",
    serotype_method="PCR",
    infection_during_pregnancy="N",
    maternal_infection_type="oral",
    gestational_age_weeks="10",
    birth_weight_gram="400",
    apgar_score="10",
    ceftizoxime="1",
    ceftizoxime_method="method1",
    cefoxitin="2",
    cefoxitin_method="method2",
    cefotaxime="3",
    cefotaxime_method="method3",
    cefazolin="4",
    cefazolin_method="method4",
    ampicillin="5",
    ampicillin_method="method5",
    penicillin="6",
    penicillin_method="method6",
    erythromycin="7",
    erythromycin_method="method7",
    clindamycin="8",
    clindamycin_method="method8",
    tetracycline="9",
    tetracycline_method="method9",
    levofloxacin="10",
    levofloxacin_method="method10",
    ciprofloxacin="11",
    ciprofloxacin_method="method11",
    daptomycin="12",
    daptomycin_method="method12",
    vancomycin="13",
    vancomycin_method="method13",
    linezolid="14",
    linezolid_method="method14",
    sanger_sample_id="60",
)

TEST_SAMPLE_1 = Metadata(**TEST_SAMPLE_1_DICT)

TEST_SAMPLE_2_DICT = dict(
    lane_id="2000_2#11",
    submitting_institution="UniversityB",
    supplier_sample_name="SUPPLIER_2",
    public_name="PUB_NAME_2",
    host_status="INVASIVE",
    study_name="My_stud2",
    study_ref="5202",
    selection_random="N",
    country="US",
    county_state="California",
    city="Los Angeles",
    collection_year="2020",
    collection_month="10",
    collection_day="07",
    host_species="chimp",
    gender="N",
    age_group="adult",
    age_years="45",
    age_months="4",
    age_weeks="1",
    age_days="1",
    disease_type="other",
    disease_onset="LOD",
    isolation_source="skin",
    serotype="IX",
    serotype_method="PCR2",
    infection_during_pregnancy="Y",
    maternal_infection_type="other",
    gestational_age_weeks="12",
    birth_weight_gram="500",
    apgar_score="3",
    ceftizoxime="11",
    ceftizoxime_method="method11",
    cefoxitin="12",
    cefoxitin_method="method12",
    cefotaxime="13",
    cefotaxime_method="method13",
    cefazolin="14",
    cefazolin_method="method14",
    ampicillin="15",
    ampicillin_method="method15",
    penicillin="16",
    penicillin_method="method16",
    erythromycin="17",
    erythromycin_method="method17",
    clindamycin="18",
    clindamycin_method="method18",
    tetracycline="19",
    tetracycline_method="method19",
    levofloxacin="20",
    levofloxacin_method="method20",
    ciprofloxacin="21",
    ciprofloxacin_method="method21",
    daptomycin="22",
    daptomycin_method="method22",
    vancomycin="23",
    vancomycin_method="method23",
    linezolid="24",
    linezolid_method="method24",
    sanger_sample_id="60",
)

TEST_SAMPLE_2 = Metadata(**TEST_SAMPLE_2_DICT)

TEST_LANE_IN_SILICO_1_DICT = dict(
    lane_id="50000_2#282",
    cps_type="III",
    ST="ST-I",
    adhP="15",
    pheS="8",
    atr="4",
    glnA="4",
    sdhA="22",
    glcK="1",
    tkt="9",
    twenty_three_S1="pos",
    twenty_three_S3="pos",
    AAC6APH2="neg",
    AADECC="neg",
    ANT6="neg",
    APH3III="neg",
    APH3OTHER="neg",
    CATPC194="neg",
    CATQ="neg",
    ERMA="neg",
    ERMB="neg",
    ERMT="neg",
    LNUB="neg",
    LNUC="neg",
    LSAC="neg",
    MEFA="neg",
    MPHC="neg",
    MSRA="neg",
    MSRD="neg",
    FOSA="neg",
    GYRA="pos",
    PARC="pos",
    RPOBGBS_1="neg",
    RPOBGBS_2="neg",
    RPOBGBS_3="neg",
    RPOBGBS_4="neg",
    SUL2="neg",
    TETB="neg",
    TETL="neg",
    TETM="pos",
    TETO="neg",
    TETS="neg",
    ALP1="neg",
    ALP23="neg",
    ALPHA="neg",
    HVGA="pos",
    PI1="pos",
    PI2A1="neg",
    PI2A2="neg",
    PI2B="pos",
    RIB="pos",
    SRR1="neg",
    SRR2="pos",
    twenty_three_S1_variant="",
    twenty_three_S3_variant="",
    GYRA_variant="",
    PARC_variant="",
    RPOBGBS_1_variant="",
    RPOBGBS_2_variant="",
    RPOBGBS_3_variant="",
    RPOBGBS_4_variant="",
)

TEST_LANE_IN_SILICO_1 = InSilicoData(**TEST_LANE_IN_SILICO_1_DICT)

TEST_LANE_IN_SILICO_2_DICT = dict(
    lane_id="50000_2#287",
    cps_type="III",
    ST="ST-II",
    adhP="3",
    pheS="11",
    atr="0",
    glnA="16",
    sdhA="14",
    glcK="31",
    tkt="6",
    twenty_three_S1="pos",
    twenty_three_S3="pos",
    AAC6APH2="neg",
    AADECC="neg",
    ANT6="neg",
    APH3III="neg",
    APH3OTHER="neg",
    CATPC194="neg",
    CATQ="neg",
    ERMA="neg",
    ERMB="neg",
    ERMT="neg",
    LNUB="neg",
    LNUC="neg",
    LSAC="neg",
    MEFA="neg",
    MPHC="neg",
    MSRA="neg",
    MSRD="neg",
    FOSA="neg",
    GYRA="pos",
    PARC="pos",
    RPOBGBS_1="neg",
    RPOBGBS_2="neg",
    RPOBGBS_3="neg",
    RPOBGBS_4="neg",
    SUL2="neg",
    TETB="neg",
    TETL="neg",
    TETM="pos",
    TETO="neg",
    TETS="neg",
    ALP1="neg",
    ALP23="neg",
    ALPHA="neg",
    HVGA="pos",
    PI1="pos",
    PI2A1="neg",
    PI2A2="neg",
    PI2B="pos",
    RIB="pos",
    SRR1="neg",
    SRR2="pos",
    twenty_three_S1_variant="",
    twenty_three_S3_variant="",
    GYRA_variant="GYRA-T78Q,L55A",
    PARC_variant="PARC-Q17S",
    RPOBGBS_1_variant="",
    RPOBGBS_2_variant="",
    RPOBGBS_3_variant="",
    RPOBGBS_4_variant="",
)

TEST_LANE_IN_SILICO_2 = InSilicoData(**TEST_LANE_IN_SILICO_2_DICT)

TEST_LANE_QC_DATA_1_DICT = dict(
    lane_id="50000_2#282",
    rel_abun_sa="93.21",
)
TEST_LANE_QC_DATA_1 = QCData(**TEST_LANE_QC_DATA_1_DICT)

TEST_LANE_QC_DATA_2_DICT = dict(
    lane_id="50000_2#287",
    rel_abun_sa="68.58",
)
TEST_LANE_QC_DATA_2 = QCData(**TEST_LANE_QC_DATA_2_DICT)


TEST_UPLOAD_SAMPLE_1_DICT = dict(
    lane_id="50000_2#282",
    submitting_institution="Test Institution A",
    supplier_sample_name="EY70425",
    public_name="CD_XX_EW00001",
    host_status="invasive disease",
    study_name="TEST-stUDY NA_ME1 (123), [ABC] %.",
    study_ref="PMID: 1234567, PMID: 12345678",
    selection_random="yes",
    country="TestCountryA",
    county_state="State",
    city="London",
    collection_year="2014",
    collection_month="10",
    collection_day="2",
    host_species="human",
    gender="M",
    age_group="neonate",
    age_years="",
    age_months="",
    age_weeks="",
    age_days="",
    disease_type="bacteraemia",
    disease_onset="EOD",
    isolation_source="blood",
    serotype="V",
    serotype_method="PCR",
    infection_during_pregnancy="yes",
    maternal_infection_type="arthritis",
    gestational_age_weeks="12",
    birth_weight_gram="130",
    apgar_score="3",
    ceftizoxime="1.2",
    ceftizoxime_method="Etest",
    cefoxitin="10.334545",
    cefoxitin_method="disk diffusion",
    cefotaxime="100.4",
    cefotaxime_method="agar dilution",
    cefazolin="1000.5",
    cefazolin_method="agar dilution",
    ampicillin="10000.6",
    ampicillin_method="agar dilution",
    penicillin="100000.7",
    penicillin_method="agar dilution",
    erythromycin="20.8",
    erythromycin_method="agar dilution",
    clindamycin="70.4",
    clindamycin_method="agar dilution",
    tetracycline="0.3",
    tetracycline_method="agar dilution",
    levofloxacin="12.2",
    levofloxacin_method="agar dilution",
    ciprofloxacin="10.1",
    ciprofloxacin_method="agar dilution",
    daptomycin="10",
    daptomycin_method="agar dilution",
    vancomycin="100",
    vancomycin_method="agar dilution",
    linezolid="20",
    linezolid_method="agar dilution",
    sanger_sample_id="60",
)

TEST_UPLOAD_SAMPLE_2_DICT = dict(
    lane_id="50000_2#287",
    submitting_institution="Test Institution A",
    supplier_sample_name="EY_70601",
    public_name="CD_XX_EW00002",
    host_status="invasive disease",
    study_name="",
    study_ref="PMID: 12345678",
    selection_random="no",
    country="TestCountryA",
    county_state="",
    city="",
    collection_year="2014",
    collection_month="",
    collection_day="",
    host_species="human",
    gender="",
    age_group="adult",
    age_years="25",
    age_months="1",
    age_weeks="1",
    age_days="2",
    disease_type="bacteraemia",
    disease_onset="",
    isolation_source="blood",
    serotype="VI",
    serotype_method="latex agglutination, PCR",
    infection_during_pregnancy="no",
    maternal_infection_type="",
    gestational_age_weeks="",
    birth_weight_gram="",
    apgar_score="",
    ceftizoxime="S",
    ceftizoxime_method="",
    cefoxitin="I",
    cefoxitin_method="",
    cefotaxime="R",
    cefotaxime_method="",
    cefazolin="S",
    cefazolin_method="",
    ampicillin="S",
    ampicillin_method="",
    penicillin="S",
    penicillin_method="",
    erythromycin="S",
    erythromycin_method="",
    clindamycin="S",
    clindamycin_method="",
    tetracycline="S",
    tetracycline_method="",
    levofloxacin="S",
    levofloxacin_method="",
    ciprofloxacin="S",
    ciprofloxacin_method="",
    daptomycin="S",
    daptomycin_method="",
    vancomycin="S",
    vancomycin_method="",
    linezolid="S",
    linezolid_method="",
    sanger_sample_id="60",
)

TEST_UPLOAD_SAMPLE_3_DICT = dict(
    lane_id="50000_2#291",
    submitting_institution="Test Institution A",
    supplier_sample_name="EY_70602",
    public_name="CD_XX_EW00003",
    host_status="invasive disease",
    study_name="",
    study_ref="",
    selection_random="no",
    country="TestCountryA",
    county_state="",
    city="",
    collection_year="2014",
    collection_month="",
    collection_day="",
    host_species="",
    gender="M",
    age_group="infant",
    age_years="",
    age_months="",
    age_weeks="",
    age_days="",
    disease_type="septic arthritis",
    disease_onset="EOD",
    isolation_source="blood",
    serotype="III",
    serotype_method="",
    infection_during_pregnancy="",
    maternal_infection_type="",
    gestational_age_weeks="",
    birth_weight_gram="",
    apgar_score="",
    ceftizoxime="1",
    ceftizoxime_method="Etest",
    cefoxitin="",
    cefoxitin_method="",
    cefotaxime="",
    cefotaxime_method="",
    cefazolin="",
    cefazolin_method="",
    ampicillin="",
    ampicillin_method="",
    penicillin="",
    penicillin_method="",
    erythromycin="",
    erythromycin_method="",
    clindamycin="",
    clindamycin_method="",
    tetracycline="",
    tetracycline_method="",
    levofloxacin="",
    levofloxacin_method="",
    ciprofloxacin="",
    ciprofloxacin_method="",
    daptomycin="",
    daptomycin_method="",
    vancomycin="",
    vancomycin_method="",
    linezolid="",
    linezolid_method="",
    sanger_sample_id="60",
)

TEST_UPLOAD_SAMPLE_4_DICT = dict(
    lane_id="50000_2#296",
    submitting_institution="Test Institution A",
    supplier_sample_name="EY70603",
    public_name="CD_XX_EW00004",
    host_status="carriage",
    study_name="",
    study_ref="",
    selection_random="no",
    country="TestCountryA",
    county_state="",
    city="",
    collection_year="2014",
    collection_month="",
    collection_day="",
    host_species="human",
    gender="F",
    age_group="adolescent",
    age_years="15",
    age_months="10",
    age_weeks="2",
    age_days="4",
    disease_type="",
    disease_onset="",
    isolation_source="other sterile site",
    serotype="III",
    serotype_method="Lancefield",
    infection_during_pregnancy="",
    maternal_infection_type="",
    gestational_age_weeks="",
    birth_weight_gram="",
    apgar_score="",
    ceftizoxime="",
    ceftizoxime_method="",
    cefoxitin="",
    cefoxitin_method="",
    cefotaxime="",
    cefotaxime_method="",
    cefazolin="",
    cefazolin_method="",
    ampicillin="",
    ampicillin_method="",
    penicillin="",
    penicillin_method="",
    erythromycin="",
    erythromycin_method="",
    clindamycin="",
    clindamycin_method="",
    tetracycline="",
    tetracycline_method="",
    levofloxacin="",
    levofloxacin_method="",
    ciprofloxacin="",
    ciprofloxacin_method="",
    daptomycin="",
    daptomycin_method="",
    vancomycin="",
    vancomycin_method="",
    linezolid="",
    linezolid_method="",
    sanger_sample_id="60",
)

TEST_UPLOAD_SAMPLE_5_DICT = dict(
    lane_id="50000_2#298",
    submitting_institution="Test Institution A",
    supplier_sample_name="EY70603",
    public_name="CD_XX_EW00006",
    host_status="carriage",
    study_name="",
    study_ref="",
    selection_random="no",
    country="TestCountryA",
    county_state="",
    city="",
    collection_year="2014",
    collection_month="",
    collection_day="",
    host_species="human",
    gender="F",
    age_group="adolescent",
    age_years="15",
    age_months="10",
    age_weeks="2",
    age_days="4",
    disease_type="",
    disease_onset="",
    isolation_source="other sterile site",
    serotype="III",
    serotype_method="Lancefield",
    infection_during_pregnancy="",
    maternal_infection_type="",
    gestational_age_weeks="",
    birth_weight_gram="",
    apgar_score="",
    ceftizoxime="",
    ceftizoxime_method="",
    cefoxitin="",
    cefoxitin_method="",
    cefotaxime="",
    cefotaxime_method="",
    cefazolin="",
    cefazolin_method="",
    ampicillin="",
    ampicillin_method="",
    penicillin="",
    penicillin_method="",
    erythromycin="",
    erythromycin_method="",
    clindamycin="",
    clindamycin_method="",
    tetracycline="",
    tetracycline_method="",
    levofloxacin="",
    levofloxacin_method="",
    ciprofloxacin="",
    ciprofloxacin_method="",
    daptomycin="",
    daptomycin_method="",
    vancomycin="",
    vancomycin_method="",
    linezolid="",
    linezolid_method="",
    sanger_sample_id="60",
)

TEST_UPLOAD_SAMPLE_1 = Metadata(**TEST_UPLOAD_SAMPLE_1_DICT)
TEST_UPLOAD_SAMPLE_2 = Metadata(**TEST_UPLOAD_SAMPLE_2_DICT)
TEST_UPLOAD_SAMPLE_3 = Metadata(**TEST_UPLOAD_SAMPLE_3_DICT)
TEST_UPLOAD_SAMPLE_4 = Metadata(**TEST_UPLOAD_SAMPLE_4_DICT)
TEST_UPLOAD_SAMPLE_5 = Metadata(**TEST_UPLOAD_SAMPLE_5_DICT)

EXPECTED_VALIDATION_ERRORS = [
    '{row: 4, column: "Sanger_Sample_ID"}: "ZZZ;;{}{}{[[STUDY" contains illegal characters',
    '{row: 5, column: "Supplier_Sample_Name"}: "%%%%%@qwe" contains illegal characters',
    '{row: 7, column: "Supplier_Sample_Name"}: "EY 70603" contains illegal characters',
    '{row: 8, column: "Public_Name"}: "^&*%RTYUT" contains illegal characters',
    '{row: 10, column: "Lane_ID"}: "ABCDE_2#FGI" is not a recognised lane Id format',
    '{row: 11, column: "Lane_ID"}: "ABCDE" is not a recognised lane Id format',
    '{row: 12, column: "Lane_ID"}: "50000-1%316" is not a recognised lane Id format',
    '{row: 16, column: "Study_Reference"}: "PMID: 1" must be a comma-separated list of study references, e.g. PMID: 1234567, PMID: 23456789',
    '{row: 19, column: "Study_Reference"}: "PMID: 1, PMID: 223" must be a comma-separated list of study references, e.g. PMID: 1234567, PMID: 23456789',
    '{row: 23, column: "Selection_Random"}: "INVALID" is not in the list of legal options (yes, no)',
    '{row: 24, column: "Country"}: "UNKNOWNCOUNTRY" is not in the list of legal options (TestCountryA, TestCountryB)',
    '{row: 29, column: "Submitting_Institution"}: "UNKNOWN" is not in the list of legal options (Test Institution A, Test Institution B)',
    '{row: 30, column: "Collection_year"}: "1" must be a YYYY format year',
    '{row: 31, column: "Collection_year"}: "AB" must be a YYYY format year',
    '{row: 32, column: "Collection_month"}: "200" must be a MM format month',
    '{row: 33, column: "Collection_month"}: "AB" must be a MM format month',
    '{row: 34, column: "Collection_day"}: "500000" must be a DD format day',
    '{row: 35, column: "Collection_day"}: "ABCD" must be a DD format day',
    '{row: 37, column: "Host_species"}: "Panda" is not in the list of legal options (human, bovine, fish, goat, camel, other)',
    '{row: 38, column: "Gender"}: "INVALID" is not in the list of legal options (M, F)',
    '{row: 44, column: "Age_years"}: "11111" should be a valid 1 to 3 digit number',
    '{row: 44, column: "Age_months"}: "22222" should be a valid 1 to 4 digit number',
    '{row: 44, column: "Age_weeks"}: "333333" should be a valid 1 to 4 digit number',
    '{row: 44, column: "Age_days"}: "4444444" should be a valid 1 to 5 digit number',
    '{row: 46, column: "Host_status"}: "GGG" is not in the list of legal options (carriage, invasive disease, non-invasive disease)',
    '{row: 46, column: "Disease_type"}: "aaa" is not in the list of legal options (sepsis, bacteraemia, meningitis, pneumonia, urinary tract infection, skin and soft-tissue infection, osteomyelitis, endocarditis, septic arthritis, chorioamnionitis, peritonitis, empyema, surgical site infection, urosepsis, endometritis, mastitis, septicaemia, invasive other, non-invasive other)',
    '{row: 46, column: "Disease_onset"}: "ZOG" is not in the list of legal options (EOD, LOD, VLOD, other)',
    '{row: 46, column: "Isolation_source"}: "finger nails" is not in the list of legal options (rectovaginal swab, vaginal swab, ear swab, umbilical swab, umbilical swab, throat swab, skin swab, rectal swab, placenta, blood, cerebrospinal fluid, cord blood, pus: skin infection, pus: brain abscess, pus: other abscess, sputum, urine, pleural fluid, peritoneal fluid, pericardial fluid, joint/synovial fluid, bone, lymph node, semen, milk, spleen, kidney, liver, brain, heart, pancreas, other sterile site, other non-sterile site, abscess, abscess/pus fluid, aspirate fluid, blood vessels, bronchoalveolar lavage, burn, cellulitis/erysipelas, decubitus, drains/tubes, endotracheal aspirate, furuncle, gall bladder, impetiginous lesions, lungs, muscle tissue, prostate, skin ulcer, spinal cord, stomach, thoracentesis fluid, tissue fluid, trachea, ulcer fluid, urethra, urinary bladder, uterus, wound)',
    '{row: 47, column: "Serotype"}: "IIIIIIII" is not in the list of legal options (Ia, Ib, II, III, IV, V, VI, VII, VIII, IX, NT)',
    '{row: 47, column: "Infection_during_pregnancy"}: "HUH?" is not in the list of legal options (yes, no)',
    '{row: 51, column: "Gestational_age_weeks"}: "ZZ" should be a valid 1 to 3 digit number',
    '{row: 51, column: "Birthweight_gram"}: "HHHH" should be a valid 1 to 7 digit number',
    '{row: 51, column: "Apgar_score"}: "AAA" should be a valid number between 0 and 10',
    '{row: 52, column: "Maternal_infection_type"}: "OTHER" is not in the list of legal options (urinary tract infection, chorioamnionitis/intrauterine infection, sepsis, meningitis, arthritis, skin and soft-tissue infection, invasive other, non-invasive other)',
    '{row: 58, column: "Ceftizoxime_method"}: "ZZZ" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Cefoxitin"}: "A" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Cefoxitin_method"}: "AAA" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Cefotaxime"}: "B" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Cefotaxime_method"}: "BBB" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Cefazolin"}: "C" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Cefazolin_method"}: "CCC" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Ampicillin"}: "D" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Ampicillin_method"}: "DDD" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Penicillin"}: "R1" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Penicillin_method"}: "EEE" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Erythromycin"}: "F" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Erythromycin_method"}: "FFF" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Clindamycin"}: "G" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Clindamycin_method"}: "GGG" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Tetracycline"}: "H" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Tetracycline_method"}: "HHH" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Tetracycline"}: "H" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Tetracycline_method"}: "HHH" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Levofloxacin"}: "I1" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Levofloxacin_method"}: "III" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Ciprofloxacin"}: "J" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Ciprofloxacin_method"}: "JJJJ" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Daptomycin"}: "K" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Daptomycin_method"}: "KKKK" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Vancomycin"}: "S1" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Vancomycin_method"}: "LLLL" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Linezolid"}: "M" should be a valid floating point number, optionally with units "mm" or "µg/ml" (\'u\' permitted in place of \'µ\'); or alternatively S, I, or R',
    '{row: 58, column: "Linezolid_method"}: "MMMM" is not in the list of legal options (disk diffusion, broth dilution, agar dilution, Etest)',
    '{row: 58, column: "Public_Name"}: "CD_XX_EW00056TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT" field length is greater than 256 characters',
    '{row: 61, column: "Apgar_score"}: "9 [extra text 5]" should be a valid number between 0 and 10',
]
