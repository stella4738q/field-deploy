FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install --default-timeout=2000 -r requirements.txt --no-cache-dir

CMD ["modbus-proxy", "-c", "modbus_proxy.yaml"]
