
FROM python:3.10

WORKDIR /spreadsheets-app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "spreadsheets_app.app"]