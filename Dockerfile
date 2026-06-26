FROM python:3.10-slim-buster

RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Render Web Services require binding to a PORT
EXPOSE 8080

CMD ["python3", "main.py"]
