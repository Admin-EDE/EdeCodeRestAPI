#FROM edemineduc/etl
FROM ubuntu:22.04
LABEL maintainer="Centro de Innovación (Mineduc) <admin@ede.mineduc.cl>"
RUN apt update
RUN apt-get install -y cron


RUN apt-get -y install python3 --fix-missing
RUN apt-get -y install python3-pip --fix-missing
#dependencies for sqlcipher
RUN apt install sqlcipher libsqlcipher0 libsqlcipher-dev -q -y --fix-missing
RUN apt install mysql-client-8.0 -q -y --fix-missing

#RUN apt install python3-mysqldb -q -y --fix-missing

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
ENV PORT 8080
ENV DEBUG False
ENV TOMIGRATE True
#ENV OTP_SERVICE << URL del servicio del verificador de indentidad >>
#ENV X_API_KEY << API KEY del servicio del verificador de identidad >>

#Configure cron
COPY cron-test /etc/cron.d/cron-test
RUN chmod 0644 /etc/cron.d/cron-test 
RUN crontab /etc/cron.d/cron-test
# Copy local code to the container image.
RUN mkdir /app
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["sh", "entrypoint.sh"]