FROM     gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/python:3.7

WORKDIR  /app

RUN      apt-get update -qq
RUN      apt-get install -y libldap2-dev libsasl2-dev

RUN      pip install flask==1.1.2                     \
                  flask-cors==3.0.10                  \
                  gunicorn==20.1.0                    \
                  python-ldap==3.3.1                  \
                  pandas==1.2.2                       \
                  PyYAML==5.3.1                       \
                  python-dateutil==2.8.1              \
                  'connexion[swagger-ui]'             \
                  mysqlclient==2.0.1                  \
                  SQLAlchemy==1.3.23                  \
                  coverage==5.5

COPY     . /app

# Temp hack until we have a final version of the dash DataSources component available
ENV      PYTHONPATH "${PYTHONPATH}:./dash/api/service"

EXPOSE   5000
CMD      ["gunicorn", "-w 2", "-b :5000", "dash.wsgi"]
