from juno.tests.base import AuthenticatableGraphQLTestCase
from juno.api.models import Institution, User, Affiliation


class InstitutionsQueryTestCase(AuthenticatableGraphQLTestCase):
    PASSWORD = "bobsicles"

    def setUp(self):
        # put an institution in the db
        self.institution = Institution.objects.create(
            name="Wellcome Sanger Institute",
            country="United Kingdom",
            latitude=52.083333,
            longitude=0.183333,
        )

        # put user in the db
        self.user = User.objects.create(
            email="bob@bob.com", first_name="Bob", last_name="Bobbity",
        )
        self.user.set_password(self.PASSWORD)
        self.user.save()

        # associate the user with the institution
        Affiliation.objects.create(
            user=self.user, institution=self.institution
        )

        # login (institutions is an auth restricted resource)
        response = self.login(self.user.email, self.PASSWORD)
        (payload, token, refresh_expires_in) = self.validate_login_successful(
            response
        )

    def make_and_validate_institutions_query(self, subquery):
        # call api
        response = self.make_query("institutions", subquery)
        data = self.validate_successful(response)
        institutions = self.validate_field(data, "institutions")

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
