FROM python:3.12.3-slim

WORKDIR /analysis

COPY . /analysis

EXPOSE 8005

RUN pip install -r requirements.txt

CMD ["uvicorn","src.main:app","--port=8005","--log-level=info","--host=0.0.0.0" ]
