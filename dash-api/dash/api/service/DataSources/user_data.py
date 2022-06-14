import logging
from base64 import b64decode, b64encode

from dash.api.exceptions import LdapDataError
from dash.api.service.DataSources.ldap_data import LdapData

DEFAULT_TOKEN_ENCODING = "utf8"
TOKEN_DELIMITER = ":"

GROUP_OBJ_CONFIG_KEY = "user_group_obj"


class UserAuthentication:
    """
    Methods related to user authentication
    """

    def get_auth_token(self, username_provided, password_provided, encoding=DEFAULT_TOKEN_ENCODING):
        """
        Pass username and password supplited by the user.  Optionally pass encodung (defaults to UTF-8).
        Returns token that should be used as the authentication cookie value, as used by the NGINX authentication module.
        """
        username_password_bytes = TOKEN_DELIMITER.join([username_provided, password_provided]).encode(encoding)
        token_bytes = b64encode(username_password_bytes)
        return token_bytes.decode(encoding)

    def get_username_from_token(self, auth_token, encoding=DEFAULT_TOKEN_ENCODING):
        """
        Pass a token.  Optionally pass encodung (defaults to UTF-8).
        This method does NOT do any authentication.  It just gets the username provided by the user
        when the token was created.
        Returns the username.
        """
        if auth_token is None or 0 == len(auth_token):
            logging.warning("Asked to extract username from empty auth token")
            return auth_token
        username_password_bytes = b64decode(auth_token)
        username_provided = username_password_bytes.decode(encoding).split(TOKEN_DELIMITER)[0]
        return username_provided


