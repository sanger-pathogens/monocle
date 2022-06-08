#!/usr/bin/env python3

import copy
import hashlib
import json
import os
import re

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
        autogeneration_note = self.get_autogeneration_note("FILE")
        output = f"from dataclasses import dataclass\n\n{autogeneration_note}\n\n@dataclass\nclass {class_name}:\n"
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
        with open(filename, "r") as in_file:
            lines = in_file.readlines()
        original_lines = list(map(lambda l: l.strip(), lines))

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
            print(f"THE FOLLOWING CHANGES NEED TO BE PERFORMED IN THE LIVE MySQL DB for {filename}:")
            print("\n".join(mysql_changes))
            print("")

        with open(filename, "w") as output_file:
            _ = output_file.write(new_code)

    def update_test_data(self, data, test_data_file_path):
        """Updates the test_data.py file if required.
        Uses as much of the existing test values as possible.
        """
        if not os.path.exists(test_data_file_path):
            print(f"Skipping non-existing file {test_data_file_path}")
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
            for k in key_value_pairs:
                if k not in current_group_data["spreadsheet_definition"]:
                    print(f"Removing {k} from test data in {test_data_file_path}")
                    key_value_pairs.pop(k)
            # Add new fields
            for k in current_group_data["spreadsheet_definition"]:
                if k not in key_value_pairs:
                    print(f"Adding {k} to test data in {test_data_file_path}")
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

    def update_yml_field_patterns(self, y, data):
        """Updates YAML field patterns."""
        for (yk, jk) in self.yml_field_patterns:
            json_keys = list(data[jk]["spreadsheet_definition"].keys())
            y["components"]["schemas"][yk]["pattern"] = "^" + "|".join(json_keys) + "$"

    def update_yml_field_list(self, y, j):
        y["properties"].clear()
        y["required"].clear()
        json_keys = list(j.keys())
        for k in json_keys:
            y["properties"][k] = {"$ref": "#/components/schemas/DownloadField"}
        y["required"] = json_keys

    def update_shared_yml(self, data, file_path):
        if not os.path.exists(file_path):
            print(f"Skipping: {file_path} does not exist")
            return
        with open(file_path) as file:
            y = yaml.safe_load(file)
        self.update_yml_field_patterns(y, data)
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

    def update_dash_yml(self, data, file_path):
        """Updates the dash openapi.yml file with various properties.
        TODO: default/required fields need to be annotated in upstream config and set here
        """
        y = self.update_shared_yml(data, file_path)
        for entry in self.yml2json:
            this_schema = y["components"]["schemas"][entry["Schema name"]]
            field_definitions = data[entry["Property name"]]["spreadsheet_definition"]
            self.update_yml_field_list(this_schema, field_definitions)
        self.output_shared_yml(y, file_path)

    def update_main_yml(self, data, file_path):
        """Updates the dash openapi.yml file with various properties.
        TODO: default/required fields need to be annotated in upstream config and set here
        """
        y = self.update_shared_yml(data, file_path)
        for entry in self.yml2json:
            this_schema = y["components"]["schemas"][entry["Schema name"]]
            field_definitions = data[entry["Property name"]]["spreadsheet_definition"]
            items_list = this_schema["properties"][entry["API config section"]]["items"]
            self.update_yml_field_list(items_list, field_definitions)
        self.output_shared_yml(y, file_path)

    def abs_path(self, relative_path):
        return f"{self.root_path}/{relative_path}"

    def update_all(self, main_config_file):
        """Runs updates on all metadata files."""
        self.update_from_main_config(self.abs_path(main_config_file))
        for files in self.files.values():
            config_path = self.abs_path(files["config_file"])
            if os.path.exists(config_path):
                with open(config_path) as config_file:
                    data = json.load(config_file)
                for entry in files["API model"]:
                    table_data = data[entry["data key"]]
                    self.generate_dataclass_file(
                        table_data,
                        entry["class name"],
                        self.abs_path(entry["model file name"]),
                    )
                    self.update_database_definition(table_data, self.abs_path(entry["SQL file name"]))
                self.update_metadata_tests(data, self.abs_path(files["test directory"]))
                self.update_dash_yml(data, self.abs_path(files["dash YAML file"]))
                self.update_main_yml(data, self.abs_path(files["API YAML file"]))

    def write_field_attributes_file(self):
        """Generated the file_attributes.json file for dash-api."""
        for files in self.files.values():
            field_attributes_file = self.abs_path(files["field attributes"])
            old_md5 = hashlib.md5(open(field_attributes_file, "rb").read()).hexdigest()
            field_attributes = copy.deepcopy(self.config)
            field_attributes.pop("config")
            for kmc in self.map_config_dict.values():
                for k in self.config_additional_section_keys:
                    if k in field_attributes[kmc]:
                        field_attributes[kmc].pop(k)
                for category in field_attributes[kmc]["categories"]:
                    for fields in category["fields"]:
                        if "db" in fields:
                            fields.pop("db")
            json_object = json.dumps(field_attributes, indent=3)
            with open(field_attributes_file, "w") as out_file:
                out_file.write(json_object)
            new_md5 = hashlib.md5(open(field_attributes_file, "rb").read()).hexdigest()
            if old_md5 != new_md5:
                print(
                    f"ATTENTION: File {field_attributes_file} has changed, you might have to update LOCAL_STORAGE_KEY_COLUMNS_STATE in frontend/src/lib/constants.js"
                )

    def update_config_section(self, c, mc):
        """Updates a section of config data (c) from main config (mc)."""
        for k in self.config_additional_section_keys:
            if k in mc:
                c[k] = mc[k]

        sd = {}  # spreadsheet_definition
        for category in mc["categories"]:
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
                    sd[id] = d
        c["spreadsheet_definition"] = sd
        return c

    def update_config_json(self, config_path):
        """Updates a config.json file based on main_config.json"""
        with open(config_path) as config_file:
            config = json.load(config_file)

        for kc, kmc in self.map_config_dict.items():
            config[kc] = self.update_config_section(config[kc], self.config[kmc])

        json_object = json.dumps(config, indent=3)
        with open(config_path, "w") as out_file:
            out_file.write(json_object)

    def update_from_main_config(self, main_config_file):
        """Updates metadata/*/config./json files, as well as dash-api/juno/field_attributes.json.
        Required first step for further updates.
        """
        with open(main_config_file) as config_file:
            self.config = json.load(config_file)

        for k, v in self.config["config"].items():
            self.__dict__[k] = v

        self.write_field_attributes_file()

        for files in self.files.values():
            config_path = self.abs_path(files["config_file"])
            if os.path.exists(config_path):
                self.update_config_json(config_path)


if __name__ == "__main__":
    umf = UpdateMetadataFiles()
    umf.update_all("config/main_config.json")
