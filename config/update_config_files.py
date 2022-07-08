#!/usr/bin/env python3

import argparse
import copy
import hashlib
import json
import logging
import os
import re
from sys import argv

import yaml

"""
Done:
database schema
metadata API SQL queries also have lists of db column names.
metadata API config.json file (used with Pandas for spreadsheet validation and loading; also referred to by metadata download code)
metadata API metadata data model
metadata API in silico data model
metadata API QC data model
tests
dashboard API openapi.yml file (OpenAPI spec. for endpoints)
metadata API openapi.yml file (OpenAPI spec. for endpoints)
Ignore:
monocle_database_service_noop_impl.py (?)
"""


class UpdateMetadataFiles:
    def __init__(self):
        self.indent = "    "
        self.root_path = f"{os.path.dirname(__file__)}/.."

    def var_comment_heuristic(self, data):
        """Tries to construct a comment for a variable definition based on config.json."""
        if "var_comment" in data:  # Manual override
            if data["var_comment"] == "":
                return ""
            return "  # " + data["var_comment"]
        comments = []
        if "mandatory" in data and data["mandatory"]:
            comments.append("mandatory")
        else:
            comments.append("optional")
        if "regex_validation_message" in data:
            comments.append(data["regex_validation_message"])
        if len(comments) == 0:
            return ""
        return "  # " + "; ".join(comments)

    def generate_dataclass_file(self, data, class_name, filename):
        """Generated a Python dataclass file."""
        logging.info("Updating dataclass file {}".format(filename))
        autogeneration_note = self.get_autogeneration_note("FILE")
        output = f"from dataclasses import dataclass\n\n{autogeneration_note}\n\n@dataclass\nclass {class_name}:\n"
        logging.debug("dataclass variables: {}".format(list(data["spreadsheet_definition"])))
        for (k, v) in data["spreadsheet_definition"].items():
            var_type = v["var_type"] if "var_type" in v else "str"
            var_comment = self.var_comment_heuristic(v)
            output += f"{self.indent}{k}: {var_type}{var_comment}\n"
        with open(filename, "w") as output_file:
            _ = output_file.write(output)

    def pad(self, text, num):
        """Left-pads every line in a multi-line string with the given number of indents."""
        return self.indent * num + text.replace("\n", "\n" + self.indent * num)

    def chunk_text(self, sep, list, max):
        """Turns a list into a multi-line string with a given maximum of list items per line."""
        ret = self.indent
        for num, t in enumerate(list):
            if num > 0:
                ret += sep
                if num % max == 0 and num + 1 < len(list):
                    ret = ret.rstrip()
                    ret += "\n" + self.indent
            ret += t
        return ret

    def skip_lines_until(self, pattern, lines):
        """Skips through a list of strings until it finds one matching a given pattern.
        Removes all lines from the list until then, including the one that matches the pattern.
        Returns the line that matches the pattern.
        """
        p = re.compile(pattern)
        while len(lines) > 0:
            line = lines.pop(0)
            if p.match(line):
                return line
        return ""

    def get_autogeneration_note(self, area):
        """Creates a code comment to warn about auto-generated code."""
        base_path = os.path.abspath(os.path.basename(__file__))
        root_path = os.path.abspath(self.root_path)
        script_path = base_path[len(root_path) + 1 :]
        return f"# THIS {area} IS AUTO-GENERATED BY {script_path}, DO NOT EDIT MANUALLY!\n"

    def update_database_definition(self, data, filename):
        """Updates an SQL table definition file.

        NOTE: This could use some additional metadata in config.json, eg unusual MySQL types, ranges etc
        """
        logging.info("Updating database definition file {}".format(filename))
        with open(filename, "r") as in_file:
            lines = in_file.readlines()
        original_lines = list(map(lambda l: l.strip(), lines))

        logging.debug("Database fields: {}".format(list(data["spreadsheet_definition"])))
        new_code = ""
        p = re.compile(r"^\s*CREATE TABLE .*$")
        while len(lines) > 0:
            line = lines.pop(0)
            out = line
            if p.match(line):
                out += "  " + self.get_autogeneration_note("TABLE DEFINITION")
                for (k, v) in data["spreadsheet_definition"].items():
                    out += f"  `{k}` {v['mysql_type']},\n"
                out += "  # END OF AUTO_GENERATED SECTION\n"
                out += self.skip_lines_until(r"^.*PRIMARY KEY.*$", lines)
            new_code += out

        # Check for differences
        new_lines = list(map(lambda l: l.strip(), new_code.split("\n")))
        mysql_changes = []
        for line in original_lines:
            if line not in new_lines:
                mysql_changes.append(f"Removed: {line}")
        for line in new_lines:
            if line not in original_lines:
                mysql_changes.append(f"Added or updated: {line}")
        if len(mysql_changes) > 0:
            logging.critical(f"THE FOLLOWING CHANGES NEED TO BE PERFORMED IN THE LIVE MySQL DB for {filename}:")
            logging.critical("\n".join(mysql_changes))
            logging.critical("")

        with open(filename, "w") as output_file:
            _ = output_file.write(new_code)

    def update_test_data(self, data, test_data_file_path):
        """Updates the test_data.py file if required.
        Uses as much of the existing test values as possible.
        """
        logging.info("Updating unit test data file {}".format(test_data_file_path))
        if not os.path.exists(test_data_file_path):
            logging.warning(f"Skipping non-existing file {test_data_file_path}")
            return
        with open(test_data_file_path) as test_data_file:
            lines = test_data_file.readlines()
        output = ""
        pattern_dict = re.compile(r"^(TEST_\S+_DICT)\s*=\s*dict\s*\(\S*$")
        pattern_key_value = re.compile(r"^\s*(\S+?)\s*=.*\s*\"(.*?)\"\s*,{0,1}\s*$")
        pattern_end_of_definition = re.compile(r"^\s*\)\S*$")
        while len(lines) > 0:
            line = lines.pop(0)
            pattern_dict_match = pattern_dict.match(line)
            if not pattern_dict_match:
                output += line
                continue
            variable_name = pattern_dict_match.group(1)
            key_value_pairs = {}
            while len(lines) > 0:
                row = lines.pop(0)
                n = pattern_key_value.match(row)
                if n:
                    key_value_pairs[n.group(1)] = n.group(2)
                if pattern_end_of_definition.match(row):
                    break
            for data_group, variable_names in self.test_data_variable_names.items():
                if variable_name in variable_names:
                    current_group_data = data[data_group]
            # Remove obsolete fields
            for k in list(key_value_pairs):
                if k not in current_group_data["spreadsheet_definition"]:
                    logging.warning(f"Removing {k} from test data in {test_data_file_path}")
                    key_value_pairs.pop(k)
            # Add new fields
            for k in current_group_data["spreadsheet_definition"]:
                if k not in key_value_pairs:
                    logging.warning(f"Adding {k} to test data in {test_data_file_path}")
                    key_value_pairs[k] = str(len(key_value_pairs) + 1)
            output += line
            for k, v in key_value_pairs.items():
                output += f'{self.indent}{k}="{v}",\n'
            output += ")\n"
        with open(test_data_file_path, "w") as output_file:
            _ = output_file.write(output)

    def update_metadata_tests(self, data, tests_path):
        """Updates tests that use data from config files."""
        self.update_test_data(data, f"{tests_path}/test_data.py")

    def update_yml_field_patterns(self, y, data, yml_field_patterns):
        """Updates YAML field patterns."""
        for (yk, jk) in yml_field_patterns:
            json_keys = list(data[jk]["spreadsheet_definition"].keys())
            y["components"]["schemas"][yk]["pattern"] = "^" + "|".join(json_keys) + "$"

    def update_yml_field_list(self, y, j, download_field_external_ref):
        y["properties"].clear()
        y["required"].clear()
        json_keys = list(j.keys())
        for k in json_keys:
            y["properties"][k] = {"$ref": download_field_external_ref}
        y["required"] = json_keys

    def update_shared_yml(self, data, file_path, yml_field_patterns):
        if not os.path.exists(file_path):
            logging.warning(f"Skipping: {file_path} does not exist")
            return
        with open(file_path) as file:
            y = yaml.safe_load(file)
        self.update_yml_field_patterns(y, data, yml_field_patterns)
        return y

    def output_shared_yml(self, yml, file_path):
        with open(file_path, "w") as out_file:
            for key in self.yml_key_order:
                if key not in yml:
                    continue
                tmp_yml = {}
                tmp_yml[key] = yml.pop(key)
                yaml.dump(tmp_yml, out_file)
            if len(yml) > 0:
                yaml.dump(yml, out_file)

    def update_dash_yml(self, data, file_path, project_key):
        """Updates the dash openapi.yml file with various properties.
        TODO: default/required fields need to be annotated in upstream config and set here
        """
        logging.info("Updating dashboard API OpenAPI spec. {}".format(file_path))
        yml2json = self.projects[project_key]["yml2json"]
        logging.debug(
            "Updating OpenAPI objects {}".format([this_object["Schema name dash"] for this_object in yml2json])
        )
        yml_field_patterns = list(map(lambda x: [x["Schema name dash"], x["field pattern dash"]], yml2json))
        y = self.update_shared_yml(data, file_path, yml_field_patterns)
        for entry in yml2json:
            this_schema = y["components"]["schemas"][entry["Schema name"]]
            field_definitions = data[entry["Property name"]]["spreadsheet_definition"]
            # FIXME this reference to the `DownloadField` shouldn't be hardcoded like this
            #       it could easily be changed in the openapi.yml file
            self.update_yml_field_list(
                this_schema,
                field_definitions,
                "file:///app/dash/interface/openapi.yml#/components/schemas/DownloadField",
            )
        self.output_shared_yml(y, file_path)

    def update_main_yml(self, data, file_path, project_key):
        """Updates the dash openapi.yml file with various properties.
        TODO: default/required fields need to be annotated in upstream config and set here
        """
        logging.info("Updating metadata API OpenAPI spec. {}".format(file_path))
        yml2json = self.projects[project_key]["yml2json"]
        logging.debug(
            "Updating OpenAPI objects {}".format([this_object["Schema name metadata"] for this_object in yml2json])
        )
        yml_field_patterns = list(map(lambda x: [x["Schema name metadata"], x["field pattern metadata"]], yml2json))
        y = self.update_shared_yml(data, file_path, yml_field_patterns)
        for entry in yml2json:
            this_schema = y["components"]["schemas"][entry["Data key metadata"]]
            field_definitions = data[entry["Property name"]]["spreadsheet_definition"]
            items_list = this_schema["properties"][entry["API config section"]]["items"]
            # FIXME this reference to the `DownloadField` shouldn't be hardcoded like this
            #       it could easily be changed in the openapi.yml file
            self.update_yml_field_list(
                items_list,
                field_definitions,
                "file:///app/metadata/interface/openapi.yml#/components/schemas/DownloadField",
            )
        self.output_shared_yml(y, file_path)

    def abs_path(self, relative_path):
        return f"{self.root_path}/{relative_path}"

    def update_all(self, main_config_file, metadata_tests_project):
        """Updates all metadata files."""
        main_config_path = self.abs_path(main_config_file)
        logging.info("Updating all config files from {}".format(main_config_path))
        self.update_from_main_config(main_config_path)
        # the metadata API config files (`metadata/juno/config.json` etc.) have now been updated
        # these files are now used to update other files:
        # - python data classes and unit test data for each metadta API
        # - the OpenAPI specs. (YAML files) for each metadta API
        # - the OpenAPI spec. for the dashboard
        # - the SQL files that create the monocle database tables
        for project_key, project in self.projects.items():
            logging.info("Updating data class, unit test data, SQL and OpenAPI spec. files for {}".format(project_key))
            files = project["files"]
            config_path = self.abs_path(files["config_file"])
            if os.path.exists(config_path):
                with open(config_path) as config_file:
                    data = json.load(config_file)
                    logging.debug("loaded metadata API data from {}".format(config_path))
                for entry in files["API model"]:
                    table_data = data[entry["data key"]]
                    self.generate_dataclass_file(
                        table_data,
                        entry["class name"],
                        self.abs_path(entry["model file name"]),
                    )
                    self.update_database_definition(table_data, self.abs_path(entry["SQL file name"]))
                if metadata_tests_project == project_key:
                    self.update_metadata_tests(data, self.abs_path(files["test directory"]))
                self.update_dash_yml(data, self.abs_path(files["dash YAML file"]), project_key)
                self.update_main_yml(data, self.abs_path(files["API YAML file"]), project_key)
            else:
                logging.error(
                    "Project {} config file {} could not be found.  Data class, unit test data, SQL and OpenAPI spec. files for this project have NOT been updated!".format(
                        project_key, config_path
                    )
                )

    def _remove_keys_not_wanted_in_field_attributes(self, sections, field_attributes):
        """
        The main config file has sections that list all the fields and their attributes,
        and this is almost exactly what is required in the <projectname>_field_attributes.json
        files used by the dashboard API.  There are just a few keys that aren't wanted in those
        field attribiutes files.  This function removes the unwanted keys.
        Only use this with a COPY of the main config dict, because the dict is modified!
        Pass the list of sections to be checked, and a dict with the copied
        config.
        Returns modified dict.
        """
        for this_section in sections:
            for this_key in self.config_additional_section_keys:
                if this_key in field_attributes[this_section]:
                    field_attributes[this_section].pop(this_key)
            for category in field_attributes[this_section]["categories"]:
                for fields in category["fields"]:
                    if "db" in fields:
                        fields.pop("db")
        return field_attributes

    def _copy_project_field_attributes_from_main_config(self, sections, this_project):
        """
        Makes a copy of the fields attributes for a given project, into a new dict.
        This is a copy of the project-specific config from each of a list of sections.
        e.g. if the section is "metadata" and the project is "juno" and the
        main config contains
        {  "metadata": { "juno": "all the juno stuff",
                         "gps":  "all the gps stuff
                         }
        }
        then the new dict would be
        {  "metadata":  "all the juno stuff"
        }
        Finally, calls _remove_keys_not_wanted_in_field_attributes() on the new dict.
        Pass the list of sections ("metadata", etc.) and the name of tghe project.
        Returns the new dict.
        """
        field_attributes = {}
        for this_section in sections:
            field_attributes[this_section] = copy.deepcopy(self.config[this_section][this_project])
        self._remove_keys_not_wanted_in_field_attributes(sections, field_attributes)
        return field_attributes

    def write_field_attributes_file(self):
        """Generated the file_attributes.json file for dash-api."""
        for this_project in self.projects:
            map_config_dict = self.projects[this_project]["map_config_dict"]
            files = self.projects[this_project]["files"]
            field_attributes_file = self.abs_path(files["field attributes"])
            logging.info("Updating field attributes file {}".format(field_attributes_file))
            old_md5 = hashlib.md5(open(field_attributes_file, "rb").read()).hexdigest()
            field_attributes = self._copy_project_field_attributes_from_main_config(
                map_config_dict.values(), this_project
            )
            logging.debug(
                "Copying {} (with minor tweaks) from main config file into {}".format(
                    list(field_attributes), field_attributes_file
                )
            )
            json_object = json.dumps(field_attributes, indent=3)
            with open(field_attributes_file, "w") as out_file:
                out_file.write(json_object)
            new_md5 = hashlib.md5(open(field_attributes_file, "rb").read()).hexdigest()
            if old_md5 != new_md5:
                logging.critical(
                    f"ATTENTION: File {field_attributes_file} has changed, you might have to update LOCAL_STORAGE_KEY_COLUMNS_STATE in frontend/src/lib/constants.js"
                )

    def update_config_section(self, c, mc):
        """Updates a section of config data (c) from main config (mc)."""
        for k in self.config_additional_section_keys:
            if k in mc:
                c[k] = mc[k]

        spreadsheet_definition = {}
        for category in mc["categories"]:
            logging.debug(
                "Updating category {}, fields {}".format(
                    category["name"], [each_field["name"] for each_field in category["fields"]]
                )
            )
            for field in category["fields"]:
                if "db" in field:
                    d = {}
                    if "spreadsheet heading" in field:
                        d["title"] = field["spreadsheet heading"]
                    else:
                        d["title"] = field["name"]
                    for k, v in field["db"].items():
                        d[k] = v
                    if "id" in d:
                        id = d.pop("id")
                    else:
                        id = field["name"]
                    spreadsheet_definition[id] = d
        c["spreadsheet_definition"] = spreadsheet_definition
        return c

    def update_config_json(self, config_path, project_key, map_config_dict):
        """Updates a config.json file based on main_config.json"""
        logging.info("Updating metadata API config file {}".format(config_path))
        with open(config_path) as config_file:
            config = json.load(config_file)

        for section_name_in_metadata_api_config in map_config_dict:
            section_name_in_main_config = map_config_dict[section_name_in_metadata_api_config]
            logging.debug("Updating metadata API config section {}".format(section_name_in_metadata_api_config))
            config[section_name_in_metadata_api_config] = self.update_config_section(
                config[section_name_in_metadata_api_config], self.config[section_name_in_main_config][project_key]
            )

        json_object = json.dumps(config, indent=3)
        with open(config_path, "w") as out_file:
            out_file.write(json_object)

    def update_from_main_config(self, main_config_file):
        """Updates metadata/*/config./json files, as well as dash-api/juno/field_attributes.json.
        Required first step for further updates.
        """
        with open(main_config_file) as config_file:
            self.config = json.load(config_file)
            logging.debug("Successfully loaded main config from {}".format(main_config_file))

        for k, v in self.config["config"].items():
            self.__dict__[k] = v

        self.write_field_attributes_file()

        for this_project_key in self.projects:
            this_project_config = self.projects[this_project_key]
            logging.info("Updating metadata API config file for {}".format(this_project_key))
            config_path = self.abs_path(this_project_config["files"]["config_file"])
            if os.path.exists(config_path):
                self.update_config_json(config_path, this_project_key, this_project_config["map_config_dict"])
            else:
                logging.warning(
                    "Metadata API config file {} could not be found: no update attempted".format(config_path)
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update all config files from  main config")
    parser.add_argument(
        "-L",
        "--log_level",
        help="Logging level [default: WARNING]",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
    )
    options = parser.parse_args(argv[1:])

    # logging.basicConfig(format="%(asctime)-15s %(levelname)s:  %(message)s", level=options.log_level)
    logging.basicConfig(format="%(levelname)s: %(message)s", level=options.log_level)

    # the unit tests are require test data for this project
    metadata_unit_test_data_project = "juno"

    umf = UpdateMetadataFiles()
    umf.update_all("config/main_config.json", metadata_unit_test_data_project)
