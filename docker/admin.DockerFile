FROM python:3.10-slim as builder

RUN apt-get update --quiet && apt-get install build-essential --yes --no-install-recommends

WORKDIR /home/web_admin

RUN groupadd -r web_admin && useradd -d /home/web_admin -r -g web_admin web_admin \
    && chown web_admin:web_admin -R /home/web_admin

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "/home/web_admin"

COPY ./src/admin_panel/requirements.txt ./

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY ./src/admin_panel/ admin_panel/
COPY ./src/common/ common/
COPY ./src/alembic.ini .

USER web_admin

CMD ["python", "admin_panel/app.py"]
