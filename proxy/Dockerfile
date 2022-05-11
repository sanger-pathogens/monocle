FROM gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/nginx:1.21.6-with-headers-more-module
COPY public /usr/share/nginx/html

# Since 1.17.0, both alpine- and debian-based images variants use the same user and group ids to drop the privileges for worker processes:
# 
#   $ id
#   uid=101(nginx) gid=101(nginx) groups=101(nginx)

RUN chown -R nginx:nginx /usr/share/nginx/html/*
RUN chmod -R 0755 /usr/share/nginx/html/*
