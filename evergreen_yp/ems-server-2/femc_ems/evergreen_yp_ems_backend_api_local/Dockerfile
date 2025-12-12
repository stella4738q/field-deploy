FROM python:3.10-slim
ENV INSTALL_PATH /app

WORKDIR ${INSTALL_PATH}
COPY . .

RUN apt-get update \
    && apt-get install libreoffice --no-install-recommends -y \
#     && apt-get install default-jre fonts-arphic-ukai python3-uno libmagic1 -y \
#     && apt-get install gcc libsasl2-dev python3-dev libldap2-dev libssl-dev vim net-tools -y \
    && apt-get install vim fonts-arphic-ukai net-tools -y \
    && pip install --upgrade pip \
    && pip install --default-timeout=2000 -r requirements.txt --no-cache-dir

EXPOSE 5000
CMD ["python", "apps/dashboard/__init__.py"]
