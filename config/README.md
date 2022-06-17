# Configuration
The central configuration file is `config/main_config.json`. If you change any
configuration in there, run `config/update_config_files.py`. This will alter the following files:
- `database/tables/api_sample.sql`
- `database/tables/in_silico.sql`
- `database/tables/qc_data.sql`
- `database/tables/gps_sample.sql`
- `database/tables/gps_in_silico.sql`
- `database/tables/gps_qc_data.sql`
- `metadata/common/metadata/tests/test_data.py`
- For each of PROJECT in ['juno','gps']:
  - `config.json`
  - `metadata/PROJECT/metadata/api/model/metadata.py` (complete replacement)
  - `metadata/PROJECT/metadata/api/model/in_silico_data.py` (complete replacement)
  - `metadata/PROJECT/metadata/api/model/qc_data.py` (complete replacement)
  - `dash-api/dash/interface/PROJECT_objects.yml`
  - `dash-api/PROJECT_field_attributes.json` (as a subset of main_config)

# main_config.json
The main_config.json file consists of
- `config`, this is mapped into the `UpdateMetadataFiles` class automatically
- `metadata`, `in silico`, and `qc data` represent different database tables, and their rules (validity patterns, field type etc)
- each of `metadata`, `in silico`, and `qc data` require a subsection for each project (currently, `juno` and `gps`)
