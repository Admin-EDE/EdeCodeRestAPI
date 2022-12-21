FROM ubuntu:22.04
LABEL maintainer="Centro de Innovación (Mineduc) <admin@ede.mineduc.cl>"
RUN apt-get update

RUN apt search python3
RUN apt-get -y install python3 --fix-missing
RUN apt-get -y install python3-pip --fix-missing
#dependencies for sqlcipher
RUN apt-get install sqlcipher libsqlcipher0 libsqlcipher-dev -q -y --fix-missing
RUN apt-get install git -q -y --fix-missing

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
ENV PORT 8080
#ENV DEBUG True

ENV GIT_PYTHON_REFRESH=quiet

# Copy local code to the container image.
#RUN mkdir /app
#ENV APP_HOME /app
#WORKDIR $APP_HOME
#COPY . .
ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt