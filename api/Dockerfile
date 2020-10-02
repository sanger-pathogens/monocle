FROM python:3.7

WORKDIR /app

# install several mysql related deps
RUN apt-get upgrade -y
RUN apt-get install -y default-libmysqlclient-dev

# install (separation of COPY to help cache dependencies)
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv \
    && pipenv install --system --ignore-pipfile

# add rest of code
COPY . /app

CMD ["gunicorn", "-w 3", "-b :80", "juno.wsgi"]

# TODO: Consider switching from wsgi to asgi as follows:
# gunicorn example:app -w 4 -k uvicorn.workers.UvicornWorker
