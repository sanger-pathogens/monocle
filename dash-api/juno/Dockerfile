FROM     gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/python:3.7

WORKDIR  /app

RUN      apt-get update -qq
RUN      apt-get install -y libldap2-dev libsasl2-dev

RUN      pip install flask==1.1.2                     \
                  flask-injector==0.12.0              \
                  flask-cors==3.0.10                  \
                  gunicorn==20.1.0                    \
                  python-ldap==3.3.1                  \
                  PyYAML==5.3.1                       \
                  'connexion[swagger-ui]'             \
                  Werkzeug==1.0.1

COPY     . /app

EXPOSE   80
CMD      ["gunicorn", "-w 1", "-b :80", "dash.wsgi"]