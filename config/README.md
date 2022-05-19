# Configuration
The central configuration file is `config/main_config.json`. If you change any
configuration in there, run `config/update_config_files.py`. This will alter the following files:
- `database/tables/api_sample.sql`
- `database/tables/in_silico.sql`
- `database/tables/qc_data.sql`
- `dash-api/juno/field_attributes.json` (as a subset of main_config)
- `dash-api/juno/dash/interface/openapi.yml`
- For each directory in `metadata`:
  - `config.json`
  - `metadata/api/database/model/metadata.py` (complete replacement)
  - `metadata/api/database/model/in_silico_data.py` (complete replacement)
  - `metadata/api/database/model/qc_data.py` (complete replacement)
  - `metadata/tests/test_data.py`
  - `metadata/interface/openapi.yml`

# main_config.json
The main_config.json file consists of
- `config`, this is mapped into the `UpdateMetadataFiles` class automatically
- `metadata`, `in silico`, and `qc data` represent different database tables, and their rules (validity patterns, field type etc)