import logging

from dash.api.service.DataSources.ldap_data import LdapData, LdapDataError

UTF_8 = "utf-8"


class InstitutionData(LdapData):
    def __init__(self, set_up=True):
        """
        Reads config from default config file in the parent class by default;
        pass set_up=False to prevent config being dong on instalation, and
        subsequently you can call set_up() to configure with a config file of your choice
        """
        super().__init__(
            [
                "institution_group_obj",
                "inst_id_attr",
                "inst_name_attr",
            ],
            set_up=set_up,
        )
        self.ldap_filter_string_institutions = None

    def get_all_institutions_regardless_of_user_membership(self):
        try:
            institutions = []
            institution_ldap_data = self._get_all_institution_ldap_data_regardless_of_user_membership()
            for this_institution_ldap_data in institution_ldap_data:
                institution = {}
                countries = list(map(self._decode_byte_string, this_institution_ldap_data.get("memberUid", [])))
                if not countries:
                    logging.warning(
                        f"institution {self._decode_byte_string(this_institution_ldap_data['description'][0])} has no specified countries"
                    )
                else:
                    institution["countries"] = countries
                institution["key"] = self._decode_byte_string(this_institution_ldap_data["cn"][0])
                institution["name"] = self._decode_byte_string(this_institution_ldap_data["description"][0])
                institutions.append(institution)
        except KeyError as err:
            error_message = f"Retrieving institution LDAP data: {err}"
            logging.error(error_message)
            raise LdapDataError(error_message)

        return institutions

    def get_all_institution_keys_regardless_of_user_membership(self):
        return self._get_all_institution_attribute_values_regardless_of_user_membership(self.config["inst_id_attr"])

    def get_all_institution_names_regardless_of_user_membership(self):
        return self._get_all_institution_attribute_values_regardless_of_user_membership(self.config["inst_name_attr"])

    def _get_all_institution_attribute_values_regardless_of_user_membership(self, attribute):
        institution_ldap_data = self._get_all_institution_ldap_data_regardless_of_user_membership()
        return [
            self._decode_byte_string(this_institution_ldap_data[attribute][0])
            for this_institution_ldap_data in institution_ldap_data
        ]

    def _get_all_institution_ldap_data_regardless_of_user_membership(self):
        if self.ldap_filter_string_institutions is None:
            self.ldap_filter_string_institutions = (
                # fmt: off
                "(&"
                f"(objectClass={self.config['institution_group_obj']})"
                "(objectClass=top)"
                "(description=*)"
                ")"
                # fmt: on
            )
        institution_ldap_tuples = self.ldap_search(self.ldap_filter_string_institutions)

        if institution_ldap_tuples is None or len(institution_ldap_tuples) == 0:
            logging.error(f"LDAP search: No ({institution_ldap_tuples}) institutions found")
            raise LdapDataError("No institutions were found")

        institution_data = [institution_ldap_tuple[1] for institution_ldap_tuple in institution_ldap_tuples]
        logging.debug(f"institutions retrieved from LDAP: {institution_data}")

        return institution_data

    def _decode_byte_string(self, byte_string):
        return byte_string.decode(UTF_8)
