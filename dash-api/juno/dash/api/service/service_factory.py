from dash.api.service.monocleclient import MonocleUser, MonocleData


class UserService(MonocleUser):
    """ Wrapper class for MonocleUser """

    def __init__(self, authenticated_username=None, set_up=True):
        MonocleUser.__init__(self, authenticated_username, set_up)


class DataService(MonocleData):
    """ Wrapper class for MonocleData, that sets a user details record """

    def __init__(self, username: str, set_up: bool = True):
        MonocleData.__init__(self, set_up)
        user_service = MonocleUser(username)
        self.user_record = user_service.load_user_record(self, authenticated_username)


class TestDataService(MonocleData):
    """ Wrapper class for MonocleData testing """

    def __init__(self, set_up: bool = True):
        MonocleData.__init__(self, set_up)


class ServiceFactory:
    """ Instantiate a service """

    TEST_MODE = False

    @staticmethod
    def user_service(username: str) -> UserService:
        return UserService(username)

    @staticmethod
    def data_service(username: str) -> DataService:
        if not ServiceFactory.TEST_MODE:
            return DataService(username)
        else:
            return TestDataService()
