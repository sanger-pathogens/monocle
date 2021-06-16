# Release steps

This is the first non-django database release.

Ensure that the version number for this folder is correct AND in the release.sql file before tagging for a release.

The manual_prod_changes.sql script must be run manually from SQL Pro or a mysql client as a pre-release step to bring 
the production database in line with dev. This is for production ONLY.

The rest of the database release can be run from the deploy.sh script along with the code release [use -m all].
The version number supplied to the deploy.sh script should match this database release version number. 
