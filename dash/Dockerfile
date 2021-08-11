FROM     gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/python:3.7

WORKDIR  /dash

RUN      apt-get update -qq
RUN      apt-get install -y   libldap2-dev \
                              libsasl2-dev

RUN      pip install dash==1.19.0                        \
                     dash-daq==0.5.0                     \
                     flask==1.1.2                        \
                     flask_parameter_validation==1.0.24  \
                     gunicorn==20.0.4                    \
                     mysqlclient==2.0.1                  \
                     pandas==1.2.2                       \
                     python-ldap==3.3.1                  \
                     PyYAML==5.3.1                       \
                     SQLAlchemy==1.3.23

COPY     . /dash

EXPOSE   80
CMD      ["gunicorn", "-w 3", "-b :80", "wsgi:server"]
