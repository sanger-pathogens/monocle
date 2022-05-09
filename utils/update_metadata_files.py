#!/usr/bin/env python3

import copy
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
Todo:
dashboard API openapi.yml file (OpenAPI spec. for endpoints)
metadata API openapi.yml file (OpenAPI spec. for endpoints)
tests
"""


class UpdateMetadataFiles:
    def __init__(self):
        self.indent = "    "
        self.root_path = f"{os.path.dirname(__file__)}/.."
        self.map_config_dict = dict(metadata="metadata", in_silico_data="in silico", qc_data="qc data")
        self.config_additional_section_keys = ["spreadsheet_header_row_position", "upload_validation_enabled"]

    def black(self, filename):
        """Runs the "black" Python formatter, if installed."""
        command = f"black -q --line-length {self.gitlab_yaml['variables']['LINE_LENGTH']} {filename}"
        os.system(command)
        command = f"isort {filename}"
        os.system(command)

    def var_type_heuristic(self, data):
        """Guesses a Python variable type based of a definition in config.json."""
        if "regex" in data:
            if data["regex"] == "^[1]?[0-9]?[0-9]\\.[0-9][0-9]?$":
                return "float"
        return "str"

    def var_comment_heuristic(self, data):
        """Tries to construct a comment for a variable definition based on config.json."""
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
        output = f"from dataclasses import dataclass\n\n\n{autogeneration_note}\n\n@dataclass\nclass {class_name}:\n"
        for (k, v) in data["spreadsheet_definition"].items():
            var_type = self.var_type_heuristic(v)
            var_comment = self.var_comment_heuristic(v)
            output += f"{self.indent}{k}: {var_type}{var_comment}\n"
        with open(filename, "w") as output_file:
            _ = output_file.write(output)
        self.black(filename)

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

    def generate_sql_replacements(self, data):
        """Generates a dict to replace SQL statements in a Python file."""
        ret = {}

        columns = data["metadata"]["spreadsheet_definition"].keys()
        ret["INSERT_OR_UPDATE_SAMPLE_SQL"] = (
            "INSERT INTO api_sample (\n"
            + self.chunk_text(", ", columns, 7)
            + "\n) VALUES (\n"
            + self.chunk_text(", ", list(map(lambda c: f":{c}", columns)), 7)
            + "\n) ON DUPLICATE KEY UPDATE\n"
            + ",\n".join(list(map(lambda c: f"{self.indent}{c} = :{c}", columns)))
        )
        ret["SELECT_SAMPLES_SQL"] = (
            "SELECT\n"
            + self.chunk_text(", ", columns, 7)
            + f"\nFROM api_sample\nWHERE\n{self.indent}sanger_sample_id IN :samples"
        )
        ret["SELECT_ALL_SAMPLES_SQL"] = (
            "SELECT\n" + self.chunk_text(", ", columns, 7) + "\nFROM api_sample\nORDER BY sanger_sample_id"
        )

        columns = data["in_silico_data"]["spreadsheet_definition"].keys()
        ret["SELECT_ALL_IN_SILICO_SQL"] = (
            "SELECT\n" + self.chunk_text(", ", columns, 7) + "\nFROM in_silico\nORDER BY lane_id"
        )
        ret["INSERT_OR_UPDATE_IN_SILICO_SQL"] = (
            "INSERT INTO in_silico (\n"
            + self.chunk_text(", ", columns, 7)
            + "\n) VALUES (\n"
            + self.chunk_text(", ", list(map(lambda c: f":{c}", columns)), 7)
            + "\n) ON DUPLICATE KEY UPDATE\n"
            + ",\n".join(list(map(lambda c: f"{self.indent}{c} = :{c}", columns)))
        )
        ret["SELECT_LANES_IN_SILICO_SQL"] = (
            "SELECT\n" + self.chunk_text(", ", columns, 7) + f"\nFROM in_silico\nWHERE\n{self.indent}lane_id IN :lanes"
        )

        return ret

    def generate_code_replacements(self, data):
        """Generates a dict to replace variable assignments based on SQL in a Python file."""
        ret = {}

        columns = data["metadata"]["spreadsheet_definition"].keys()
        ret["get_samples"] = [
            r"^\s*Metadata\(.*$",
            "\n".join(list(map(lambda c: f'{c}=row["{c}"],', columns))),
        ]
        ret["update_sample_metadata"] = [
            r"^\s*self\.INSERT_OR_UPDATE_SAMPLE_SQL,\s*$",
            "\n".join(list(map(lambda c: f"{c}=metadata.{c},", columns))),
        ]
        ret["get_download_metadata"] = [
            r"^\s*Metadata\(.*$",
            "\n".join(list(map(lambda c: f'{c}=row["{c}"],', columns))),
        ]

        columns = data["in_silico_data"]["spreadsheet_definition"].keys()
        ret["update_lane_in_silico_data"] = [
            r"^\s*self\.INSERT_OR_UPDATE_IN_SILICO_SQL,\s*$",
            "\n".join(
                list(
                    map(
                        lambda c: f"{c}=self.convert_string(in_silico_data.{c}),",
                        columns,
                    )
                )
            ),
        ]
        ret["get_download_in_silico_data"] = [
            r"^\s*InSilicoData\(\s*$",
            "\n".join(list(map(lambda c: f'{c}=row["{c}"],', columns))),
        ]

        return ret

    def get_autogeneration_note(self, area):
        """Creates a code comment to warn about auto-generated code."""
        return f"# THIS {area} IS AUTO-GENERATED BY utils/update_metadata_files.py, DO NOT EDIT MANUALLY!\n"

    def update_monocle_database_service_impl(self, data, filename):
        """Updates the monocle_database_service_impl.py file."""
        autogeneration_note = self.get_autogeneration_note("CODE SECTION")
        sql_replacements = self.generate_sql_replacements(data)
        code_replacements = self.generate_code_replacements(data)

        # Replace existing code
        with open(filename, "r") as in_file:
            lines = in_file.readlines()
        new_code = ""
        current_method = ""
        p_current_method = re.compile(r"^\s*def ([^ \()]+).*$")
        while len(lines) > 0:
            line = lines.pop(0)
            out = line

            # SQL replacements
            for (replacement_key, replacement_text) in sql_replacements.items():
                p = re.compile(r"^\s*" + replacement_key + r"\s*=\s*text\s*\($")
                if p.match(line):
                    out += f"{self.indent*2}{autogeneration_note}"
                    out += f'{self.indent*2}""" \\\n' + self.pad(replacement_text, 3) + f'\n{self.indent*2}"""\n'
                    self.skip_lines_until(r"^.*\"\"\".*$", lines)  # Quote open
                    self.skip_lines_until(r"^.*\"\"\".*$", lines)  # Quote close
                    break
            if line == out:
                # Code replacements
                m = p_current_method.match(line)
                if m:
                    current_method = m.group(1)
                if current_method in code_replacements:
                    v = code_replacements[current_method]
                    p = re.compile(v[0])
                    if p.match(line):
                        out += f"{self.indent*5}{autogeneration_note}"
                        out += self.pad(v[1], 5) + "\n"
                        out += self.skip_lines_until(r"^\s*\)\s*$", lines)
            new_code += out
        with open(filename, "w") as output_file:
            _ = output_file.write(new_code)
        self.black(filename)

    def update_database_definition(self, data, filename):
        """Updates an SQL table definition file.

        NOTE: This could use some additional metadata in config.json, eg unusual MySQL types, ranges etc
        """
        with open(filename, "r") as in_file:
            lines = in_file.readlines()

        new_code = ""
        p = re.compile(r"^\s*CREATE TABLE .*$")
        while len(lines) > 0:
            line = lines.pop(0)
            out = line
            if p.match(line):
                out += "  " + self.get_autogeneration_note("TABLE DEFINITION")
                for (k, v) in data["spreadsheet_definition"].items():
                    row = f"  `{k}` "
                    if self.var_type_heuristic(v) == "float":
                        row += "DECIMAL(5,2) UNSIGNED"
                    elif "max_length" in v:
                        row += f"VARCHAR({v['max_length']})"
                    else:
                        row += "int(11)"
                    if "mandatory" in v and v["mandatory"]:
                        row += " NOT NULL"
                    else:
                        row += " DEFAULT NULL"
                    row += ",\n"
                    out += row
                out += "  # END OF AUTO_GENERATED SECTION\n"
                out += self.skip_lines_until(r"^.*PRIMARY KEY.*$", lines)
            new_code += out

        with open(filename, "w") as output_file:
            _ = output_file.write(new_code)

    def update_all(self):
        """Runs updates on all metadata files."""
        metadata_path = f"{self.root_path}/metadata"
        with open(f"{self.root_path}/.gitlab-ci.yml", "r") as file:
            self.gitlab_yaml = yaml.safe_load(file)
        self.black(__file__)  # Self-format
        for entry in os.scandir(metadata_path):
            if entry.is_dir():
                config_path = f"{metadata_path}/{entry.name}/config.json"
                if os.path.exists(config_path):
                    with open(config_path) as config_file:
                        data = json.load(config_file)
                        self.update_monocle_database_service_impl(
                            data,
                            f"{metadata_path}/{entry.name}/metadata/api/database/monocle_database_service_impl.py",
                        )
                        for (k, class_name) in [
                            ("metadata", "Metadata"),
                            ("in_silico_data", "InSilicoData"),
                            ("qc_data", "QCData"),
                        ]:
                            self.generate_dataclass_file(
                                data[k],
                                class_name,
                                f"{metadata_path}/{entry.name}/metadata/api/model/{k}.py",
                            )
                        for (k, filename) in [
                            ("metadata", "api_sample.sql"),
                            ("in_silico_data", "in_silico.sql"),
                            ("qc_data", "qc_data.sql"),
                        ]:
                            self.update_database_definition(data[k], f"{self.root_path}/database/tables/{filename}")

    def write_field_attributes_file(self):
        """Generated the file_attributes.json file for dash-api."""
        field_attributes_file = f"{self.root_path}/dash-api/juno/field_attributes.json"
        field_attributes = copy.deepcopy(self.config)
        for _, kmc in self.map_config_dict.items():
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

    def update_from_main_config(self):
        """Updates metadata/*/config./json files, as well as dash-api/juno/field_attributes.json.
        Required first step for further updates.
        """
        main_config_file = f"{self.root_path}/config/main_config.json"
        with open(main_config_file) as config_file:
            self.config = json.load(config_file)

        self.write_field_attributes_file()

        metadata_path = f"{self.root_path}/metadata"
        for entry in os.scandir(metadata_path):
            if entry.is_dir():
                config_path = f"{metadata_path}/{entry.name}/config.json"
                if os.path.exists(config_path):
                    self.update_config_json(config_path)


if __name__ == "__main__":
    umf = UpdateMetadataFiles()
    umf.update_from_main_config()
    umf.update_all()
