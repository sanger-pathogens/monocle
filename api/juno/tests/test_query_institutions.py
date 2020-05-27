from juno.tests.base import APITestCase
from juno.api.models import Institution


class InstitutionsQueryTestCase(APITestCase):
    def setUp(self):
        # put something in the db
        self.institution = Institution.objects.create(
            name="Wellcome Sanger Institute",
            country="United Kingdom",
            latitude=52.083333,
            longitude=0.183333,
        )

    def make_and_validate_institutions_query(self, subquery):
        # call api
        institutions = self.make_and_validate_query("institutions", subquery)

        # check non-empty
        self.validate_non_empty_list(institutions)

        # return institutions
        return institutions

    def test_has_field_name(self):
        institutions = self.make_and_validate_institutions_query("name")
        self.validate_field(
            institutions[0], "name", expected_value=self.institution.name,
        )

    def test_has_latitude(self):
        institutions = self.make_and_validate_institutions_query("latitude")
        self.validate_field(
            institutions[0],
            "latitude",
            expected_value=self.institution.latitude,
        )

    def test_has_longitude(self):
        institutions = self.make_and_validate_institutions_query("longitude")
        self.validate_field(
            institutions[0],
            "longitude",
            expected_value=self.institution.longitude,
        )

    def test_has_field_country(self):
        institutions = self.make_and_validate_institutions_query("country")
        self.validate_field(
            institutions[0],
            "country",
            expected_value=self.institution.country,
        )
