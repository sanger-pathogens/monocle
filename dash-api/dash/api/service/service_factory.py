import logging

from dash.api.service.DataServices.sample_data_services import MonocleSampleData
from dash.api.service.DataServices.sample_tracking_services import MonocleSampleTracking
from dash.api.service.DataServices.user_services import MonocleAuthentication, MonocleUser


class AuthenticationService(MonocleAuthentication):
    """Wrapper class for MonocleAuthentication"""

    # this is a placeholder
    # currently this wrapper needs no specific initlialization


def _add_user_record(username, obj_ref):
    user = MonocleUser(username)
    obj_ref.user_record = user.record
    # Set the project
    # (in future we will probably support membership of multiple projects)
    project_list = user.record.get("projects")
    if project_list is None or 0 == len(project_list):
        raise RuntimeError("User accounts must have a projects attribute (user record: {})".format(user.record))
    elif len(project_list) > 1:
        raise RuntimeError(
            "Multiple project membership for users is not currently supported (user record: {})".format(user.record)
        )
    else:
        obj_ref.current_project = project_list[0]
    logging.debug("Setting current_project = {} (user record = {})".format(obj_ref.current_project, user.record))


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
        # Setting the user record will enforce data filtering by user
        _add_user_record(username, self)


class TestDataService(MonocleSampleData):
    """Wrapper class for MonocleSampleData testing, which does not do user checking"""

    def __init__(self, set_up: bool = True):
        MonocleSampleData.__init__(self, set_up=set_up)


class SampleTrackingService(MonocleSampleTracking):
    """Wrapper class for MonocleSampleTracking, that sets a user details record"""

    def __init__(self, username: str, set_up: bool = True):
        MonocleSampleTracking.__init__(self, set_up=set_up)
        # Setting the user record will enforce data filtering by user
        _add_user_record(username, self)


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
