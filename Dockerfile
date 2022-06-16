FROM python:3.9.12-slim

WORKDIR /analysis

COPY . /analysis

EXPOSE 8005

RUN pip install -r requirements.txt

CMD ["uvicorn","src.main:app","--reload","--port=8005","--host=0.0.0.0" ]


