FROM     python:3.7

WORKDIR  /dash

RUN      pip install dash==1.19.0      \
                     dash-daq==0.5.0   \
                     flask==1.1.2      \
                     gunicorn==20.0.4  \
                     pandas

COPY     . /dash


EXPOSE   80
CMD      ["gunicorn", "-w 3", "-b :80", "wsgi:server"]
