FROM  gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/python:3.7

WORKDIR /app

RUN      apt-get update -qq
RUN      apt-get install -y libldap2-dev libsasl2-dev

# install dependencies
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv \
    && pipenv install --system --ignore-pipfile

# add rest of code
COPY . /app

EXPOSE   80
CMD ["gunicorn", "-w 2", "-b :80", "dash.wsgi"]
