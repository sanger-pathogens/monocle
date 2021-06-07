# v0.1.47 database release

## Release steps
* Back up the api_sample, api_institution and api_affiliation tables to file if required.
* Apply the pre-release-steps.sql to the correct database from a sql client.
* Then perform the code release. Make sure to specify the '-m yes' option to the deploy.sh script. This ensures that Django will update the table structure.
* If necessary [i.e. check], stop the applications.
* Apply the post-release-steps.sql to the correct database from a sql client.
* Start the applications
