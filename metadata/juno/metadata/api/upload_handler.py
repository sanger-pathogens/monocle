import pandas
import logging
from typing import List
from pandas_schema import Column, Schema
from pandas_schema.validation import LeadingWhitespaceValidation, TrailingWhitespaceValidation, MatchesPatternValidation, InRangeValidation, InListValidation
from metadata.api.model.metadata import Metadata
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition

logger = logging.getLogger()


class UploadHandler:
    """ Handle processing of upload spreadsheets """

    @property
    def data_frame(self):
        return self.__df

    def __init__(self, in_def: SpreadsheetDefinition) -> None:
        self.__df = None
        # self.spreadsheet_def = config['spreadsheet_definition']
        self.spreadsheet_def = in_def

    def get_column_name_for_key(self, key: str):
        return self.spreadsheet_def.get_column_name(key)

    def create_schema(self) -> Schema:
        return Schema([
            Column(self.get_column_name_for_key('sanger_sample_id'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=False),
            Column(self.get_column_name_for_key('supplier_sample_name'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=False),
            Column(self.get_column_name_for_key('public_name'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=False),
            Column(self.get_column_name_for_key('lane_id'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('study_name'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('study_ref'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('selection_random'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), InListValidation(['Yes', 'No'])],
                   allow_empty=False),
            Column(self.get_column_name_for_key('country'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=False),
            Column(self.get_column_name_for_key('county_state'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('city'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('submitting_institution'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=False),
            Column(self.get_column_name_for_key('collection_year'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), InRangeValidation(2000, 9999)],
                   allow_empty=False),
            Column(self.get_column_name_for_key('collection_month'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), InRangeValidation(0, 12)],
                   allow_empty=True),
            Column(self.get_column_name_for_key('collection_day'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), InRangeValidation(0, 31)],
                   allow_empty=True),
            Column(self.get_column_name_for_key('host_species'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), InListValidation(['human', 'bovine', 'fish', 'camel', 'other'])],
                   allow_empty=False),
            Column(self.get_column_name_for_key('gender'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), InListValidation(['M', 'F', 'Unknown', 'unknown'])],
                   allow_empty=True),
            Column(self.get_column_name_for_key('age_group'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), InListValidation(['Neonate', 'Adult', 'Other', 'Unknown'])],
                   allow_empty=False),
            Column(self.get_column_name_for_key('age_years'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('age_months'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('age_weeks'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('age_days'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('host_status'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), InListValidation(['carriage', 'invasive', 'non-invasive', 'disease other'])],
                   allow_empty=True),
            Column(self.get_column_name_for_key('disease_type'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('disease_onset'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), InListValidation(['EOD', 'LOD', 'VLOD', 'other', 'unknown', 'NA'])],
                   allow_empty=True),
            Column(self.get_column_name_for_key('isolation_source'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('serotype'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('serotype_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), InListValidation(['latex agglutination', 'lancefield', 'PCR', 'other'])],
                   allow_empty=True),
            Column(self.get_column_name_for_key('infection_during_pregnancy'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(), InListValidation(['Yes', 'No', 'Unknown'])],
                   allow_empty=True),
            Column(self.get_column_name_for_key('maternal_infection_type'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('gestational_age_weeks'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('birth_weight_gram'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('apgar_score'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('ceftizoxime'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('ceftizoxime_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('cefoxitin'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('cefoxitin_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('cefotaxime'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('cefotaxime_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('cefazolin'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('cefazolin_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('ampicillin'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('ampicillin_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('penicillin'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('penicillin_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('erythromycin'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('erythromycin_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('clindamycin'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('clindamycin_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('tetracycline'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('tetracycline_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('levofloxacin'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('levofloxacin_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('ciprofloxacin'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('ciprofloxacin_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('daptomycin'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('daptomycin_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('vancomycin'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('vancomycin_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('linezolid'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('linezolid_method'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True),
            Column(self.get_column_name_for_key('additional_metadata'), [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()],
                   allow_empty=True)
        ])

    def format_validation_errors(self, errors: list) -> List[str]:
        results = []
        for error in errors:
            results.append(str(error))
        return results

    def load(self, file_path: str) -> List[str]:
        data = pandas.read_excel(file_path, header=2)
        data = data.astype(str)
        data.replace(to_replace=r'^nan$', value='', regex=True, inplace=True)

        for key, value in data.iterrows():
            print(key, value)
            print()

        errors = self.create_schema().validate(data)
        if len(errors) > 0:
            return self.format_validation_errors(errors)

        self.__df = pandas.DataFrame(data.replace('NaN', ''))

        return errors

    def parse(self) -> List[Metadata]:
        results = []
        for _, row in self.__df.iterrows():
            metadata = Metadata(
                            sanger_sample_id=row[self.get_column_name_for_key('sanger_sample_id')],
                            lane_id=row[self.get_column_name_for_key('lane_id')],
                            submitting_institution=row[self.get_column_name_for_key('submitting_institution')],
                            supplier_sample_name=row[self.get_column_name_for_key('supplier_sample_name')],
                            public_name=row[self.get_column_name_for_key('public_name')],
                            host_status=row[self.get_column_name_for_key('host_status')],
                            study_name=row[self.get_column_name_for_key('study_name')],
                            study_ref=row[self.get_column_name_for_key('study_ref')],
                            selection_random=row[self.get_column_name_for_key('selection_random')],
                            country=row[self.get_column_name_for_key('country')],
                            county_state=row[self.get_column_name_for_key('county_state')],
                            city=row[self.get_column_name_for_key('city')],
                            collection_year=row[self.get_column_name_for_key('collection_year')],
                            collection_month=row[self.get_column_name_for_key('collection_month')],
                            collection_day=row[self.get_column_name_for_key('collection_day')],
                            host_species=row[self.get_column_name_for_key('host_species')],
                            gender=row[self.get_column_name_for_key('gender')],
                            age_group=row[self.get_column_name_for_key('age_group')],
                            age_years=row[self.get_column_name_for_key('age_years')],
                            age_months=row[self.get_column_name_for_key('age_months')],
                            age_weeks=row[self.get_column_name_for_key('age_weeks')],
                            age_days=row[self.get_column_name_for_key('age_days')],
                            disease_type=row[self.get_column_name_for_key('disease_type')],
                            disease_onset=row[self.get_column_name_for_key('disease_onset')],
                            isolation_source=row[self.get_column_name_for_key('isolation_source')],
                            serotype=row[self.get_column_name_for_key('serotype')],
                            serotype_method=row[self.get_column_name_for_key('serotype_method')],
                            infection_during_pregnancy=row[self.get_column_name_for_key('infection_during_pregnancy')],
                            maternal_infection_type=row[self.get_column_name_for_key('maternal_infection_type')],
                            gestational_age_weeks=row[self.get_column_name_for_key('gestational_age_weeks')],
                            birth_weight_gram=row[self.get_column_name_for_key('birth_weight_gram')],
                            apgar_score=row[self.get_column_name_for_key('apgar_score')],
                            ceftizoxime=row[self.get_column_name_for_key('ceftizoxime')],
                            ceftizoxime_method=row[self.get_column_name_for_key('ceftizoxime_method')],
                            cefoxitin=row[self.get_column_name_for_key('cefoxitin')],
                            cefoxitin_method=row[self.get_column_name_for_key('cefoxitin_method')],
                            cefotaxime=row[self.get_column_name_for_key('cefotaxime')],
                            cefotaxime_method=row[self.get_column_name_for_key('cefotaxime_method')],
                            cefazolin=row[self.get_column_name_for_key('cefazolin')],
                            cefazolin_method=row[self.get_column_name_for_key('cefazolin_method')],
                            ampicillin=row[self.get_column_name_for_key('ampicillin')],
                            ampicillin_method=row[self.get_column_name_for_key('ampicillin_method')],
                            penicillin=row[self.get_column_name_for_key('penicillin')],
                            penicillin_method=row[self.get_column_name_for_key('penicillin_method')],
                            erythromycin=row[self.get_column_name_for_key('erythromycin')],
                            erythromycin_method=row[self.get_column_name_for_key('erythromycin_method')],
                            clindamycin=row[self.get_column_name_for_key('clindamycin')],
                            clindamycin_method=row[self.get_column_name_for_key('clindamycin_method')],
                            tetracycline=row[self.get_column_name_for_key('tetracycline')],
                            tetracycline_method=row[self.get_column_name_for_key('tetracycline_method')],
                            levofloxacin=row[self.get_column_name_for_key('levofloxacin')],
                            levofloxacin_method=row[self.get_column_name_for_key('levofloxacin_method')],
                            ciprofloxacin=row[self.get_column_name_for_key('ciprofloxacin')],
                            ciprofloxacin_method=row[self.get_column_name_for_key('ciprofloxacin_method')],
                            daptomycin=row[self.get_column_name_for_key('daptomycin')],
                            daptomycin_method=row[self.get_column_name_for_key('daptomycin_method')],
                            vancomycin=row[self.get_column_name_for_key('vancomycin')].replace("nan", 'HELLO WORLD'),
                            vancomycin_method=row[self.get_column_name_for_key('vancomycin_method')],
                            linezolid=row[self.get_column_name_for_key('linezolid')],
                            linezolid_method=row[self.get_column_name_for_key('linezolid_method')],
                            additional_metadata=row[self.get_column_name_for_key('additional_metadata')])
            results.append(metadata)
        return results


