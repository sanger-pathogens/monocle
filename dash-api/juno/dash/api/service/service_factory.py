from dash.api.service.DataServices.sample_data_services import MonocleSampleData
from dash.api.service.DataServices.sample_tracking_services import MonocleSampleTracking
from dash.api.service.DataServices.user_services            import MonocleAuthentication, MonocleUser


class AuthenticationService(MonocleAuthentication):
    """ Wrapper class for MonocleAuthentication """

    # this is a placeholder
    # currently this wrapper needs no specific initlialization


class UserService(MonocleUser):
    """Wrapper class for MonocleUser"""

    def __init__(self, authenticated_username=None, set_up=True):
        MonocleUser.__init__(self, authenticated_username, set_up=set_up)

    @property
    def user_details(self):
        return self.record


class DataService(MonocleSampleData):
    """Wrapper class for MonocleSampleData, that sets a user details record"""

    def __init__(self, username: str, set_up: bool = True):
        MonocleSampleData.__init__(self, set_up=set_up)
        user = MonocleUser(username)
        # Setting this record will enforce data filtering by user
        self.sample_tracking.user_record = user.record


class TestDataService(MonocleSampleData):
    """Wrapper class for MonocleSampleData testing, which does not do user checking"""

    def __init__(self, set_up: bool = True):
        MonocleSampleData.__init__(self, set_up=set_up)


class SampleTrackingService(MonocleSampleTracking):
    """Wrapper class for MonocleSampleTracking, that sets a user details record"""

    def __init__(self, username: str, set_up: bool = True):
        MonocleSampleTracking.__init__(self, set_up=set_up)
        user = MonocleUser(username)
        # Setting this record will enforce data filtering by user
        self.user_record = user.record


class TestSampleTrackingService(MonocleSampleTracking):
    """Wrapper class for MonocleSampleTracking testing, which does not do user checking"""

    def __init__(self, set_up: bool = True):
        MonocleSampleTracking.__init__(self, set_up=set_up)


class ServiceFactory:
    """Instantiate a service"""

    TEST_MODE = False

    @staticmethod
    def authentication_service() -> AuthenticationService:
        return AuthenticationService()

    @staticmethod
    def user_service(username: str) -> UserService:
        return UserService(username)

    @staticmethod
    def sample_data_service(username: str) -> DataService:
        if not ServiceFactory.TEST_MODE:
            return DataService(username)
        else:
            return TestDataService()

    @staticmethod
    def sample_tracking_service(username: str) -> SampleTrackingService:
        if not ServiceFactory.TEST_MODE:
            return SampleTrackingService(username)
        else:
            return TestSampleTrackingService()
