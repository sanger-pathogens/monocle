# 0.9.0 is from 2019-11-05, the latest version-numbered tag available
# stable is from 2021-02-19, but unfortunately there is version-numbered tag, so
# the locally cached copy of the image was tagged uniquely as stable_20220412Z1015
FROM  gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/osixia/phpldapadmin:stable_20220412Z1015

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

# cache bust to update quickly the image build time
# pass a new value as CACHE_BUST, e.g. with `--build-arg "CACHE_BUST=$(date)"`
ARG      CACHE_BUST
RUN      echo "$CACHE_BUST" > /dev/null

RUN   echo "$ADDITIONAL_CONFIG" >> "$PHPLDAPADMIN_CONFIG_FILE"

CMD /container/tool/run
