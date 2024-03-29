#FROM ubuntu:22.04
FROM edemineduc/etl:2022.2
LABEL maintainer="Centro de Innovación (Mineduc) <admin@ede.mineduc.cl>"
#RUN apt-get update


#RUN apt search python3
#RUN apt-get -y install python3 --fix-missing
#RUN apt-get -y install python3-pip --fix-missing
#dependencies for sqlcipher
#RUN apt-get install sqlcipher libsqlcipher0 libsqlcipher-dev -q -y --fix-missing
#RUN apt-get install git -q -y --fix-missing

# Allow statements and log messages to immediately appear in the Knative logs
#ENV PYTHONUNBUFFERED True
#ENV PORT 8080
#ENV DEBUG True

#ENV GIT_PYTHON_REFRESH=quiet
#ENV OTP_SERVICE << URL del servicio del verificador de indentidad >>
#ENV X_API_KEY << API KEY del servicio del verificador de identidad >>

# Copy local code to the container image.
RUN mkdir /app
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

#RUN pip install --no-cache-dir -r requirements.txt
#RUN pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["sh", "entrypoint.sh"]