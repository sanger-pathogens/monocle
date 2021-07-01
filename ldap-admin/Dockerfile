FROM  gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/osixia/phpldapadmin:0.9.0

# the phpLDAPadmin config file
ARG   PHPLDAPADMIN_CONFIG_FILE='/container/service/phpldapadmin/assets/config/config.php'

# config to be added to the stock config file# 
# 
# login.anon_bind:
# this flag dictates if an anonymous, read only access is offered on the phpLDAPadmin log in page
# (the documentation makes it sound as if it sets the readonly status of the anonymous log in, but
# empirically, setting this to false makes the option disappear from the log in page; h/t
# https://www.surekhatech.com/blog/install-and-configure-phpldapadmin-web-client)
ARG   ADDITIONAL_CONFIG='$servers->setValue('login','anon_bind',false);'

RUN   echo "$ADDITIONAL_CONFIG" >> "$PHPLDAPADMIN_CONFIG_FILE"
