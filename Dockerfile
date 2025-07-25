FROM python:3.13-alpine

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync

RUN pip uninstall uv -y
RUN pip cache purge

COPY ./pymuse ./pymuse
COPY config.yml ./

COPY ./alembic ./alembic
COPY alembic.ini ./

RUN mkdir database temp

CMD [".venv/bin/python3", "pymuse/main.py"]
