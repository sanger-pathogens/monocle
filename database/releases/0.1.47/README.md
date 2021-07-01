# v0.1.47 database release

## Release steps

* Back up the api_sample, api_institution and api_affiliation tables to file if required.
* Apply the pre-release-steps.sql to the correct database from a sql client.
* Apply the table_changes_prod.sql from a sql client (only required for prod, dev was done with Django [now retired]).
* Apply the post-release-steps.sql to the correct database from a sql client.
* Then perform the code release.
* Start the applications.
