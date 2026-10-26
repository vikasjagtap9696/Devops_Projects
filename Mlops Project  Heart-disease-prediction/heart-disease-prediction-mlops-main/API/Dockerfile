FROM python:3.12.13-slim

#Ensure that Python output is sent straight to the terminal without buffering
ENV PYTHONBUFFERED=1 

ENV PYTHONBYTECODE=1 

WORKDIR /app


COPY requirements_fasapi.txt .

RUN pip install --no-cache-dir -r requirements_fasapi.txt

COPY API/*.py ./


EXPOSE 8000

CMD ["python", "server.py"]