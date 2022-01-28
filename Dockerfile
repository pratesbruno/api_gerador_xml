FROM python:3.9.10-buster

COPY api /api
COPY gerador_xml /gerador_xml
COPY requirements.txt /requirements.txt
COPY gerador-xml-dfffc2276183.json /credentials.json

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD uvicorn api.fast:app --host 0.0.0.0 --port $PORT