FROM python:3.11.7-slim

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY pyproject.toml ./
COPY poetry.lock ./

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev

COPY . .

CMD ["python", "main.py"]
