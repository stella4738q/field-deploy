FROM python:3.10-slim
ENV INSTALL_PATH /app

WORKDIR ${INSTALL_PATH}
COPY . .

RUN apt-get update \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install --default-timeout=2000 -r requirements.txt --no-cache-dir

CMD ["python", "main.py"]