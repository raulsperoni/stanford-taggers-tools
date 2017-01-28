FROM java:8
MAINTAINER Raul Speroni (raulsperoni@gmail.com)

RUN mkdir stanford

WORKDIR /stanford

RUN apt-get update
RUN apt-get install -y python-pip 

RUN pip install Flask

EXPOSE 9191
EXPOSE 9190
