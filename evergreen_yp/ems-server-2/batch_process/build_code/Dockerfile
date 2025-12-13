FROM python:3.10-slim
ENV INSTALL_PATH /app

WORKDIR ${INSTALL_PATH}
COPY . .

RUN apt-get update \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get update \
    && apt-get install ffmpeg libsm6 libxext6 libaio1 -y \
    && pip install --upgrade pip \
    && pip install --default-timeout=2000 -r requirements.txt --no-cache-dir \
    && echo /app/oracle_client* > /etc/ld.so.conf.d/oracle-instantclient.conf \
    && ldconfig

CMD ["python", "main.py"]