class UserData(LdapData):
    """
    Methods for retrieving user data from the Monocle LDAP service.
    """

    def __init__(self, set_up=True):
        """
        Reads config from default config file in the parent class by default;
        pass set_up=False to prevent config being dong on instalation, and
        subsequently you can call set_up() to configure with a config file of your choice
        """
        super().__init__(
            [
                "users_obj",
                "user_group_obj",
                "username_attr",
                "uid_attr",
                "membership_attr",
                "inst_id_attr",
                "inst_name_attr",
            ],
            set_up=set_up,
        )
        self.required_attributes_for_group_search = None

    def get_user_details(self, username):
        """
        Retrieves details of a user from LDAP, given a username.
        Returns details as a dict.
        This is expected to be called when we have an authenticated username, so
        if this doesn't match a valid user something has gone badly wrong.  Consequently,
        will raise LdapDataError unless the username matches a user who is a member of at
        least one institution, which is the minimum we should expect.
        """
        logging.info("retrieving user information for username {}".format(username))
        user_details = {"username": username, "memberOf": [], "projects": []}
        ldap_user_rec = self.ldap_search_user_by_username(username)
        if ldap_user_rec is None:
            logging.error(
                "searched for username {} which could not be found in LDAP, which should never happen when the user has been authenticated.".format(
                    username
                )
            )
            raise LdapDataError("username {} not found".format(username))
        # note dict of attributes is the second element of the `ldap_user_rec` tuple
        user_attr = ldap_user_rec[1]
        # check username attribute matches what we searched for
        # (if this isn't the case, the search must have found a match on some other attribute, which *should* be impossible, but LDAP)
        uid_attr = user_attr[self.config["username_attr"]][0].decode("UTF-8")
        if not uid_attr == username:
            logging.error(
                "Search for username {} returned a record with a mismatched {} value of {} (should be same as the username)".format(
                    username, self.config["username_attr"], uid_attr
                )
            )
            raise LdapDataError("user record returned with mismatched {}".format(self.config["username_attr"]))
        org_gids = [org_gid_bytes.decode("UTF-8") for org_gid_bytes in user_attr[self.config["membership_attr"]]]
        if len(org_gids) < 1:
            logging.error(
                "The username {} is not associated with any organisations (full attributes: {})".format(
                    username, user_attr
                )
            )
            raise LdapDataError("username {} has no organisation attribute values ".format(username))

        # get user's project(s)
        if self.config["project_attr"] not in user_attr:
            raise LdapDataError("username {} has no project attribute values ".format(username))
        user_details["projects"] = [
            project_bytes.decode("UTF-8") for project_bytes in user_attr[self.config["project_attr"]]
        ]
        if len(user_details["projects"]) < 1:
            logging.error(
                "The username {} is not associated with any projects (full attributes: {})".format(username, user_attr)
            )
            raise LdapDataError("username {} has no project attribute values ".format(username))

        try:
            # Try to get optional employee type attribute
            employee_type = user_attr[self.config["employee_type_attr"]][0].decode("UTF-8")
            if employee_type:
                user_details["type"] = employee_type
        except Exception:
            pass

        if self.required_attributes_for_group_search is None:
            self.required_attributes_for_group_search = [
                self.config["inst_id_attr"],
                self.config["inst_name_attr"],
                self.config["country_names_attr"],
            ]
        for this_gid in org_gids:
            ldap_group_rec = self.ldap_search_group_by_gid(
                this_gid, GROUP_OBJ_CONFIG_KEY, self.required_attributes_for_group_search
            )
            if ldap_group_rec is None:
                logging.error(
                    "A group with GID {} could not be found in LDAP, which indicates an invalid user record.".format(
                        this_gid
                    )
                )
                raise LdapDataError("group with GID {} not found.".format(this_gid))
            # note dict of attributes is the second element of the `ldap_group_rec` tuple
            group_attr = ldap_group_rec[1]
            inst_id = group_attr[self.config["inst_id_attr"]][0].decode("UTF-8")
            country_names = [
                country_name_bytes.decode("UTF-8")
                for country_name_bytes in group_attr[self.config["country_names_attr"]]
            ]
            if len(country_names) < 1:
                logging.error(
                    "The institute id {} is not associated with any countries, which indicates an invalid group record)".format(
                        inst_id
                    )
                )
                raise LdapDataError("institute id {} has no country name attribute values ".format(inst_id))

            user_details["memberOf"].append(
                {
                    "inst_id": inst_id,
                    "inst_name": group_attr[self.config["inst_name_attr"]][0].decode("UTF-8"),
                    "country_names": country_names,
                }
            )

        return user_details

    def ldap_search_user_by_username(self, username):
        """
        Wraps ldap_search_by_attribute_value() adding params for search for a user using the username passed.
        Returns LDAP user record for the user if found, None if not found.
        Raises LdapDataError if more than 1 match (username should be unique)
        or if returned data are not valid for a user record.
        LDAP record expected to be a tuple with two elements
        - the user's DN
        - a dict of attributes
        Note attribute valids are bytes, require decode() to convert to string
        """
        logging.debug("searching for username {}".format(username))
        result_list = self.ldap_search_by_attribute_value(
            self.config["users_obj"], self.config["username_attr"], username
        )
        if 0 == len(result_list):
            return None
        # believe there should be only one hit -- or usernames aren't unique :-/
        if len(result_list) > 1:
            logging.error(
                "The username {} matched multiple entries in {}.{}:  it should be unique".format(
                    username, self.config["users_obj"], self.config["username_attr"]
                )
            )
            raise LdapDataError("uid {} not unique".format(username))
        result = result_list[0]
        # check attributes returned include required attributes
        for this_required_attr in [
            self.config["username_attr"],
            self.config["membership_attr"],
            self.config["project_attr"],
        ]:
            if this_required_attr not in result[1]:
                logging.error(
                    "username {} search result doesn't seem to contain the required attribute {} (complete data = {})".format(
                        username, this_required_attr, result
                    )
                )
                raise LdapDataError(
                    "username {} doesn't contain required attribute {}".format(username, this_required_attr)
                )
        # TODO more validation to check user data are OK
        logging.debug("found user: {}".format(result))
        return result
