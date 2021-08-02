FROM  gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/python:3.7

WORKDIR /app

# install dependencies
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv coverage==5.5 \
    && pipenv install --system --ignore-pipfile

# add rest of code
COPY . /app

CMD ["gunicorn", "-w 2", "-b :80", "metadata.wsgi"]
