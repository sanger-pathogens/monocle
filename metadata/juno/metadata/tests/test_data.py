from metadata.api.model.metadata import Metadata
from metadata.api.model.in_silico_data import InSilicoData

""" Some test data to use in unit tests... """

TEST_SAMPLE_1 = Metadata(
    sanger_sample_id='9999STDY8113123',
    lane_id='2000_2#10',
    submitting_institution='UniversityA',
    supplier_sample_name='SUPPLIER_1',
    public_name='PUB_NAME_1',
    host_status='CARRIAGE',
    study_name='My_study1',
    study_ref='5201',
    selection_random='Y',
    country='UK',
    county_state='Cambridgeshire',
    city='Cambridge',
    collection_year='2019',
    collection_month='12',
    collection_day='05',
    host_species='human',
    gender='M',
    age_group='adult',
    age_years='35',
    age_months='10',
    age_weeks='2',
    age_days='2',
    disease_type='GBS',
    disease_onset='EOD',
    isolation_source='blood',
    serotype='IV',
    serotype_method='PCR',
    infection_during_pregnancy='N',
    maternal_infection_type='oral',
    gestational_age_weeks='10',
    birth_weight_gram='400',
    apgar_score='10',
    ceftizoxime='1',
    ceftizoxime_method='method1',
    cefoxitin='2',
    cefoxitin_method='method2',
    cefotaxime='3',
    cefotaxime_method='method3',
    cefazolin='4',
    cefazolin_method='method4',
    ampicillin='5',
    ampicillin_method='method5',
    penicillin='6',
    penicillin_method='method6',
    erythromycin='7',
    erythromycin_method='method7',
    clindamycin='8',
    clindamycin_method='method8',
    tetracycline='9',
    tetracycline_method='method9',
    levofloxacin='10',
    levofloxacin_method='method10',
    ciprofloxacin='11',
    ciprofloxacin_method='method11',
    daptomycin='12',
    daptomycin_method='method12',
    vancomycin='13',
    vancomycin_method='method13',
    linezolid='14',
    linezolid_method='method14')

TEST_SAMPLE_2 = Metadata(
    sanger_sample_id='9999STDY8113124',
    lane_id='2000_2#11',
    submitting_institution='UniversityB',
    supplier_sample_name='SUPPLIER_2',
    public_name='PUB_NAME_2',
    host_status='INVASIVE',
    study_name='My_stud2',
    study_ref='5202',
    selection_random='N',
    country='US',
    county_state='California',
    city='Los Angeles',
    collection_year='2020',
    collection_month='10',
    collection_day='07',
    host_species='chimp',
    gender='N',
    age_group='adult',
    age_years='45',
    age_months='4',
    age_weeks='1',
    age_days='1',
    disease_type='other',
    disease_onset='LOD',
    isolation_source='skin',
    serotype='IX',
    serotype_method='PCR2',
    infection_during_pregnancy='Y',
    maternal_infection_type='other',
    gestational_age_weeks='12',
    birth_weight_gram='500',
    apgar_score='3',
    ceftizoxime='11',
    ceftizoxime_method='method11',
    cefoxitin='12',
    cefoxitin_method='method12',
    cefotaxime='13',
    cefotaxime_method='method13',
    cefazolin='14',
    cefazolin_method='method14',
    ampicillin='15',
    ampicillin_method='method15',
    penicillin='16',
    penicillin_method='method16',
    erythromycin='17',
    erythromycin_method='method17',
    clindamycin='18',
    clindamycin_method='method18',
    tetracycline='19',
    tetracycline_method='method19',
    levofloxacin='20',
    levofloxacin_method='method20',
    ciprofloxacin='21',
    ciprofloxacin_method='method21',
    daptomycin='22',
    daptomycin_method='method22',
    vancomycin='23',
    vancomycin_method='method23',
    linezolid='24',
    linezolid_method='method24')

TEST_LANE_1 = InSilicoData(
    lane_id='50000_2#282',
    cps_type='III',
    ST='ST-I',
    adhP=15,
    pheS=8,
    atr=4,
    glnA=4,
    sdhA=22,
    glcK=1,
    tkt=9,
    twenty_three_S1='pos',
    twenty_three_S3='pos',
    CAT='neg',
    ERMB='neg',
    ERMT='neg',
    FOSA='neg',
    GYRA='pos',
    LNUB='neg',
    LSAC='neg',
    MEFA='neg',
    MPHC='neg',
    MSRA='neg',
    MSRD='neg',
    PARC='pos',
    RPOBGBS_1='neg',
    RPOBGBS_2='neg',
    RPOBGBS_3='neg',
    RPOBGBS_4='neg',
    SUL2='neg',
    TETB='neg',
    TETL='neg',
    TETM='pos',
    TETO='neg',
    TETS='neg',
    ALP1='neg',
    ALP23='neg',
    ALPHA='neg',
    HVGA='pos',
    PI1='pos',
    PI2A1='neg',
    PI2A2='neg',
    PI2B='pos',
    RIB='pos',
    SRR1='neg',
    SRR2='pos',
    GYRA_variant='*',
    PARC_variant='*')

TEST_LANE_2 = InSilicoData(
    lane_id='50000_2#287',
    cps_type='III',
    ST='ST-II',
    adhP=3,
    pheS=11,
    atr=0,
    glnA=16,
    sdhA=14,
    glcK=31,
    tkt=6,
    twenty_three_S1='pos',
    twenty_three_S3='pos',
    CAT='neg',
    ERMB='neg',
    ERMT='neg',
    FOSA='neg',
    GYRA='pos',
    LNUB='neg',
    LSAC='neg',
    MEFA='neg',
    MPHC='neg',
    MSRA='neg',
    MSRD='neg',
    PARC='pos',
    RPOBGBS_1='neg',
    RPOBGBS_2='neg',
    RPOBGBS_3='neg',
    RPOBGBS_4='neg',
    SUL2='neg',
    TETB='neg',
    TETL='neg',
    TETM='pos',
    TETO='neg',
    TETS='neg',
    ALP1='neg',
    ALP23='neg',
    ALPHA='neg',
    HVGA='pos',
    PI1='pos',
    PI2A1='neg',
    PI2A2='neg',
    PI2B='pos',
    RIB='pos',
    SRR1='neg',
    SRR2='pos',
    GYRA_variant='GYRA-T78Q,L55A',
    PARC_variant='PARC-Q17S')
