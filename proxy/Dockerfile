FROM gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/nginx:1.21.6

COPY public /usr/share/nginx/html

# Since 1.17.0, both alpine- and debian-based images variants use the same user and group ids to drop the privileges for worker processes:
# 
#   $ id
#   uid=101(nginx) gid=101(nginx) groups=101(nginx)

RUN chown -R nginx:nginx /usr/share/nginx/html/*
RUN chmod -R 0755 /usr/share/nginx/html/*

# cache bust to update quickly the image build time
# pass a new value as CACHE_BUST, e.g. with `--build-arg "CACHE_BUST=$(date)"`
ARG      CACHE_BUST
RUN      echo "$CACHE_BUST" > /dev/null
