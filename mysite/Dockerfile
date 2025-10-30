FROM python:3.11


WORKDIR /app


RUN pip install --upgrade pip "poetry==2.2.1"
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root


COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]
