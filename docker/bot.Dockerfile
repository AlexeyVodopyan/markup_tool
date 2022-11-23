FROM python:3.10-slim as builder

RUN apt-get update --quiet && apt-get install build-essential --yes --no-install-recommends

WORKDIR /home/bot

RUN groupadd -r bot && useradd -d /home/bot -r -g bot bot \
    && chown bot:bot -R /home/bot

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "/home/bot"

COPY ./src/telegram_bot/requirements.txt ./

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY ./src/telegram_bot/ telegram_bot/
COPY ./src/common/ common/
COPY ./src/alembic.ini .

USER bot

CMD ["python", "telegram_bot/bot.py"]
