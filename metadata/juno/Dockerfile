FROM  gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/python:3.7

WORKDIR /app

# install dependencies
COPY Pipfile /app/
RUN pip install pipenv \
    && pipenv install --system --skip-lock

# add rest of code
COPY . /app

CMD ["gunicorn", "-w 2", "-b :80", "metadata.wsgi"]
